import sys
import os
import time
import re
import threading
from playwright.sync_api import sync_playwright, Page
from PySide6.QtCore import QObject, Signal, Qt

from llm.llm_parse import parse_creator_list_by_llm, format_creator_list_by_llm
from helpers.helpers import get_reader_stats
from models.article_models import Article
import constants as consts

from utils.logging import get_logger

logger = get_logger(__name__)

# 统一UA、浏览器参数
CONTEXT_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", # pylint: disable=line-too-long
    "viewport": {"width": 1280, "height": 720},
}

# 验证页URL特征正则
CAPTCHA_URL_REG = re.compile(r"mp/wappoc_appmsgcaptcha")
# 验证页面文字关键词
CAPTCHA_TEXT_KEYWORDS = ["环境异常", "前往验证", "人机验证", "安全校验"]

MAX_RETRIES = consts.MAX_RETRIES
FETCH_INTERVAL_S = consts.FETCH_INTERVAL_S

TEMP_CONTEXT_DIR = consts.TEMP_CONTEXT_DIR

class CrawlSignals(QObject):
    """
    爬虫信号类
    """
    log_msg = Signal(str)          # 打印日志
    need_user_verify = Signal()    # 需要用户手动验证弹窗提示
    task_over = Signal(bool)      # 任务结束信号
    verify_done = Signal(bool)     # [GUI → 爬虫：用户已完成人机验证，bool=True
    progress_update = Signal(int, int, str)  # (当前进度, 总数, 详细消息)


