import asyncio
import json
from threading import Thread
from typing import Any, Coroutine
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
        self.template_flow: http.HTTPFlow | None = None
    def __str__(self):
        return "ArticleListResponseHandler"
    def response(self, flow: http.HTTPFlow):
        """处理响应"""
        # 跳过重放产生的请求
        if flow.is_replay:
            return

        if flow.request.query.get("action") == "getmsg":
            logger.info("article list flow got: %s", flow.request.url)
            self.template_flow = flow.copy()


class Crawler:
    """爬虫类"""
    def __init__(self, handler):
        self.loop = asyncio.new_event_loop()
        self.response_handler = handler
        self.options = Options(listen_host="0.0.0.0", listen_port=LISTEN_PORT)
        self.master = DumpMaster(self.options, with_termlog=False, with_dumper=False, loop=self.loop)
        self.master.addons.add(self.response_handler)
        self._thread = Thread(target=self._run_loop, daemon=True)

    def _run_loop(self):
        """运行事件循环 + master"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.master.run())

    def start(self):
        """启动爬虫"""
        logger.info("start crawler, handler: %s", self.response_handler)
        self._thread.start()

    def stop(self):
        """安全停止 master + 事件循环"""      
        if self._thread.is_alive():
            self.master.shutdown()
            self.loop.stop()
            self._thread.join(timeout=5)
            logger.info("mitmproxy 已停止")

    def run_async(self, coro: Coroutine) -> Any:
        """异步运行"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()


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
        self.flow: http.HTTPFlow | None = None
        super().__init__(ArticleListResponseHandler())

    def has_template(self) -> bool:
        """是否已经捕获到模板 flow"""
        return self.response_handler.template_flow is not None

    def get_article_list(self, offset: int, count: int) -> list[dict] | None:
        """
        获取文章列表

        :param offset: 分页offset
        :param count: 分页数量

        :return: 文章列表
        """
        template: http.HTTPFlow | None = self.response_handler.template_flow
        if not template:
            logger.error("未捕获到文章列表模板 flow，无法重放")
            return None

        try:
            # 1. 基于模板复制新 flow，保留所有 cookie、headers、签名参数
            new_flow = template.copy()
            
            # 2. 仅修改分页参数，其他参数完全保留（保证签名校验通过）
            new_flow.request.query["offset"] = str(offset)
            new_flow.request.query["count"] = str(count)

            # 3. 跨线程提交重放任务，等待请求完成
            async def _replay_and_wait():
                # 执行客户端重放（主动发请求到服务器）
                await self.master.commands.call("replay.client", [new_flow])
                # 重放完成后，new_flow.response 已被填充
                return new_flow

            result_flow: http.HTTPFlow = self.run_async(_replay_and_wait())

            # 4. 校验响应并解析
            # TODO: 验证状态码
            if not result_flow.response:
                logger.error(f"重放请求失败，状态码: {getattr(result_flow.response, 'status_code', '无响应')}")
                return None

            # 解析微信返回的 JSON（微信接口返回通常是带 general_msg_list 的 JSON）
            resp_text = result_flow.response.text
            if not resp_text:
                logger.error("重放请求失败，响应体为空")
                return None
            
            # 微信部分接口会有转义，按需处理
            data = json.loads(resp_text)
            general_msg_list = json.loads(data.get("general_msg_list", "{}"))
            article_list = general_msg_list.get("list", [])
            
            logger.info(f"获取第 {offset} 页成功，共 {len(article_list)} 条")
            return article_list

        except Exception as e: # pylint: disable=broad-exception-caught
            logger.error("重放获取文章列表失败: %s", e)
            return None

