import asyncio
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import http

from constants import LISTEN_PORT

from utils.logging import get_logger
logger = get_logger(__name__)


class MpBizResponseHandler:
    """mp biz响应处理类"""
    def __init__(self):
        self.biz_result: str | None = None
    def __str__(self):
        return "MpBizResponseHandler"
    def response(self, flow: http.HTTPFlow):
        """处理响应"""
        biz = flow.request.query.get("__biz") or flow.request.query.get("biz")
        if biz is not None:
            logger.info("biz got: %s, flow: %s", biz, flow.request.url)
            self.biz_result = biz


class ArticleListResponseHandler:
    """文章列表URL响应处理类"""
    def __init__(self):
        self.article_list_flow: http.HTTPFlow | None = None
    def __str__(self):
        return "ArticleListResponseHandler"
    def response(self, flow: http.HTTPFlow):
        """处理响应"""
        if flow.request.query.get("action") == "getmsg":
            logger.info("article list flow got: %s", flow.request.url)
            self.article_list_flow = flow


class Crawler:
    """爬虫类"""
    def __init__(self, handler):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.response_handler = handler
        self.options = Options(listen_host="0.0.0.0", listen_port=LISTEN_PORT)
        self.master = DumpMaster(self.options, with_termlog=False, with_dumper=False, loop=self.loop)
        self.master.addons.add(self.response_handler)

    def start(self):
        """启动爬虫"""
        logger.info("start crawler, handler: %s", self.response_handler)
        self.loop.run_until_complete(self.master.run())

    def stop(self):
        """停止爬虫"""
        logger.info("stop crawler")
        self.master.shutdown()


class MpBizCrawler(Crawler):
    """biz爬虫类"""
    def __init__(self):
        super().__init__(MpBizResponseHandler())

    def get_mp_biz(self) -> str | None:
        """获取mp biz"""
        return self.response_handler.biz_result or None


class ArticleListCrawler(Crawler):
    """文章列表爬虫类"""
    def __init__(self):
        super().__init__(ArticleListResponseHandler())
    def get_article_list_flow(self) -> http.HTTPFlow | None:
        """获取文章列表URL flow"""
        return self.response_handler.article_list_flow or None

    def get_article_list(self, offset: int, count: int):
        """获取文章列表"""
        pass
