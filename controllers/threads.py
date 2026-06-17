import time
from threading import Thread
from PySide6.QtCore import Signal
from PySide6.QtCore import QThread
from mitmproxy import http

from controllers.crawler import MpBizCrawler, ArticleListCrawler

from utils import logging

logger = logging.get_logger(__name__)

class GetMpBizThread(QThread):
    """获取微信公众号BIZ"""
    task_over = Signal(str)

    def __init__(self):
        super().__init__()
        self.to_stop = False # 停止thread标志
        self.crawler = MpBizCrawler()

    def run(self):
        """线程运行方法"""
        self.to_stop = False
        self.crawler.start()
        while True:
            if self.to_stop:
                self.crawler.stop()
                logger.info("停止获取微信公众号BIZ")
                break
            mp_biz = self.crawler.get_mp_biz()
            if mp_biz is not None:
                self.to_stop = True
                self.crawler.stop()
                logger.info("获取到微信公众号BIZ: %s", mp_biz)
                self.task_over.emit(mp_biz)
                break
    
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
        self.crawler = ArticleListCrawler()

    def run(self):
        """线程运行方法"""
        self.to_stop = False
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
            articles = self.crawler.get_article_list(offset, page_size)
            if not articles:
                break
            all_articles.extend(articles)
            offset += page_size
            for article in articles:
                logger.info("获取到文章: %s", article)
            time.sleep(1)  # 控制请求频率，避免被微信拦截

        # 所有拉取完成后再停止爬虫
        self.crawler.stop()
        self.task_over.emit(f"拉取完成，共获取 {len(all_articles)} 篇文章")
    
    def stop(self):
        """停止线程"""
        self.to_stop = True
        self.wait()

