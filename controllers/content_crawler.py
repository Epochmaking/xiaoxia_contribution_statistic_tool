import json
import time
import re
import threading
from playwright.sync_api import sync_playwright, Page
from PySide6.QtCore import QObject, Signal, Qt

from database.db import get_session
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


class ContentCrawler:
    """
    文章内容爬虫类
    """
    def __init__(self):
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

    def parse_article_data(self, page: Page, to_calc_fee: bool):
        """页面解析逻辑：提取落款、阅读量等信息"""
        # 获取页面全部纯文本
        full_text = page.evaluate("() => document.body.innerText")
        crop_text = full_text[-300:] # 取最后300个字符
        creator_list = parse_creator_list_by_llm(crop_text)
        formatted_creator_list = format_creator_list_by_llm(creator_list) if to_calc_fee else {}
        if consts.TEMPLATE_FLOW is not None:
            reader_stats = get_reader_stats(page.url, consts.TEMPLATE_FLOW)
        else:
            reader_stats = {}
        return {
            "view_count": reader_stats.get("view_count", 0), # 阅读量
            "heart_count": reader_stats.get("heart_count", 0), # 爱心量
            "like_count": reader_stats.get("like_count", 0), # 在看量
            "share_count": reader_stats.get("share_count", 0), # 分享量
            "collect_count": reader_stats.get("collect_count", 0), # 收藏量
            "creator_list": creator_list,
            "formatted_creator_list": formatted_creator_list,
        }
    
    def crawl_all_articles(self, to_calc_fee: bool):
        """
        主爬取逻辑，运行在QThread内部。
        流程改进：
          - 默认保持浏览器窗口后台静默（窗口移至屏幕外）
          - 仅在触发人机验证时将窗口移回屏幕可见区域
          - 用户完成验证后立即再次隐藏窗口
          - 全程复用同一个 browser + context，保证 Cookie / 会话一致性
        """
        # TODO: 多线程并行处理，提高效率
        page = None
        try:
            # 1. 单独读取数据库，快速释放db会话，不长期占用
            with get_session() as db_session:
                article_list = db_session.query(Article).all()
            if not article_list:
                self.signals.log_msg.emit("数据库无待爬取文章")
                self.signals.task_over.emit(True)
                return

            # 2. 初始化浏览器（始终 headed 启动，启动时窗口即位于屏幕外）
            self.init_browser()

            if not self.context:
                self.signals.log_msg.emit("browser init failed")
                self.signals.task_over.emit(False)
                logger.error("浏览器初始化失败")
                return

            page = self.context.new_page()

            # 3. 循环遍历所有文章URL
            for article in article_list:
                url = article.content_url
                if not url:
                    logger.error(f"文章《{article.title}》URL记录不完整。ID:{article.id}")
                    self.signals.log_msg.emit(f"URL记录不完整。ID:{article.id}，标题：{article.title}")
                    self.signals.task_over.emit(False)
                    return

                self.signals.log_msg.emit(f"正在访问：《{article.title}》")

                for i in range(MAX_RETRIES):
                    try:
                        page.goto(url, wait_until="domcontentloaded")
                        break
                    except Exception as e: # pylint: disable=broad-exception-caught
                        logger.error(f"第{i}次尝试，文章《{article.title}》内容加载失败: {str(e)}")
                        if i < MAX_RETRIES - 1:
                            continue
                        else:
                            logger.error(f"文章《{article.title}》内容加载失败: {str(e)}")
                            self.signals.log_msg.emit(f"读取文章《{article.title}》内容失败，请检查网络连接")
                            self.signals.task_over.emit(False)
                            return
                    finally:
                        time.sleep(FETCH_INTERVAL_S)

                # 检测验证页面 —— 不销毁 browser/context，只切换窗口可见性
                if self.is_verify_page(page):
                    logger.info(f"检测到人机验证, 文章《{article.title}》")
                    self.signals.log_msg.emit("检测到人机验证，请在浏览器窗口完成验证...")
                    # 将当前 page 标记为"验证页"，供 CDP 操作窗口使用
                    self._ensure_verify_page(page)
                    # 窗口移回可见区域
                    self._set_window_visible(True, page=page)
                    self.signals.need_user_verify.emit()
                    # 阻塞等待用户操作完成：GUI 层关闭 msgbox 后回传 verify_done 信号
                    # 方案A（GUI交互推荐）：Qt信号等待 + threading.Event 跨线程安全唤醒
                    # TODO: 用户验证完成自动进入下一步，不用点ok
                    logger.info("爬虫线程进入等待用户验证阻塞...")
                    verify_ok = self.wait_for_user_verify()
                    logger.info(f"爬虫线程已被唤醒，验证结果: {verify_ok}")

                    # 验证后刷新会话缓存，并立刻把窗口重新隐藏
                    page.wait_for_timeout(1500)
                    self._set_window_visible(False, page=page)

                # 解析文章数据
                data = self.parse_article_data(page, to_calc_fee)
                if not data:
                    logger.error(f"{url} 解析数据为空")
                    self.signals.log_msg.emit(f"{url} 解析数据为空")
                    continue

                # 写入数据库：单独开db会话，避免长连接
                with get_session() as db_session:
                    target = db_session.query(Article).filter(Article.id == article.id).first()
                    if target:
                        target.view_count = data.get("view_count", 0)
                        target.heart_count = data.get("heart_count", 0)
                        target.like_count = data.get("like_count", 0)
                        target.share_count = data.get("share_count", 0)
                        target.collect_count = data.get("collect_count", 0)
                        target.creators_list = data.get("creator_list", "")
                        target.formatted_creators_list = json.dumps(data.get("formatted_creator_list", {}), ensure_ascii=False)
                        db_session.commit()
                        logger.info(
                            f"更新成功 ID:{article.id}, 题目：《{article.title}》\n"
                            f"阅读量：{data.get('view_count', 0)}, 爱心量：{data.get('heart_count', 0)}, 在看量：{data.get('like_count', 0)}, 分享量：{data.get('share_count', 0)}, 评论量：{data.get('comment_count', 0)}\n"
                            f"落款信息：{data.get('creator_list', '')}\n格式化作者列表：{data.get('formatted_creator_list', {})}"
                        )
                        self.signals.log_msg.emit(f"更新成功 ID:{article.id}")
                    else:
                        logger.warning(f"数据库中未找到 ID={article.id} 的文章，跳过写入")

            logger.info("全部文章爬取完成")
            self.signals.log_msg.emit("全部文章爬取完成")
            self.signals.task_over.emit(True)

        except Exception as err: # pylint: disable=broad-exception-caught
            logger.error(f"爬取任务异常终止：{str(err)}")
            self.signals.log_msg.emit(f"爬取任务异常终止：{str(err)}")
            self.signals.task_over.emit(False)
        finally:
            # 无论成功失败，强制关闭浏览器
            self.close_all_resource()