"""UI组件模块"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from ui.ui_compiled.main_win import Ui_MainForm


class MainWindow(QWidget, Ui_MainForm):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 1. 设置窗口标志：无边框
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 2. 设置背景透明（必须和无边框一起用）
        self.setupUi(self)

        # 连接按钮点击事件
        self.close_win_btn.clicked.connect(self.close_win_btn_on_click)
        self.minimize_win_btn.clicked.connect(self.minimize_win_btn_on_click)

        # 用于拖动窗口
        self.m_drag = False
        self.m_drag_position = None

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
