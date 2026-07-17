import asyncio
import json
from threading import Thread, Event
from typing import Any, Coroutine
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import http

from controllers.proxy import unset_network_proxy, set_network_proxy
from constants import LISTEN_PORT, MAX_TIMEOUT_S, LISTEN_HOST

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
            self.template_flow = flow.copy()
            self.biz_result = biz


class ArticleListResponseHandler:
    """文章列表URL响应处理类"""
    def __init__(self):
        self.template_flow: http.HTTPFlow | None = None
        self.template_cookie_flow: http.HTTPFlow | None = None
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

        if flow.request.query.get("action") == "urlcheck":
            logger.info("urlcheck flow got: %s", flow.request.url)
            self.template_cookie_flow = flow.copy()


class Crawler:
    """爬虫类"""
    def __init__(self, handler):
        self.response_handler = handler
        self.listen_port = LISTEN_PORT
        self._loop = None
        self.master = None
        self._thread = None
        self._ready_event = None

    def _run_loop(self):
        """运行事件循环 + master"""
        assert self._ready_event is not None
        # 1. 子线程内创建并绑定事件循环
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # 2. 子线程内初始化 DumpMaster
        opts = Options(
            listen_host="0.0.0.0",
            listen_port=self.listen_port,
            ssl_insecure=True
        )
        self.master = DumpMaster(opts, with_termlog=False, with_dumper=False, loop=self._loop)
        self.master.addons.add(self.response_handler)

        try:
            # 3. 通知外部初始化完成
            self._ready_event.set()

            # 4. 启动运行
            self._loop.run_until_complete(self.master.run())
        except (RuntimeError, asyncio.CancelledError):
            logger.info("crawler _loop exit") # 任务退出
        finally:
            # 在事件循环所在线程内取消并等待所有未完成任务，避免 "Task was destroyed but it is pending" 警告
            try:
                # 在本线程的事件循环内执行清理协程，确保所有任务被等待
                self._loop.run_until_complete(self._cleanup())
            except Exception as e: # pylint: disable=broad-exception-caught
                logger.exception("_loop cleanup error: %s", e)
            finally:
                self._loop.close()

    async def _cleanup(self):
        # 排除当前运行的 cleanup task 自身
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        if not tasks:
            return
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    def start(self):
        """启动爬虫"""
        set_network_proxy(LISTEN_HOST, LISTEN_PORT) # 设置代理
        self._ready_event = Event()  # 用于等待master初始化完成
        self._thread = Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._ready_event.wait(timeout=5)  # 阻塞到初始化完成
        logger.info("start crawler, handler: %s", self.response_handler)

    def stop(self):
        """安全停止 master + 事件循环""" 
        try:
            if self.master is not None:
                self.master.shutdown() # 告知 DumpMaster 关闭（线程安全）
            # self._loop.call_soon_threadsafe(self._loop.stop) # 安排由事件循环所在线程去停止 _loop，避免跨线程 await
        except Exception as e: # pylint: disable=broad-exception-caught
            logger.exception("master _loop stop error: %s", e)
        finally:
            unset_network_proxy() # 取消代理
            self.master = None

        if self._thread is not None:
            self._thread.join(timeout=5)
            if self._thread.is_alive():
                logger.warning("crawler thread did not exit within timeout")

        self._thread = None
        self._ready_event = None
        self._loop = None

    def run_async(self, coro: Coroutine) -> Any:
        """异步运行"""
        assert self._loop is not None
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
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
    
    def has_cookie_template(self) -> bool:
        """是否已经捕获到包含cookie的模板 flow"""
        return self.response_handler.template_cookie_flow is not None
    
    def get_cookie_template(self) -> http.HTTPFlow | None:
        """获取包含cookie的模板 flow"""
        return self.response_handler.template_cookie_flow
    
    def get_template(self) -> http.HTTPFlow | None:
        """获取文章列表模板 flow"""
        return self.response_handler.template_flow

    async def _replay_and_wait(self, new_flow: http.HTTPFlow, timeout_s: float = 10.0) -> http.HTTPFlow | None:
        assert self.master is not None
        # 执行客户端重放（主动发请求到服务器）
        logger.info("replay flow: %s", new_flow)
        self.master.commands.call("replay.client", [new_flow])
        # 等待 response 被填充，带超时保护
        interval = 0.1
        waited = 0.0
        while waited < timeout_s:
            if new_flow.response:
                return new_flow
            await asyncio.sleep(interval)
            waited += interval
        logger.error("重放请求超时（%ss），未收到响应: %s", timeout_s, new_flow.request.url)
        # 重放完成后，new_flow.response 已被填充
        return new_flow

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
            result_flow: http.HTTPFlow = self.run_async(self._replay_and_wait(new_flow, MAX_TIMEOUT_S))

            # 4. 校验响应并解析
            assert result_flow.response is not None
            if result_flow.response.status_code != 200:
                logger.error(f"重放请求失败，状态码: {result_flow.response.status_code}")
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

            return article_list

        except Exception as e: # pylint: disable=broad-exception-caught
            logger.error("重放获取文章列表失败: %s", e)
            return None
