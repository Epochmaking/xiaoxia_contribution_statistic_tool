import time
from PySide6.QtCore import Signal
from PySide6.QtCore import QThread

from controllers.crawler import MpBizCrawler, ArticleListCrawler
from constants import MAX_RETRIES, FETCH_INTERVAL_S

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
    task_over = Signal(str)
    flow_got = Signal(bool)

    def __init__(self):
        super().__init__()
        self.to_stop = False # 停止thread标志
        self.crawler = None

    def run(self):
        """线程运行方法"""
        self.to_stop = False
        # 每次运行时创建新的爬虫实例（线程只能启动一次）
        self.crawler = ArticleListCrawler()
        try:
            self.crawler.start()
            while not self.to_stop:
                if self.crawler.has_template():
                    logger.info("已捕获到文章列表接口模板，可开始分页拉取")
                    self.flow_got.emit(True)
                    break
                time.sleep(0.5)

            # ========== 示例：循环拉取多页 ==========
            all_articles = []
            offset = 0
            page_size = 10
            max_page = 1  # 拉取页数按需调整

            for _ in range(max_page):
                if self.to_stop:
                    break
                time.sleep(FETCH_INTERVAL_S)  # 控制请求频率，避免被微信拦截

                articles = None

                for _ in range(MAX_RETRIES): # 最多尝试MAX_RETRIES次获取文章列表
                    articles = self.crawler.get_article_list(offset, page_size)
                    if articles is not None:
                        break
                    time.sleep(FETCH_INTERVAL_S)  # 控制请求频率，避免被微信拦截
                if articles is None:
                    break

                all_articles.extend(articles)
                offset += page_size

                for article in articles:
                    logger.info("获取到文章: %s", article)

            self.task_over.emit(f"拉取完成，共获取 {len(all_articles)} 篇文章")
        finally:
            self.crawler.stop()

    def stop(self):
        """停止线程"""
        self.to_stop = True
        self.wait()
