import os 
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PySide6.QtCore import Qt, QDate

from ui.ui_compiled.main_win import Ui_MainForm
from ui.ui_helper import set_article_confirm_table
from controllers.threads import GetMpBizThread, GetArticleListThread, GetArticleContentThread
from controllers.export import export_to_file
from helpers.config_helper import write_config, del_config, read_config
from helpers.cert_helper import ensure_cert_status
from exceptions import GetArticleContentError

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
        self.export_file_btn_connection = self.export_file_btn.clicked.connect(self.export_file_btn_on_click)
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
        self.get_article_content_thread = None

        # 注册变量
        self.article_list = []

        # 注册弹窗
        self.index_status_msg_box = QMessageBox(parent=self)
        self.index_status_msg_box.setModal(False)
        self.index_status_msg_box.setWindowTitle("推送统计工具提示")
        self.get_biz_msg_box = QMessageBox(parent=self)
        self.get_biz_msg_box.setModal(False)
        self.get_biz_msg_box.setWindowTitle("推送统计工具提示")

        # 检查证书状态
        ensure_cert_status(self)

    # 汇报文章索引事件
    def on_report_index(self, index: int): 
        """汇报文章索引事件"""
        self.index_status_msg_box.setText(
            f"捕获到公众号接口\n开始获取文章列表索引，请耐心等待...\n已获取{index}篇文章"
        )

    def on_flow_got(self, got: bool):
        """获取到公众号接口事件"""
        if got:
            self.index_status_msg_box.setText(
                "捕获到公众号接口\n开始获取文章列表索引，请耐心等待...\n已获取0篇文章"
            )
            self.index_status_msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
            self.index_status_msg_box.setWindowFlags(
                self.index_status_msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
            )
            self.index_status_msg_box.show()
        else:
            self.index_status_msg_box.setText("未获取到文章索引")
            self.index_status_msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    def on_report_progress(self, current: int, total: int, message: str):
        """汇报进度事件：以每篇文章为单位更新进度条和消息"""
        progress_bar = self.progress_bar
        progress_msg = self.progress_msg
        if progress_bar is not None:
            # 首次收到进度时初始化范围
            if progress_bar.minimum() != 0 or progress_bar.maximum() != total:
                progress_bar.setRange(0, total)
            progress_bar.setValue(current)
            # 同时更新百分比显示
            percent = int(current * 100 / total) if total > 0 else 0
            progress_bar.setFormat(f"{current}/{total} ({percent}%)")
        if progress_msg is not None:
            progress_msg.setText(message)

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
        self.get_biz_msg_box.setText(f"已获取到微信公众号BIZ: {biz_result}\n返回本软件进行下一步")
        self.get_biz_msg_box.setWindowFlags(self.get_biz_msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.get_biz_msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

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

        self.step_two_btn.disconnect(self.step_two_btn_connection)

        if len(all_articles) == 0:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("推送统计工具提示")
            msg_box.setText("终止获取")
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            msg_box.exec()

            # 绑定按钮为开始获取按钮
            self.step_two_btn.setText("开始获取")
            self.step_two_btn_connection = self.step_two_btn.clicked.connect(self.step_two_btn_on_click)
            return

        # 写入变量
        self.article_list = all_articles

        # 提示获取到的文章数量
        logger.info("获取到的文章索引: %d", len(all_articles))
        self.index_status_msg_box.setText(f"已获取到的文章索引: 共{len(all_articles)}条。\n单击OK开始分析文章信息。")
        self.index_status_msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        ret = self.index_status_msg_box.exec()
        if ret == QMessageBox.StandardButton.Cancel:
            self.step_two_btn.setText("开始获取")
            self.step_two_btn_connection = self.step_two_btn.clicked.connect(self.step_two_btn_on_click)
            return

        # 进入下一步
        self.go_to_next_step()
        self.start_article_content_crawl()

    def get_article_content_thread_article_list_persist_ok(self):
        """分析线程文章列表写入数据库完成"""
        logger.info("分析线程文章列表写入数据库完成")

    def get_article_content_thread_task_over(self, ok: bool):
        """文章信息获取完成"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("推送统计工具提示")
        if ok:
            set_article_confirm_table(self.article_confirm_table, to_calc_fee=self.to_calc_fee.isChecked())
            self.go_to_next_step()
            msg_box.setText("文章信息获取成功，请返回软件查看文章列表")
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            msg_box.exec()
        else:
            msg_box.setText("文章信息获取失败")
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            msg_box.exec()
            return

    def need_verify(self):
        """需要验证：弹窗仅作提示，用户完成浏览器验证后点击确认即自动继续爬取，不可取消"""
        logger.info("需要验证 - 弹出提示等待用户完成浏览器验证后点击确认")
        msg_box = QMessageBox()
        msg_box.setWindowTitle("推送统计工具提示")
        msg_box.setText("请在弹出的浏览器窗口中完成人机验证，完成后请点击【OK】以继续爬取。")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg_box.exec()

        # 回传信号给爬虫，用户已操作，可继续
        ok = True
        if (self.get_article_content_thread is not None
            and self.get_article_content_thread.crawler is not None):
            self.get_article_content_thread.crawler.signals.verify_done.emit(ok)
            logger.info(f"已向爬虫发出验证完成信号: ok={ok}")


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
        self.step_one_btn_connection = self.step_one_btn.clicked.connect(self.step_one_btn_on_click)

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
            # 步骤三：文章列表加载状态
            pass

    def step_one_btn_on_click(self):
        """步骤一按钮点击事件"""
        if not self.step_start:
            self.step_start = True
            self.step_one_btn.setText("停止获取")
            logger.info("开始获取微信公众号BIZ")
            self.get_biz_msg_box.setText("获取微信公众号BIZ中...\n大概需要三十秒，请耐心等待")
            self.get_biz_msg_box.setWindowFlags(self.get_biz_msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.get_biz_msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
            self.get_biz_msg_box.show()

            self.get_mp_biz_thread = GetMpBizThread()
            self.get_mp_biz_thread.task_over.connect(self.get_mp_biz_task_over)
            self.get_mp_biz_thread.start()
        else:
            self.step_start = False
            self.step_one_btn.setText("开始获取")
            self.get_biz_msg_box.hide()
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
            self.get_article_list_thread.flow_got.connect(self.on_flow_got)
            self.get_article_list_thread.report_index.connect(self.on_report_index)

            time_epoch = self.date_edit.dateTime().toSecsSinceEpoch()
            self.get_article_list_thread.target_time = (
                datetime.fromtimestamp(time_epoch)
            )
            self.get_article_list_thread.start()
        else:
            self.step_start = False
            self.step_two_btn.setText("开始获取")
            self.index_status_msg_box.hide()
            logger.info("停止获取文章列表")
            if self.get_article_list_thread is not None:
                self.get_article_list_thread.stop()
                self.get_article_list_thread.task_over.disconnect()
                self.get_article_list_thread = None

    def start_article_content_crawl(self):
        """开始获取文章内容信息"""
        if not self.step_start:
            self.step_start = True
            logger.info("开始分析文章数据")

            # 重置进度条
            total = len(self.article_list) if self.article_list else 0
            self.progress_bar.setRange(0, total if total > 0 else 1)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(f"0/{total} (0%)" if total > 0 else "等待数据")
            self.progress_msg.setText("正在初始化...")

            self.get_article_content_thread = GetArticleContentThread(self.article_list, self.to_calc_fee.isChecked())
            self.get_article_content_thread.report_progress.connect(self.on_report_progress)
            self.get_article_content_thread.article_list_persist_ok.connect(
                self.get_article_content_thread_article_list_persist_ok
            )
            self.get_article_content_thread.need_user_verify.connect(self.need_verify) # 连接人机验证信号（线程一启动后，crawler创建即转发到此信号）
            self.get_article_content_thread.task_over.connect(self.get_article_content_thread_task_over) # 连接任务完成信号

            try:
                self.get_article_content_thread.start()
            except GetArticleContentError as e:
                logger.error("分析失败: %s", e)
                self.step_start = False
                if self.get_article_content_thread is not None:
                    self.get_article_content_thread.stop()
                    self.get_article_content_thread = None
                msg_box = QMessageBox()
                msg_box.setWindowTitle("推送统计工具提示")
                msg_box.setText(f"分析失败: {e}")
                msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
                msg_box.exec()

    def export_file_btn_on_click(self):
        """导出文件按钮点击事件"""
        logger.info("导出文件")
        if self.to_calc_fee.isChecked():
            # 先计算稿费
            ...

        # 读取上次选择的导出目录，作为文件夹选择器的初始目录
        last_export_dir = read_config("last_export_dir", "") or ""

        # 弹出文件夹选择器，定位到上次选择的目录
        folder_str = QFileDialog.getExistingDirectory(
            self,
            "选择导出文件夹",
            last_export_dir
        )
        if not folder_str:
            return
        folder_path = Path(folder_str)

        # 记录本次选择的目录，下次导出时默认定位到这里
        write_config({"last_export_dir": folder_str})

        export_to_file(folder_path, to_calc_fee=self.to_calc_fee.isChecked())
        msg_box = QMessageBox()
        msg_box.setWindowTitle("导出提示")
        msg_box.setText("导出完成")
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg_box.exec()

        # 打开文件夹
        os.startfile(folder_path)