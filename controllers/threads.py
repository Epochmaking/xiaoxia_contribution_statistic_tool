import time
import random
from datetime import datetime
from PySide6.QtCore import Signal
from PySide6.QtCore import QThread

from controllers.crawler import MpBizCrawler, ArticleListCrawler
from controllers.content_crawler import ContentCrawler
from helpers.helpers import parse_and_crop_article_list, persist_articles_to_db
import constants as consts
from constants import MAX_RETRIES, FETCH_INTERVAL_S
from exceptions.exceptions import GetArticleContentError

from utils import logging

logger = logging.get_logger(__name__)

class GetMpBizThread(QThread):
    """获取微信公众号BIZ"""
    task_over = Signal(str)

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
                if mp_biz is not None:
                    self.to_stop = True
                    logger.info("获取到微信公众号BIZ: %s", mp_biz)
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
                if self.crawler.has_template() and self.crawler.has_cookie_template():
                    logger.info("已捕获到文章列表接口模板，可开始分页拉取")
                    consts.TEMPLATE_FLOW = self.crawler.get_cookie_template()
                    self.flow_got.emit(True)
                    break
                time.sleep(0.5)

            # ========== 调试用 ==========
            if False:
                all_articles = [
                    {
                        "title": "今天，厦大获中共中央表彰！",
                        "author": "厦门大学",
                        "publishing_time": "1782897820",
                        "content_url": "http://mp.weixin.qq.com/s?__biz=MzA3OTM1MTIzNQ==&amp;mid=2653264807&amp;idx=1&amp;sn=e4ce0b28f1ed01aa5e9634a79454b3fd&amp;chksm=85fc369d045317a55e5750e0727426eba5111f306142bfa15905b7fe34b17934ed136de0973c&amp;scene=27#wechat_redirect",
                        "type": "图文",
                    },
                    {
                        "title": "100年囊萤星火！105年向党同行！",
                        "author": "厦门大学",
                        "publishing_time": "1782869714",
                        "content_url": "http://mp.weixin.qq.com/s?__biz=MzA3OTM1MTIzNQ==&amp;mid=2653264778&amp;idx=1&amp;sn=5ef43eec88ab383f861b58fa69ab8503&amp;chksm=850a2ef041f5536a16f256cc64cd6a487c9f90bf7102c71d580fd3f461a980e8d8c4195b723d&amp;scene=27#wechat_redirect",
                        "type": "图文",
                    },
                    {
                        "title": "囊萤星火燃夏夜，厦大青年正当时✨",
                        "author": "",
                        "publishing_time": "1783425868",
                        "content_url": "https://mp.weixin.qq.com/s?__biz=MzA3OTM1MTIzNQ==&amp;mid=2653265026&amp;idx=1&amp;sn=5a9ef44ff50da61fa33947793e303759&amp;chksm=85c47c7e4b0b2a4534ff2481d3ba521f5cc8fcdb22ac44e682afb6cda86dae7fab49c0991b7a&amp;scene=27#wechat_redirect",
                        "type": "图文",
                    },
                    {
                        "title": "厦园的凤凰花，红了",
                        "author": "",
                        "publishing_time": "1782025868",
                        "content_url": "https://mp.weixin.qq.com/s/A8KQLaCUVTQr4057aCWNIg",
                        "type": "图文",
                    },
                ]
                time.sleep(3)
                self.task_over.emit(all_articles)
                return


            # ========== 示例：循环拉取多页 ==========
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
                    time.sleep(FETCH_INTERVAL_S+random.uniform(-FETCH_INTERVAL_S/2.0, FETCH_INTERVAL_S*2.0))  # 控制请求频率，避免被微信拦截
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

                logger.info("本轮获取到文章: %s", articles)

                page_num += 1

            self.task_over.emit(all_articles)
        finally:
            self.crawler.stop()

    def stop(self):
        """停止线程"""
        self.to_stop = True
        self.wait()


class GetArticleContentThread(QThread):
    """
    获取文章内容线程类
    """
    article_list_persist_ok = Signal()
    need_user_verify = Signal()      # 转发 ContentCrawler.need_user_verify
    def __init__(self, article_list: list[dict]):
        super().__init__()
        # self.to_stop = False # 停止thread标志
        self.article_list = article_list
        self.crawler: ContentCrawler | None = None

    def run(self):
        """
        运行方法
        """
        try:
            # 将确认好的文章列表写入数据库
            persist_articles_to_db(self.article_list)
            self.article_list_persist_ok.emit()
            self.crawler = ContentCrawler()
            # 转发爬虫的 need_user_verify 信号到线程自身，GUI 层连接线程信号即可
            self.crawler.signals.need_user_verify.connect(self.need_user_verify.emit)
            # 同时把日志也转发出来（供未来扩展）
            #self.crawler.signals.log_msg.connect(lambda s: logger.info(s))
            self.crawler.crawl_all_articles()

        except Exception as e:
            logger.error("获取文章内容失败: %s", e)
            raise GetArticleContentError(f"获取文章内容失败: {str(e)}") from e

    def stop(self):
        """
        停止方法
        """
        # 强制停止线程
        try:
            if self.crawler:
                # 如果爬虫当前正阻塞在人机验证等待上，先唤醒它以避免死锁
                try:
                    self.crawler._verify_evt.set()  # pylint: disable=protected-access
                except Exception:
                    pass
                self.crawler.close_all_resource()
        finally:
            self.terminate()
            self.crawler = None