class ContentCrawler:
    """
    文章内容爬虫类
    """
    def __init__(self):
        browser_root = self._get_browser_root()
        self.env = os.environ.copy()
        self.env["PLAYWRIGHT_BROWSERS_PATH"] = browser_root

        self.signals = CrawlSignals()
        self.playwright = None
        self.context = None
        self._verify_page = None    # 用于人机验证的独立页面
        self._is_visible = False    # 当前浏览器窗口是否可见（面向用户）
        self._verify_evt = threading.Event()  # GUI 阻塞等待事件
        # 注意：信号在GUI线程发射后，若使用 QueuedConnection，槽函数会在爬虫线程执行；
        # 但爬虫线程当前正被 wait() 阻塞，无法派发自己的事件循环，
        # 因此此处用 DirectConnection 在发射者线程（GUI）直接执行 _on_verify_done，
        # 仅调用 Event.set()——它本身是线程安全的。
        self.signals.verify_done.connect(self._on_verify_done, Qt.ConnectionType.DirectConnection)

    @staticmethod
    def _get_browser_root() -> str:
        # 打包后 Nuitka _MEIPASS / 程序目录
        if hasattr(sys, "_MEIPASS"):
            # onefile 模式临时解压目录
            base = os.path.dirname(sys.executable)
            return os.path.join(base, "ms-playwright")
        elif "__compiled__" in globals():
            # standalone 文件夹模式
            base = os.path.abspath(".")
            return os.path.join(base, "ms-playwright")
        # 本地开发环境，读取系统默认缓存
        return os.path.join(os.environ["LOCALAPPDATA"], "ms-playwright")

    def _on_verify_done(self, ok: bool):
        """GUI调用的槽函数：标记验证完成，释放阻塞"""
        logger.info(f"收到GUI验证完成信号: ok={ok}")
        self._verify_evt.set()

    def wait_for_user_verify(self, timeout_s: int = 0) -> bool:
        """阻塞等待用户验证完成。timeout_s=0代表无限等待"""
        self._verify_evt.clear()
        if timeout_s > 0:
            result = self._verify_evt.wait(timeout=timeout_s)
        else:
            self._verify_evt.wait()
            result = True
        self._verify_evt.clear()
        return result

    def init_playwright(self):
        """初始化Playwright"""
        self.playwright = sync_playwright().start()

    def init_browser(self):
        """
        初始化浏览器。
        为保持 context 一致，浏览器始终以有头模式启动（仅 headless=False 时允许切换可见性），
        通过 CDP 控制窗口显隐来达到"后台静默/前台可见"的效果。
        """
        if not self.playwright:
            self.init_playwright()
        assert self.playwright is not None, "请先初始化Playwright"
        # 始终以 headed 方式启动，通过窗口位置/最小化控制是否"前台可见"
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=TEMP_CONTEXT_DIR,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--window-position=-32000,-32000",  # 启动时移出屏幕外，默认为"后台静默"
                "--window-size=1280,720",
            ],
            env=self.env, # type: ignore
            **CONTEXT_CONFIG.copy()
        )
        self.context.set_default_timeout(100000)  # 全局100s超时
        self._is_visible = False
        logger.info(f"浏览器初始化完成，默认后台静默模式 (headless launched as headed, hidden off-screen), context_args={CONTEXT_CONFIG}")

    def _ensure_verify_page(self, source_page=None):
        """确保存在一个用于承载人机验证交互的 page（在同一个 context 下）。"""
        if self._verify_page and not self._verify_page.is_closed():
            return self._verify_page
        if source_page and not source_page.is_closed():
            # 复用传入的 page 作为验证页（它本身就是验证页面）
            self._verify_page = source_page
        elif self.context:
            self._verify_page = self.context.new_page()
        return self._verify_page

    def _set_window_visible(self, visible: bool, page=None):
        """
        通过 CDP 的 Browser.setWindowBounds 控制浏览器窗口的位置：
          visible=True  -> 移动到屏幕可见区域，供用户手动完成验证
          visible=False -> 移动到屏幕外侧，达到"后台静默"效果
        整个过程始终使用同一个 browser + 同一个 context，不会销毁会话。
        """
        target_page = self._ensure_verify_page(page)
        if not target_page:
            return
        try:
            # 通过 CDP 获取当前浏览器窗口并修改其边界/位置
            assert self.context is not None
            cdp_session = self.context.new_cdp_session(target_page)
            window_info = cdp_session.send("Browser.getWindowForTarget")
            window_id = window_info.get("windowId")
            if window_id is None:
                logger.warning("CDP 获取 windowId 失败，无法切换窗口可见性")
                return
            if visible:
                cdp_session.send("Browser.setWindowBounds", {
                    "windowId": window_id,
                    "bounds": {"windowState": "normal"},
                })
                cdp_session.send("Browser.setWindowBounds", {
                    "windowId": window_id,
                    "bounds": {"left": 100, "top": 100, "width": 1280, "height": 800},
                })
                target_page.bring_to_front()
            else:
                cdp_session.send("Browser.setWindowBounds", {
                    "windowId": window_id,
                    "bounds": {"left": -32000, "top": -32000, "width": 1280, "height": 720},
                })
            self._is_visible = visible
            logger.info(f"浏览器窗口已切换为: {'前台可见' if visible else '后台静默'}")
        except Exception as err: # pylint: disable=broad-exception-caught
            logger.warning(f"切换浏览器窗口可见性失败，降级为仅 bring_to_front: {err}")
            # 降级方案：visible=True 时只把页面调到前台
            if visible and target_page:
                target_page.bring_to_front()

    def close_all_resource(self):
        """统一释放浏览器资源"""
        if self.playwright:
            self.playwright.stop()
        self.context = None

    def is_verify_page(self, page: Page) -> bool:
        """
        判断当前页面是否是微信公众号人机验证页
        返回True=需要人工验证；False=正常文章页面
        """
        # 1. URL精准判断（最高优先级）
        current_url = page.url
        if CAPTCHA_URL_REG.search(current_url):
            return True

        # 2. 兜底：读取页面文本匹配关键词（防止URL正常但页面渲染验证弹窗）
        page_html = page.content().lower()
        for kw in CAPTCHA_TEXT_KEYWORDS:
            if kw in page_html:
                return True

        # 正常文章页面
        return False

    def extract_raw_page_data(self, page: Page) -> tuple[str, dict]:
        """
        仅从页面提取原始数据，不调用LLM（用于流水线模式）。
        返回: (crop_text, reader_stats)
          - crop_text: 文末300字符原始文本
          - reader_stats: 阅读/点赞等统计数据字典
        """
        full_text = page.evaluate("() => document.body.innerText")
        crop_text = full_text[-300:]
        reader_stats = {}
        if consts.TEMPLATE_FLOW is not None:
            reader_stats = get_reader_stats(page.url, consts.TEMPLATE_FLOW)
        return crop_text, reader_stats

    def parse_article_data(self, page: Page, to_calc_fee: bool):
        """页面解析逻辑：提取落款、阅读量等信息（保留用于兼容旧逻辑）"""
        crop_text, reader_stats = self.extract_raw_page_data(page)
        creator_list = parse_creator_list_by_llm(crop_text)
        formatted_creator_list = format_creator_list_by_llm(creator_list) if to_calc_fee else {}
        return {
            "view_count": reader_stats.get("view_count", 0), # 阅读量
            "heart_count": reader_stats.get("heart_count", 0), # 爱心量
            "like_count": reader_stats.get("like_count", 0), # 在看量
            "share_count": reader_stats.get("share_count", 0), # 分享量
            "collect_count": reader_stats.get("collect_count", 0), # 收藏量
            "creator_list": creator_list,
            "formatted_creator_list": formatted_creator_list,
        }
    
    def crawl_pages_for_pipeline(self, article_list: list[Article], raw_queue, stop_flag, progress_cb, verify_cb, log_cb):
        """
        【流水线模式 Stage 1】仅负责浏览器页面爬取（单线程防反爬）。
        对每篇文章：
          1. 访问URL → 人机验证处理
          2. 提取文末300字符 crop_text + reader_stats
          3. 将 (article_id, title, crop_text, reader_stats, to_calc_fee_flag) 放入 raw_queue
        完成所有文章后向 raw_queue 放入 None 作为结束标志。

        :param article_list: 数据库 Article 对象列表
        :param raw_queue: queue.Queue，用于向 Stage2 输送原始页面数据
        :param stop_flag: threading.Event，外部请求停止时置位
        :param progress_cb: callable(idx, total, msg) 进度回调
        :param verify_cb: callable() 需要用户验证时的回调
        :param log_cb: callable(msg) 日志回调
        """
        page = None
        try:
            self.init_browser()
            if not self.context:
                logger.error("浏览器初始化失败")
                log_cb("browser init failed")
                raw_queue.put(None)
                return False

            page = self.context.new_page()
            total_count = len(article_list)

            for idx, article in enumerate(article_list, start=1):
                if stop_flag.is_set():
                    logger.info(f"收到停止信号，终止浏览器爬取，当前进度 {idx}/{total_count}")
                    break

                url = article.content_url
                if not url:
                    logger.error(f"文章《{article.title}》URL记录不完整。ID:{article.id}")
                    log_cb(f"URL记录不完整。ID:{article.id}，标题：{article.title}")
                    # 即使URL无效，也向队列塞一条空数据占位，保证各阶段计步一致
                    raw_queue.put({
                        "article_id": article.id,
                        "title": article.title,
                        "crop_text": "",
                        "reader_stats": {},
                        "skip": True,
                        "skip_reason": "URL无效",
                    })
                    continue

                progress_cb(idx, total_count, f"[浏览器] 正在访问 {idx}/{total_count}：《{article.title}》")

                load_ok = False
                for i in range(MAX_RETRIES):
                    if stop_flag.is_set():
                        break
                    try:
                        page.goto(url, wait_until="domcontentloaded")
                        load_ok = True
                        break
                    except Exception as e: # pylint: disable=broad-exception-caught
                        logger.error(f"第{i}次尝试，文章《{article.title}》内容加载失败: {str(e)}")
                        time.sleep(FETCH_INTERVAL_S)
                        continue
                time.sleep(FETCH_INTERVAL_S)

                if not load_ok:
                    logger.error(f"文章《{article.title}》内容加载失败，跳过")
                    log_cb(f"读取文章《{article.title}》内容失败，跳过")
                    raw_queue.put({
                        "article_id": article.id,
                        "title": article.title,
                        "crop_text": "",
                        "reader_stats": {},
                        "skip": True,
                        "skip_reason": "页面加载失败",
                    })
                    continue

                # --- 人机验证处理循环 ---
                verify_skip = False
                while self.is_verify_page(page):
                    if stop_flag.is_set():
                        verify_skip = True
                        break
                    logger.info(f"检测到人机验证, 文章《{article.title}》")
                    log_cb("检测到人机验证，请在浏览器窗口完成验证...")
                    self._ensure_verify_page(page)
                    self._set_window_visible(True, page=page)
                    verify_cb()  # 触发GUI提示
                    verify_ok = self.wait_for_user_verify()
                    page.wait_for_timeout(1500)
                    if not verify_ok:
                        logger.warning(f"用户取消验证，文章《{article.title}》")
                        log_cb("用户取消验证，跳过当前文章")
                        verify_skip = True
                        break
                    if self.is_verify_page(page):
                        continue
                    break

                self._set_window_visible(False, page=page)

                if verify_skip or stop_flag.is_set():
                    raw_queue.put({
                        "article_id": article.id,
                        "title": article.title,
                        "crop_text": "",
                        "reader_stats": {},
                        "skip": True,
                        "skip_reason": "验证跳过/停止信号",
                    })
                    if stop_flag.is_set():
                        break
                    continue

                # 提取原始数据（不调用LLM）
                try:
                    crop_text, reader_stats = self.extract_raw_page_data(page)
                except Exception as ex: # pylint: disable=broad-exception-caught
                    logger.warning(f"提取页面原始数据失败，文章《{article.title}》: {ex}")
                    crop_text, reader_stats = "", {}

                raw_queue.put({
                    "article_id": article.id,
                    "title": article.title,
                    "crop_text": crop_text,
                    "reader_stats": reader_stats,
                    "skip": False,
                })

            # 流水线Stage1结束标记：所有Stage2 worker共享同一个None哨兵数量应等于worker数，
            # 具体由外部threads控制者put多个None，这里不再额外放哨兵
            logger.info(f"浏览器爬取阶段结束，共处理 {idx if 'idx' in dir() else 0}/{total_count}") # type: ignore # pylint: disable=undefined-loop-variable
            return True

        except Exception as err: # pylint: disable=broad-exception-caught
            logger.error(f"浏览器爬取阶段异常：{str(err)}")
            log_cb(f"浏览器爬取阶段异常：{str(err)}")
            return False
        finally:
            # 资源由外部 threads.stop() 统一释放
            pass

