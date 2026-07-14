from datetime import datetime
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt, QDate

from ui.ui_compiled.main_win import Ui_MainForm
from ui.ui_helper import set_article_confirm_table
from controllers.threads import GetMpBizThread, GetArticleListThread, AnalyseThread
from helpers.config_helper import write_config, del_config
from exceptions import AnalyseThreadError

import constants as consts
from utils.logging import get_logger


logger = get_logger(__name__)


class MainWindow(QWidget, Ui_MainForm):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 1. 设置窗口标志：无边框
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 2. 设置背景透明（必须和无边框一起用）
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0) # 3. 初始化显示步骤一
        self.date_edit.setDate(QDate.currentDate())

        # 连接按钮点击事件
        self.close_win_btn.clicked.connect(self.close_win_btn_on_click)
        self.minimize_win_btn.clicked.connect(self.minimize_win_btn_on_click)
        self.step_one_btn_connection = self.step_one_btn.clicked.connect(self.step_one_btn_on_click)
        self.step_two_btn_connection = self.step_two_btn.clicked.connect(self.step_two_btn_on_click)
        self.step_three_btn_connection = self.step_three_btn.clicked.connect(self.step_three_btn_on_click)
        self.reget_biz_btn_connection = self.reget_biz_btn.clicked.connect(self.reget_biz_btn_on_click)

        # 初始化显示已获取的BIZ
        if consts.MP_BIZ:
            self.biz_display_label.setText(consts.MP_BIZ)
            self.reget_biz_btn.setVisible(True)
            consts.ARTICLE_LIST_URL = consts.ARTICLE_LIST_URL_TEMPLATE.format(biz=consts.MP_BIZ)
            # 绑定按钮为下一步按钮
            self.step_one_btn.setText("下一步")
            self.step_start = False
            self.step_one_btn.disconnect(self.step_one_btn_connection)
            self.step_one_btn_connection = self.step_one_btn.clicked.connect(self.go_to_next_step)
        else:
            self.reget_biz_btn.setVisible(False)

        # 用于拖动窗口
        self.m_drag = False
        self.m_drag_position = None

        # 按钮点击事件标记
        self.step_start = False

        # 注册线程
        self.get_mp_biz_thread = None
        self.get_article_list_thread = None
        self.analyse_thread = None

        # 注册变量
        self.article_list = []

    # 步骤一任务完成
    def get_mp_biz_task_over(self, biz_result: str):
        """步骤一任务完成"""
        # 保存到全局变量
        consts.MP_BIZ = biz_result
        consts.ARTICLE_LIST_URL = consts.ARTICLE_LIST_URL_TEMPLATE.format(biz=biz_result)

        # 停止线程并断开信号槽连接
        if self.get_mp_biz_thread is not None:
            self.get_mp_biz_thread.stop()
            self.get_mp_biz_thread.task_over.disconnect()
            self.get_mp_biz_thread = None

        # 弹窗提示获取到的微信公众号BIZ
        logger.info("获取到微信公众号BIZ: %s", biz_result)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("置顶提示")
        msg_box.setText(f"获取到的微信公众号BIZ: {biz_result}")
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg_box.exec()

        # 写入至配置文件并更新到“已获取biz”当中
        write_config({"mp_id": biz_result})
        self.biz_display_label.setText(biz_result)

        # 显示重新获取按钮
        self.reget_biz_btn.setVisible(True)

        # 绑定按钮为下一步按钮
        self.step_one_btn.setText("下一步")
        self.step_start = False
        self.step_one_btn.disconnect(self.step_one_btn_connection)
        self.step_one_btn_connection = self.step_one_btn.clicked.connect(self.go_to_next_step)

    # 步骤二任务完成
    def get_article_list_task_over(self, all_articles: list[dict]):
        """步骤二任务完成"""
        # 停止线程并断开信号槽连接
        if self.get_article_list_thread is not None:
            self.get_article_list_thread.stop()
            self.get_article_list_thread.task_over.disconnect()
            self.get_article_list_thread = None

        self.step_start = False

        if len(all_articles) == 0:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("置顶提示")
            msg_box.setText("获取失败，请检查网络连接或稍后再试")
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            msg_box.exec()

            # 绑定按钮为开始获取按钮
            self.step_two_btn.setText("开始获取")
            self.step_two_btn.disconnect(self.step_two_btn_connection)
            self.step_two_btn_connection = self.step_two_btn.clicked.connect(self.step_two_btn_on_click)
            return
        
        # 写入变量
        self.article_list = all_articles

        # 绑定按钮为下一步按钮
        self.step_two_btn.disconnect(self.step_two_btn_connection)
        self.go_to_next_step()

        # 弹窗提示获取到的文章数量
        logger.info("获取到的文章数量: %d", len(all_articles))

        set_article_confirm_table(self.article_confirm_table, all_articles)

    def analyse_thread_article_list_persist_ok(self):
        """分析线程文章列表写入数据库完成"""
        logger.info("分析线程文章列表写入数据库完成")
        msg_box = QMessageBox()
        msg_box.setWindowTitle("置顶提示")
        msg_box.setText("分析线程文章列表写入数据库完成")
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg_box.exec()
        self.step_three_btn.setText("结束")
        self.step_start = False
        self.step_three_btn.disconnect(self.step_three_btn_connection)


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

    def reget_biz_btn_on_click(self):
        """重新获取按钮点击事件"""
        consts.MP_BIZ = None
        del_config("mp_id")
        self.biz_display_label.setText("无")
        self.reget_biz_btn.setVisible(False)
        self.step_one_btn.setText("开始获取")
        self.step_start = False
        self.step_one_btn.disconnect(self.step_one_btn_connection)
        self.step_one_btn.clicked.connect(self.step_one_btn_on_click)

    def go_to_next_step(self):
        """下一步"""
        logger.info("进入下一步")
        current_index = self.stackedWidget.currentIndex()
        next_index = current_index + 1
        if next_index <= self.stackedWidget.count() - 1:
            self.stackedWidget.setCurrentIndex(next_index)

        # 根据不同步骤，附加不同逻辑做页面初始化
        if next_index == 1:
            # 步骤二：提供文章列表URL链接
            assert consts.ARTICLE_LIST_URL is not None, "文章列表URL未设置"
            self.article_list_url.setText(consts.ARTICLE_LIST_URL)
            self.article_list_url.setSelection(0, len(self.article_list_url.text()))
        if next_index == 2:
            # 步骤三：提供文章列表
            pass

    def step_one_btn_on_click(self):
        """步骤一按钮点击事件"""
        if not self.step_start:
            self.step_start = True
            self.step_one_btn.setText("停止获取")
            logger.info("开始获取微信公众号BIZ")
            self.get_mp_biz_thread = GetMpBizThread()
            self.get_mp_biz_thread.task_over.connect(self.get_mp_biz_task_over)
            self.get_mp_biz_thread.start()
        else:
            self.step_start = False
            self.step_one_btn.setText("开始获取")
            logger.info("停止获取微信公众号BIZ")
            if self.get_mp_biz_thread is not None:
                self.get_mp_biz_thread.stop()
                self.get_mp_biz_thread.task_over.disconnect()
                self.get_mp_biz_thread = None

    def step_two_btn_on_click(self):
        """步骤二按钮点击事件"""
        if not self.step_start:
            self.step_start = True
            self.step_two_btn.setText("停止获取")

            logger.info("开始获取文章列表")

            self.get_article_list_thread = GetArticleListThread()
            self.get_article_list_thread.task_over.connect(self.get_article_list_task_over)

            time_epoch = self.date_edit.dateTime().toSecsSinceEpoch()
            self.get_article_list_thread.target_time = (
                datetime.fromtimestamp(time_epoch)
            )
            self.get_article_list_thread.start()
        else:
            self.step_start = False
            self.step_two_btn.setText("开始获取")
            logger.info("停止获取文章列表")
            if self.get_article_list_thread is not None:
                self.get_article_list_thread.stop()
                self.get_article_list_thread.task_over.disconnect()
                self.get_article_list_thread = None

    def step_three_btn_on_click(self):
        """步骤三按钮点击事件"""
        if not self.step_start:
            self.step_start = True
            self.step_three_btn.setText("停止分析")
            logger.info("开始分析文章数据")
            self.analyse_thread = AnalyseThread(self.article_list)
            self.analyse_thread.article_list_persist_ok.connect(self.analyse_thread_article_list_persist_ok)
            try:
                self.analyse_thread.start()
            except AnalyseThreadError as e:
                logger.error("分析失败: %s", e)
                if self.analyse_thread is not None:
                    self.analyse_thread.stop()
        else:
            self.step_start = False
            self.step_three_btn.setText("开始分析")
            logger.info("停止分析文章数据")
            if self.analyse_thread is not None:
                self.analyse_thread.stop()
                self.analyse_thread.article_list_persist_ok.disconnect()
                self.analyse_thread = None
