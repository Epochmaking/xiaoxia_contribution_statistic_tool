import time
import random
import queue
import threading
import json
from datetime import datetime
from PySide6.QtCore import Signal
from PySide6.QtCore import QThread

from controllers.crawler import MpBizCrawler, ArticleListCrawler
from controllers.content_crawler import ContentCrawler
from helpers.helpers import parse_and_crop_article_list, persist_articles_to_db
import constants as consts
from constants import MAX_RETRIES, FETCH_INTERVAL_S
from exceptions.exceptions import GetArticleContentError
from database.db import get_session
from models.article_models import Article
from llm.llm_parse import parse_creator_list_by_llm, format_creator_list_by_llm

from utils import logging

logger = logging.get_logger(__name__)

# ============ LLM Worker 数量配置 ============
LLM_PARSE_WORKERS = 3   # Stage2 解析作者清单的并发线程数
LLM_FORMAT_WORKERS = 3  # Stage3 格式化作者JSON的并发线程数


# ======================================================================
#  带计数的 FIFO 队列包装：用于精确统计 Stage1 已入队数作为浏览器完成度
# ======================================================================
class CountedQueue(queue.Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._put_count = 0
        self._lock = threading.Lock()

    def put(self, item, *args, **kwargs):
        super().put(item, *args, **kwargs)
        # None 是哨兵，不计入完成数
        if item is not None:
            with self._lock:
                self._put_count += 1

    def put_count(self):
        with self._lock:
            return self._put_count


class GetMpBizThread(QThread):
    """获取微信公众号BIZ"""
    task_over = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.to_stop = False # 停止thread标志
        self.crawler = None

    def run(self):
        """线程运行方法"""
        self.to_stop = False
        # 每次运行时创建新的爬虫实例（线程只能启动一次）
        self.crawler = MpBizCrawler()
        try:
            self.crawler.start()
            while True:
                if self.to_stop:
                    self.crawler.stop()
                    logger.info("停止获取微信公众号BIZ")
                    break
                mp_biz = self.crawler.get_mp_biz()

                if mp_biz:
                    self.to_stop = True
                    logger.info("获取微信公众号BIZ线程完成")
                    self.task_over.emit(mp_biz)
                    break
        finally:
            self.crawler.stop()

    def stop(self):
        """停止线程"""
        self.to_stop = True
        self.wait()


class GetArticleListThread(QThread):
    """获取文章列表接口"""
    task_over = Signal(list)
    flow_got = Signal(bool)
    report_index = Signal(int)

    def __init__(self):
        super().__init__()
        self.to_stop = False # 停止thread标志
        self.crawler = None
        self.target_time: datetime | None = None # 目标年月

    def run(self):
        """线程运行方法"""
        self.to_stop = False
        # 每次运行时创建新的爬虫实例（线程只能启动一次）
        self.crawler = ArticleListCrawler()
        try:
            self.crawler.start()
            while not self.to_stop:
                if self.crawler.has_cookie_template():
                    logger.info("已捕获到urlcheck接口模板，可开始分页拉取")
                    consts.TEMPLATE_FLOW = self.crawler.get_cookie_template()
                    self.flow_got.emit(True)
                    break
                time.sleep(0.5)

            # ========== 循环拉取多页 ==========
            all_articles = []
            offset = 0
            count = 10
            page_num = 1

            while count != 0:
                if self.to_stop:
                    break
                time.sleep(FETCH_INTERVAL_S)  # 控制请求频率，避免被微信拦截

                articles = None

                logger.info(f"开始获取第 {page_num} 页文章")

                for _ in range(MAX_RETRIES): # 最多尝试MAX_RETRIES次获取文章列表
                    articles = self.crawler.get_article_list(offset, count)
                    time.sleep(FETCH_INTERVAL_S+random.uniform(-FETCH_INTERVAL_S/2.0, FETCH_INTERVAL_S*2.0))
                    if articles is not None:
                        break

                if articles is None:
                    break

                logger.info(f"获取第 {page_num} 页成功，共 {len(articles)} 条")

                count = len(articles)

                assert self.target_time is not None
                offset, count = parse_and_crop_article_list(
                    articles,
                    self.target_time,
                    offset,
                    count,
                )

                all_articles.extend(articles)
                self.report_index.emit(len(all_articles))

                logger.info("本轮获取到文章: %s", articles)

                page_num += 1

            self.task_over.emit(all_articles)
        finally:
            self.crawler.stop()

    def stop(self):
        """停止线程"""
        self.to_stop = True
        self.wait()


# ======================================================================
#  流水线多线程版本的 GetArticleContentThread
#  Stage1 (单线程浏览器防反爬): 浏览器访问页面 → raw_queue (带计数)
#  Stage2 (N 并发 LLM Worker):  raw_queue 取 crop_text → parse_creator_list_by_llm → parsed_queue
#  Stage3 (M 并发 LLM Worker):  parsed_queue 取作者字符串 → format_creator_list_by_llm → 写DB
# ======================================================================
class GetArticleContentThread(QThread):
    """
    FIFO 队列 + 多 LLM Worker 流水线。
    进度条策略：
      - progress_bar 主进度 = 数据库最终写入完成数（与原UI逻辑保持完全兼容）
      - progress_msg 文本：同时展示浏览器/作者解析/格式化入库 三阶段各自完成情况，以及队列积压情况
    """
    article_list_persist_ok = Signal()
    need_user_verify = Signal()
    task_over = Signal(bool)
    report_progress = Signal(int, int, str)  # (当前进度, 总数, 详细消息)
    log_msg = Signal(str)

    def __init__(self, article_list: list[dict], to_calc_fee: bool):
        super().__init__()
        self.to_calc_fee = to_calc_fee
        self.article_list = article_list
        self.crawler: ContentCrawler | None = None

        # 全局停止标志（所有 Worker 都检查）
        self._stop_flag = threading.Event()

        # 两个 FIFO 队列（raw_queue 用带计数的版本用于精确浏览器完成度）
        self._raw_queue: CountedQueue = CountedQueue()      # Stage1 → Stage2
        self._parsed_queue: "queue.Queue" = queue.Queue()   # Stage2 → Stage3

        # 各阶段原子计数（Stage2/Stage3 完成数）
        self._count_lock = threading.Lock()
        self._parse_done = 0    # Stage2 已完成数
        self._format_done = 0   # Stage3 已完成并写入DB数（主进度）
        self._total_count = 0

        # 内部线程句柄
        self._browser_th: threading.Thread | None = None
        self._parse_workers: list[threading.Thread] = []
        self._format_workers: list[threading.Thread] = []
        self._progress_poll_th: threading.Thread | None = None

        # 异常汇总标志
        self._any_stage_failed = False

    # ------------------------------------------------------------
    #  Stage2 Worker：  crop_text → LLM → 作者清单字符串
    # ------------------------------------------------------------
    def _parse_worker(self, worker_id: int):
        logger.info(f"[Stage2 Worker-{worker_id}] 启动")
        while not self._stop_flag.is_set():
            try:
                item = self._raw_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if item is None:
                self._raw_queue.task_done()
                break
            try:
                if self._stop_flag.is_set():
                    break

                article_id = item["article_id"]
                title = item["title"]
                crop_text = item["crop_text"]
                reader_stats = item["reader_stats"]
                skip = item.get("skip", False)

                creator_list_str = ""
                if not skip and crop_text:
                    try:
                        creator_list_str = parse_creator_list_by_llm(crop_text)
                    except Exception as ex:  # pylint: disable=broad-exception-caught
                        logger.warning(
                            f"[Stage2 Worker-{worker_id}] 解析作者清单异常，文章《{title}》: {ex}"
                        )
                        creator_list_str = ""

                self._parsed_queue.put({
                    "article_id": article_id,
                    "title": title,
                    "reader_stats": reader_stats,
                    "creator_list_str": creator_list_str,
                    "skip": skip,
                    "skip_reason": item.get("skip_reason", ""),
                })
                with self._count_lock:
                    self._parse_done += 1
            finally:
                self._raw_queue.task_done()
        logger.info(f"[Stage2 Worker-{worker_id}] 退出")

    # ------------------------------------------------------------
    #  Stage3 Worker：  作者清单字符串 → LLM → JSON字典并写库
    # ------------------------------------------------------------
    def _format_worker(self, worker_id: int):
        logger.info(f"[Stage3 Worker-{worker_id}] 启动")
        while not self._stop_flag.is_set():
            try:
                item = self._parsed_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if item is None:
                self._parsed_queue.task_done()
                break
            try:
                if self._stop_flag.is_set():
                    break

                article_id = item["article_id"]
                title = item["title"]
                reader_stats = item["reader_stats"]
                creator_list_str = item["creator_list_str"]
                skip = item.get("skip", False)

                formatted_creator_dict: dict = {}
                if not skip and creator_list_str and self.to_calc_fee:
                    try:
                        formatted_creator_dict = format_creator_list_by_llm(creator_list_str)
                    except Exception as ex:  # pylint: disable=broad-exception-caught
                        logger.warning(
                            f"[Stage3 Worker-{worker_id}] 格式化作者JSON异常，文章《{title}》: {ex}"
                        )
                        formatted_creator_dict = {}

                try:
                    with get_session() as db_session:
                        target = db_session.query(Article).filter(Article.id == article_id).first()
                        if target:
                            target.view_count = reader_stats.get("view_count", 0) or 0
                            target.heart_count = reader_stats.get("heart_count", 0) or 0
                            target.like_count = reader_stats.get("like_count", 0) or 0
                            target.share_count = reader_stats.get("share_count", 0) or 0
                            target.collect_count = reader_stats.get("collect_count", 0) or 0
                            target.creators_list = creator_list_str or ""
                            target.formatted_creators_list = json.dumps(
                                formatted_creator_dict, ensure_ascii=False
                            )
                            db_session.commit()
                            logger.info(
                                f"[Stage3 Worker-{worker_id}] 更新成功 ID:{article_id}, 题目：《{title}》\n"
                                f"阅读：{target.view_count}, 爱心：{target.heart_count}, "
                                f"点赞：{target.like_count}, 分享：{target.share_count}, "
                                f"收藏：{target.collect_count}\n"
                                f"落款信息：\n{creator_list_str}\n"
                                f"格式化作者列表：\n{formatted_creator_dict}"
                            )
                        else:
                            logger.warning(
                                f"[Stage3 Worker-{worker_id}] 数据库中未找到 ID={article_id} 的文章"
                            )
                except Exception as ex:  # pylint: disable=broad-exception-caught
                    logger.error(
                        f"[Stage3 Worker-{worker_id}] 写入数据库异常，文章《{title}》: {ex}"
                    )

                with self._count_lock:
                    self._format_done += 1
            finally:
                self._parsed_queue.task_done()
        logger.info(f"[Stage3 Worker-{worker_id}] 退出")

    # ------------------------------------------------------------
    #  进度轮询线程：每 300ms 读取一次计数器，把三阶段状态同步给UI
    # ------------------------------------------------------------
    def _progress_poller(self):
        while not self._stop_flag.is_set():
            with self._count_lock:
                parse_d = self._parse_done
                fmt = self._format_done
                total = self._total_count
            browser_done = self._raw_queue.put_count()
            raw_qsize = self._raw_queue.qsize()
            parsed_qsize = self._parsed_queue.qsize()

            if total > 0:
                msg = (
                    f"文章内容 {browser_done}/{total} 已获取 · "
                    f"作者解析 {parse_d}/{total} · "
                    f"格式化入库 {fmt}/{total} | "
                    f"[待解析队列:{raw_qsize} · 待格式化队列:{parsed_qsize}]"
                )
                self.report_progress.emit(fmt, total, msg)
            if total > 0 and fmt >= total:
                break
            time.sleep(0.3)

    # ------------------------------------------------------------
    #  Stage1 浏览器执行函数（跑在子线程，保持单线程防反爬）
    # ------------------------------------------------------------
    def _run_browser_stage(self, db_articles, progress_cb, verify_cb, log_cb):
        if not self.crawler:
            return
        try:
            ok = self.crawler.crawl_pages_for_pipeline(
                article_list=db_articles,
                raw_queue=self._raw_queue,
                stop_flag=self._stop_flag,
                progress_cb=progress_cb,
                verify_cb=verify_cb,
                log_cb=log_cb,
            )
            if not ok:
                self._any_stage_failed = True
        except Exception as ex:  # pylint: disable=broad-exception-caught
            logger.error(f"浏览器阶段异常: {ex}")
            self._any_stage_failed = True
        finally:
            if self.crawler:
                try:
                    self.crawler.close_all_resource()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass

    # ------------------------------------------------------------
    #  主入口
    # ------------------------------------------------------------
    def run(self):
        """
        主入口：启动文章爬取流水线
        """
        try:
            # 1. 持久化文章列表
            persist_articles_to_db(self.article_list)
            self.article_list_persist_ok.emit()

            # 2. 从数据库读出所有 Article 对象
            with get_session() as db_session:
                db_articles: list[Article] = db_session.query(Article).all()
            if not db_articles:
                logger.error("数据库无待爬取文章")
                self.task_over.emit(True)
                return
            self._total_count = len(db_articles)
            logger.info(
                f"流水线开始处理，共 {self._total_count} 篇；"
                f"LLM解析={LLM_PARSE_WORKERS}线程，LLM格式化={LLM_FORMAT_WORKERS}线程"
            )

            # 3. 初始化浏览器爬虫（只初始化，不启动老的 crawl_all_articles
            self.crawler = ContentCrawler()
            self.crawler.signals.need_user_verify.connect(self.need_user_verify.emit)
            self.crawler.signals.log_msg.connect(self.log_msg.emit)

            # 4. 先启动 Stage2/Stage3 Worker（先启动 Consumer，避免队列积压）
            for i in range(LLM_PARSE_WORKERS):
                t = threading.Thread(target=self._parse_worker, args=(i,), daemon=True)
                self._parse_workers.append(t)
                t.start()
            for i in range(LLM_FORMAT_WORKERS):
                t = threading.Thread(target=self._format_worker, args=(i,), daemon=True)
                self._format_workers.append(t)
                t.start()

            # 5. 启动 UI 进度轮询线程
            self._progress_poll_th = threading.Thread(target=self._progress_poller, daemon=True)
            self._progress_poll_th.start()

            # 6. 启动 Stage1：浏览器爬取（仍为单线程，防反爬
            def _browser_progress(idx, total, msg):
                self.report_progress.emit(
                    self._format_done, self._total_count,
                    f"[浏览器 {idx}/{total}] {msg}"
                )
            def _log_cb(msg):
                self.log_msg.emit(msg)
            def _verify_cb():
                self.need_user_verify.emit()

            self._browser_th = threading.Thread(
                target=self._run_browser_stage,
                args=(db_articles, _browser_progress, _verify_cb, _log_cb),
                daemon=True,
            )
            self._browser_th.start()

            # 7. 等待 Stage1 完成
            self._browser_th.join()
            logger.info("Stage1 浏览器爬取阶段结束")

            # 8. Stage1 → Stage2：放 LLM_PARSE_WORKERS 个哨兵 None，每个 Worker 吃一个后退出
            for _ in range(LLM_PARSE_WORKERS):
                self._raw_queue.put(None)
            for t in self._parse_workers:
                t.join()
            logger.info("Stage2 LLM解析阶段结束")

            # 9. Stage2 → Stage3：放 LLM_FORMAT_WORKERS 个哨兵
            for _ in range(LLM_FORMAT_WORKERS):
                self._parsed_queue.put(None)
            for t in self._format_workers:
                t.join()
            logger.info("Stage3 LLM格式化+入库阶段结束")

            # 10. 等待 UI 进度轮询线程退出
            if self._progress_poll_th and self._progress_poll_th.is_alive():
                self._progress_poll_th.join(timeout=2.0)

            # 11. 收尾：最终完整进度
            with self._count_lock:
                fmt = self._format_done
                total = self._total_count
            self.report_progress.emit(fmt, total, f"全部 {fmt}/{total} 篇处理完成")

            ok = not self._any_stage_failed
            logger.info(f"流水线全部完成，success={ok}")
            self.task_over.emit(ok)

        except Exception as e:
            logger.error(f"流水线 GetArticleContentThread 异常: {e}")
            self._any_stage_failed = True
            raise GetArticleContentError(f"获取文章内容失败: {str(e)}") from e
        finally:
            self._cleanup()

    # ------------------------------------------------------------
    #  资源清理
    # ------------------------------------------------------------
    def _cleanup(self):
        self._stop_flag.set()
        try:
            if self.crawler:
                try:
                    self.crawler._verify_evt.set()  # pylint: disable=protected-access
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
                self.crawler.close_all_resource()
                self.wait()
        finally:
            self.crawler = None

    def stop(self):
        """停止流水线线程"""
        logger.info("请求停止流水线 GetArticleContentThread")
        self._stop_flag.set()
        try:
            if self.crawler:
                try:
                    self.crawler._verify_evt.set()  # pylint: disable=protected-access
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
                self.crawler.close_all_resource()
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        self.terminate()
        self.crawler = None
        self.wait()