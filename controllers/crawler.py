import asyncio
from threading import Thread
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
        biz = flow.request.query.get("__biz")
        if biz is not None:
            logger.info("biz got: %s", biz)
            self.biz_result = biz

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

    def get_mp_biz(self) -> str | None:
        """获取mp biz"""
        return self.response_handler.biz_result
