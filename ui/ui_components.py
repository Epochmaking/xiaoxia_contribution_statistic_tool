import os 
import sys
import subprocess
import ctypes
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PySide6.QtCore import Qt, QDate, QPropertyAnimation, QRect, QEasingCurve

from ui.ui_compiled.main_win import Ui_MainForm
from ui.ui_setting_components import SettingWindow
from ui.ui_helper import set_article_confirm_table, apply_frame_shadow
from controllers.threads import GetMpBizThread, GetArticleListThread, GetArticleContentThread
from controllers.analyse import calculate_fee
from controllers.export import export_to_file
from helpers.config_helper import write_config, del_config, read_config
from helpers.cert_helper import ensure_cert_status
from exceptions import GetArticleContentError

import constants as consts
from utils.logging import get_logger


logger = get_logger(__name__)

# Win32 ShowWindow 常量
SW_SHOW = 5
SW_RESTORE = 9

class MainWindow(QWidget, Ui_MainForm):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.setting_window = SettingWindow(parent=None)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 1. 设置窗口标志：无边框
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 2. 设置背景透明（必须和无边框一起用）
        self.setupUi(self)
        apply_frame_shadow(self.MainFrame, self.horizontalLayout_3)
        self.stackedWidget.setCurrentIndex(0) # 3. 初始化显示步骤一
        self.date_edit.setDate(QDate.currentDate())

        # 连接按钮点击事件
        self.close_win_btn.clicked.connect(self.close_win_btn_on_click)
        self.minimize_win_btn.clicked.connect(self.minimize_win_btn_on_click)
        self.step_one_btn_connection = self.step_one_btn.clicked.connect(self.step_one_btn_on_click)
        self.step_two_btn_connection = self.step_two_btn.clicked.connect(self.step_two_btn_on_click)
        self.export_file_btn_connection = self.export_file_btn.clicked.connect(self.export_file_btn_on_click)
        self.reget_biz_btn_connection = self.reget_biz_btn.clicked.connect(self.reget_biz_btn_on_click)
        self.setting_btn_connection = self.setting_btn.clicked.connect(self.setting_btn_on_click)

        # 初始化显示已获取的BIZ
        if consts.MP_BIZ:
            self.biz_display_label.setText(consts.MP_BIZ)
            self.reget_biz_btn.setVisible(True)
            consts.ARTICLE_LIST_URL = consts.ARTICLE_LIST_URL_TEMPLATE.format(biz=consts.MP_BIZ)
            # 绑定按钮为下一步按钮
            self.step_one_btn.setText("下一步")
            self.step_one_started = False
            self.step_one_btn.disconnect(self.step_one_btn_connection)
            self.step_one_btn_connection = self.step_one_btn.clicked.connect(self.go_to_next_step)
        else:
            self.reget_biz_btn.setVisible(False)

        # 用于拖动窗口
        self.m_drag = False
        self.m_drag_position = None

        # 最小化/还原动画相关状态
        self._min_anim = None
        self._min_opacity_anim = None
        self._restore_anim = None
        self._restore_opacity_anim = None
        self._saved_geometry = None
        self._is_restoring = False

        # 各步骤的运行状态标志（独立管理，避免互相干扰）
        self.step_one_started = False
        self.step_two_started = False
        self.article_content_started = False

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

        # 检查是否是第一次打开软件
        if consts.FIRST_OPEN:
            self.first_open_message()

    def _make_msg_box(self, title: str = "推送统计工具提示", on_top: bool = True,
                      buttons=QMessageBox.StandardButton.Ok, modal: bool = True) -> QMessageBox:
        """创建消息框的工厂方法，统一设置标题、置顶、按钮等公共属性"""
        box = QMessageBox(parent=self)
        box.setWindowTitle(title)
        if on_top:
            box.setWindowFlags(box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        box.setStandardButtons(buttons)
        if not modal:
            box.setModal(False)
        return box

    def _stop_thread(self, thread, signal_names: list[str] | None = None):
        """统一停止线程并断开信号连接"""
        if thread is None:
            return
        if signal_names:
            for sig_name in signal_names:
                try:
                    getattr(thread, sig_name).disconnect()
                except (TypeError, RuntimeError):
                    pass
        try:
            thread.stop()
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("停止线程失败")

    @staticmethod
    def _open_folder(path: Path):
        """跨平台打开文件夹"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("打开文件夹失败: %s", path)

    def first_open_message(self):
        """第一次打开软件提示用户配置"""
        write_config({"first_open": "0"})
        msg_box = self._make_msg_box()
        msg_box.setText("这是第一次打开软件，请打开设置配置小夏成员名单。")
        msg_box.show()

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
        self._stop_thread(self.get_mp_biz_thread, ["task_over"])
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
        self.step_one_started = False
        self.step_one_btn.disconnect(self.step_one_btn_connection)
        self.step_one_btn_connection = self.step_one_btn.clicked.connect(self.go_to_next_step)

    # 步骤二任务完成
    def get_article_list_task_over(self, all_articles: list[dict]):
        """步骤二任务完成"""
        # 停止线程并断开所有信号槽连接
        self._stop_thread(self.get_article_list_thread, ["task_over", "flow_got", "report_index"])
        self.get_article_list_thread = None

        self.step_two_started = False

        self.step_two_btn.disconnect(self.step_two_btn_connection)

        if len(all_articles) == 0:
            msg_box = self._make_msg_box()
            msg_box.setText("终止获取")
            msg_box.exec()

            # 绑定按钮为开始获取按钮
            self.step_two_btn.setText("开始获取")
            self.step_two_btn_connection = self.step_two_btn.clicked.connect(self.step_two_btn_on_click)
            return

        # 写入变量
        self.article_list = all_articles

        # 提示获取到的文章数量
        logger.info("获取到的文章索引: %d", len(all_articles))
        # 先清除置顶标志再彻底关闭 msgbox，避免置顶残留影响
        self.index_status_msg_box.setWindowFlags(
            self.index_status_msg_box.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
        )
        self.index_status_msg_box.close()

        # 强制主窗口到前台显示（处理无边框窗口在 Windows 上 raise_ 失效的问题）
        if sys.platform == "win32":
            try:
                hwnd = int(self.winId())
                # 先恢复窗口（若被最小化）
                ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
                # 再显示并强制激活到前台
                ctypes.windll.user32.ShowWindow(hwnd, SW_SHOW)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                ctypes.windll.user32.BringWindowToTop(hwnd)
            except Exception as ex:  # pylint: disable=broad-exception-caught
                logger.warning("Win32 强制前台失败，退回 Qt 原生方法: %s", ex)
                self.showNormal()
                self.raise_()
                self.activateWindow()
        else:
            self.showNormal()
            self.raise_()
            self.activateWindow()

        # 进入下一步
        self.go_to_next_step()
        self.start_article_content_crawl()

    def get_article_content_thread_article_list_persist_ok(self):
        """分析线程文章列表写入数据库完成"""
        logger.info("分析线程文章列表写入数据库完成")

    def get_article_content_thread_task_over(self, ok: bool):
        """文章信息获取完成"""
        self.article_content_started = False
        msg_box = self._make_msg_box()
        if ok:
            set_article_confirm_table(self.article_confirm_table, to_calc_fee=self.to_calc_fee.isChecked())
            self.go_to_next_step()
            msg_box.setText("文章信息获取成功，请返回软件查看文章列表")
            msg_box.exec()
        else:
            msg_box.setText("文章信息获取失败")
            msg_box.exec()

    def need_verify(self):
        """需要验证：弹窗仅作提示，用户完成浏览器验证后点击确认即自动继续爬取，不可取消"""
        logger.info("需要验证 - 弹出提示等待用户完成浏览器验证后点击确认")
        msg_box = self._make_msg_box(buttons=QMessageBox.StandardButton.Ok)
        msg_box.setText("请在弹出的浏览器窗口中完成人机验证，完成后请点击【OK】以继续爬取。")
        msg_box.exec()

        # 回传信号给爬虫，用户已操作，可继续
        if (self.get_article_content_thread is not None
            and self.get_article_content_thread.crawler is not None):
            self.get_article_content_thread.crawler.signals.verify_done.emit(True)
            logger.info("已向爬虫发出验证完成信号")


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

    def closeEvent(self, event):
        """关闭事件：主窗口退出时一并关闭设置窗口和清理运行中的线程"""
        try:
            # 关闭设置窗口
            if hasattr(self, 'setting_window') and self.setting_window is not None:
                try:
                    self.setting_window.close()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
                self.setting_window = None

            # 停止可能仍在运行的三个线程
            self._stop_thread(self.get_article_content_thread)
            self.get_article_content_thread = None
            self._stop_thread(self.get_article_list_thread)
            self.get_article_list_thread = None
            self._stop_thread(self.get_mp_biz_thread)
            self.get_mp_biz_thread = None

            # 停止可能仍在运行的最小化/还原动画
            for anim in (self._min_anim, self._min_opacity_anim,
                         self._restore_anim, self._restore_opacity_anim):
                if anim is not None:
                    anim.stop()
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        finally:
            event.accept()

    # pylint: enable=invalid-name

    def close_win_btn_on_click(self):
        """关闭按钮点击事件"""
        self.close()

    def minimize_win_btn_on_click(self):
        """最小化按钮点击事件：带动画收缩到任务栏"""
        # 保存当前窗口几何信息，还原时用
        self._saved_geometry = self.geometry()

        # 计算目标收缩点：屏幕底部中央的一个小矩形
        screen = self.screen().availableGeometry()
        target_rect = QRect(
            screen.center().x() - 15,
            screen.bottom() - 8,
            30,
            8
        )

        # geometry 收缩动画
        self._min_anim = QPropertyAnimation(self, b"geometry")
        self._min_anim.setDuration(220)
        self._min_anim.setStartValue(self.geometry())
        self._min_anim.setEndValue(target_rect)
        self._min_anim.setEasingCurve(QEasingCurve.Type.InBack)

        # opacity 淡出动画（配合收缩更自然）
        self._min_opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self._min_opacity_anim.setDuration(200)
        self._min_opacity_anim.setStartValue(1.0)
        self._min_opacity_anim.setEndValue(0.0)
        self._min_opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 动画结束后真正最小化，并恢复透明度以便还原时使用
        self._min_anim.finished.connect(self._on_minimize_anim_finished)
        self._min_anim.start()
        self._min_opacity_anim.start()

    def _on_minimize_anim_finished(self):
        """最小化动画结束：真正最小化窗口并恢复透明度"""
        self.setWindowOpacity(1.0)
        self.showMinimized()

    def changeEvent(self, event):
        """监听窗口状态变化，在从最小化还原时播放动画"""
        if event.type() == event.Type.WindowStateChange:
            old_state = event.oldState()
            new_state = self.windowState()
            # 从最小化状态恢复到正常状态时播放还原动画
            if (old_state & Qt.WindowState.WindowMinimized and
                    not (new_state & Qt.WindowState.WindowMinimized) and
                    not self._is_restoring):
                self._play_restore_animation()
        super().changeEvent(event)

    def _play_restore_animation(self):
        """播放还原动画：从任务栏小点展开到原位置并淡入"""
        self._is_restoring = True

        saved = self._saved_geometry or self.geometry()
        screen = self.screen().availableGeometry()
        start_rect = QRect(
            screen.center().x() - 15,
            screen.bottom() - 8,
            30,
            8
        )

        # showNormal 会瞬间恢复原位，所以先把窗口放到起始点
        self.showNormal()
        self.setGeometry(start_rect)
        self.setWindowOpacity(0.0)

        # geometry 展开动画
        self._restore_anim = QPropertyAnimation(self, b"geometry")
        self._restore_anim.setDuration(240)
        self._restore_anim.setStartValue(start_rect)
        self._restore_anim.setEndValue(saved)
        self._restore_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self._restore_anim.finished.connect(self._on_restore_anim_finished)

        # opacity 淡入动画
        self._restore_opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self._restore_opacity_anim.setDuration(220)
        self._restore_opacity_anim.setStartValue(0.0)
        self._restore_opacity_anim.setEndValue(1.0)
        self._restore_opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._restore_anim.start()
        self._restore_opacity_anim.start()

    def _on_restore_anim_finished(self):
        """还原动画结束：清除标志位"""
        self._is_restoring = False

    def reget_biz_btn_on_click(self):
        """重新获取按钮点击事件"""
        consts.MP_BIZ = None
        del_config("mp_id")
        self.biz_display_label.setText("无")
        self.reget_biz_btn.setVisible(False)
        self.step_one_btn.setText("开始获取")
        self.step_one_started = False
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
            if consts.ARTICLE_LIST_URL is None:
                logger.error("文章列表URL未设置，无法进入步骤二")
                return
            self.article_list_url.setText(consts.ARTICLE_LIST_URL)
            self.article_list_url.setSelection(0, len(self.article_list_url.text()))
        if next_index == 2:
            # 步骤三：文章列表加载状态
            pass

    def step_one_btn_on_click(self):
        """步骤一按钮点击事件"""
        if not self.step_one_started:
            self.step_one_started = True
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
            self.step_one_started = False
            self.step_one_btn.setText("开始获取")
            self.get_biz_msg_box.hide()
            logger.info("停止获取微信公众号BIZ")
            self._stop_thread(self.get_mp_biz_thread, ["task_over"])
            self.get_mp_biz_thread = None

    def step_two_btn_on_click(self):
        """步骤二按钮点击事件"""
        if not self.step_two_started:
            self.step_two_started = True
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
            self.step_two_started = False
            self.step_two_btn.setText("开始获取")
            self.index_status_msg_box.hide()
            logger.info("停止获取文章列表")
            self._stop_thread(self.get_article_list_thread, ["task_over", "flow_got", "report_index"])
            self.get_article_list_thread = None

    def start_article_content_crawl(self):
        """开始获取文章内容信息"""
        if not self.article_content_started:
            self.article_content_started = True
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
                self.article_content_started = False
                self._stop_thread(self.get_article_content_thread)
                self.get_article_content_thread = None
                msg_box = self._make_msg_box()
                msg_box.setText(f"分析失败: {e}")
                msg_box.exec()

    def export_file_btn_on_click(self):
        """导出文件按钮点击事件"""
        logger.info("导出文件")
        if self.to_calc_fee.isChecked():
            # 先计算稿费
            calculate_fee()

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
        msg_box = self._make_msg_box(title="导出提示")
        msg_box.setText("导出完成")
        msg_box.exec()

        # 打开文件夹
        self._open_folder(folder_path)

    def setting_btn_on_click(self):
        """设置按钮点击事件"""
        if self.setting_window is None:
            return
        logger.info("打开设置")
        self.setting_window.show_config_values()
        self.setting_window.show()