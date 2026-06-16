"""UI组件模块"""
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt
from ui.ui_compiled.main_win import Ui_MainForm
from controllers.threads import GetMpBizThread

import constants as consts
from utils.logging import get_logger


logger = get_logger(__name__)

MP_BIZ: str | None = None


class MainWindow(QWidget, Ui_MainForm):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 1. 设置窗口标志：无边框
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 2. 设置背景透明（必须和无边框一起用）
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)

        # 连接按钮点击事件
        self.close_win_btn.clicked.connect(self.close_win_btn_on_click)
        self.minimize_win_btn.clicked.connect(self.minimize_win_btn_on_click)
        self.step_one_btn_connection = self.step_one_btn.clicked.connect(self.step_one_btn_on_click)

        # 用于拖动窗口
        self.m_drag = False
        self.m_drag_position = None

        # 按钮点击事件标记
        self.step_one_start = False

        # 注册线程
        self.get_mp_biz_thread = GetMpBizThread()
        self.get_mp_biz_thread.task_over.connect(self.get_mp_biz_task_over)

    # 步骤一任务完成
    def get_mp_biz_task_over(self, biz_result: str):
        """步骤一任务完成"""
        # 保存到全局变量
        consts.MP_BIZ = biz_result
        consts.ARTICLE_LIST_URL = f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz_result}#wechat_redirect"

        # 停止线程
        self.get_mp_biz_thread.stop()

        # 弹窗提示获取到的微信公众号BIZ
        logger.info("获取到微信公众号BIZ: %s", biz_result)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("置顶提示")
        msg_box.setText(f"获取到的微信公众号BIZ: {biz_result}")
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg_box.exec()

        # 绑定按钮为下一步按钮
        self.step_one_btn.setText("下一步")
        self.step_one_start = False
        self.step_one_btn.disconnect(self.step_one_btn_connection)
        self.step_one_btn.clicked.connect(self.go_to_next_step)



    # 鼠标按下
    # pylint: disable=invalid-name
    def mousePressEvent(self, event): 
        """鼠标按下事件，用于拖动窗口"""
        if self.title_bar.underMouse() and event.button() == Qt.MouseButton.LeftButton:
            self.m_drag = True
            self.m_drag_position = event.globalPos() - self.pos()
            event.accept()

    # 鼠标移动
    def mouseMoveEvent(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if event.buttons() & Qt.MouseButton.LeftButton and self.m_drag:
            self.move(event.globalPos() - self.m_drag_position)
            event.accept()

    # 鼠标释放开
    def mouseReleaseEvent(self, event):
        """鼠标释放开事件，用于拖动窗口"""
        if self.title_bar.underMouse() and event.button() == Qt.MouseButton.LeftButton:
            self.m_drag = False
            event.accept()

    # pylint: enable=invalid-name


    def close_win_btn_on_click(self):
        """关闭按钮点击事件"""
        self.close()

    def minimize_win_btn_on_click(self):
        """最小化按钮点击事件"""
        self.showMinimized()

    def go_to_next_step(self):
        """下一步"""
        logger.info("进入下一步")
        current_index = self.stackedWidget.currentIndex()
        next_index = current_index + 1
        if next_index < self.stackedWidget.count() - 1:
            self.stackedWidget.setCurrentIndex(next_index)

        # 根据不同步骤，附加不同逻辑做页面初始化
        if next_index == 1:
            # 步骤二：提供文章列表URL链接
            assert consts.ARTICLE_LIST_URL is not None, "文章列表URL未设置"
            self.article_list_url.setText(consts.ARTICLE_LIST_URL)
            self.article_list_url.setSelection(0, len(self.article_list_url.text()))


    def step_one_btn_on_click(self):
        """步骤一按钮点击事件"""
        if not self.step_one_start:
            self.step_one_start = True
            self.step_one_btn.setText("停止获取")
            logger.info("开始获取微信公众号BIZ")
            self.get_mp_biz_thread.start()
        else:
            self.step_one_start = False
            self.step_one_btn.setText("开始获取")
            logger.info("停止获取微信公众号BIZ")
            self.get_mp_biz_thread.stop()
