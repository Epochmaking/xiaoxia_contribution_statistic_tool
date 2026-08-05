from PySide6.QtWidgets import QWidget, QMessageBox, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QIntValidator, QDoubleValidator, QRegularExpressionValidator,
    QSyntaxHighlighter, QTextCharFormat, QColor,
)
from PySide6.QtCore import QRegularExpression

from ui.ui_compiled.setting_win import Ui_Form
from helpers.config_helper import read_config, write_config

from utils.logging import get_logger

logger = get_logger(__name__)


# 中文 Unicode 范围：构建真实字符区间字符串（避免 Qt 正则不识别 \uXXXX 写法）
_HAN_START = chr(0x4E00)
_HAN_END = chr(0x9FA5)
# 合法字符集合的正则模式（Qt 正则引擎直接吃真实的中文字符）
_MEMBERS_LEGAL_PATTERN = (
    f"[^"
    f"{_HAN_START}-{_HAN_END}"  # 中文区间（由真实字符构成）
    f"A-Za-z0-9"                # 英文数字
    f",，;；、"                   # 中英文逗号分号顿号
    f"·"                        # 中文·号
    r"\s"                       # 空白字符（Qt 正则识别 \s）
    r"\n"                       # 换行符
    f"]"
)


class MembersSyntaxHighlighter(QSyntaxHighlighter):
    """小夏成员名单(QTextEdit)自定义语法高亮：把非法字符用红色背景标出"""

    def __init__(self, document):
        super().__init__(document)
        self._err_fmt = QTextCharFormat()
        self._err_fmt.setBackground(QColor(255, 100, 100, 180))
        # 非法字符 = 不在"中文/英文/数字/中英文逗号分号/空白字符"范围内的任意字符
        self._illegal_re = QRegularExpression(_MEMBERS_LEGAL_PATTERN)

    def highlightBlock(self, text: str):  # pylint: disable=invalid-name
        it = self._illegal_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self._err_fmt)

class SettingWindow(QWidget, Ui_Form):
    """设置窗口类"""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 1. 设置窗口标志：无边框
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 2. 设置背景透明（必须和无边框一起用）
        self.setupUi(self)
        self._setup_validators()

        # 用于拖动窗口
        self.m_drag = False
        self.m_drag_position = None

        # 注册按钮点击事件
        self.cancel_btn.clicked.connect(self.close)
        self.apply_btn.clicked.connect(self.apply_settings)
        self.set_default_btn.clicked.connect(self.set_default_settings)

        # 显示配置值
        self.show_config_values()

    def _setup_validators(self):
        """
        根据配置参数类型为每个控件设置输入验证：
        - QLineEdit 使用 Qt 内置 Validator（阻止非法字符输入）
        - QTextEdit xiaoxia_members 使用 SyntaxHighlighter 把非法字符高亮标出
        """
        # --- int 类型：端口、重试次数、文章数、稿费基数 ---
        port_validator = QIntValidator(1, 65535, self)
        self.listen_port.setValidator(port_validator)

        pos_int_validator = QIntValidator(0, 999999, self)
        self.max_retries.setValidator(pos_int_validator)
        self.max_article_count_per_request.setValidator(QIntValidator(1, 10, self))
        self.max_llm_retries.setValidator(pos_int_validator)
        self.fee_base.setValidator(QIntValidator(0, 999999, self))

        # --- float 类型：超时、请求间隔 ---
        pos_float_validator = QDoubleValidator(0.0, 999999.0, 6, self)
        pos_float_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.max_timeout_s.setValidator(pos_float_validator)
        self.fetch_interval_s.setValidator(pos_float_validator)
        self.llm_fetch_interval_s.setValidator(pos_float_validator)

        # --- 字符串类型：模型名（允许字母、数字、点、短横线、下划线）---
        model_re = QRegularExpression(r"^[A-Za-z0-9._\-]*$")
        model_validator = QRegularExpressionValidator(model_re, self)
        self.glm_model.setValidator(model_validator)
        self.glm_backup_model.setValidator(model_validator)

        # --- API Key：允许字母数字点号等常见字符 ---
        apikey_re = QRegularExpression(r"^[A-Za-z0-9._\-]*$")
        self.glm_api_key.setValidator(QRegularExpressionValidator(apikey_re, self))

        # --- QTextEdit：xiaoxia_members（QTextEdit 没有 setValidator，用 SyntaxHighlighter 高亮非法字符）---
        assert isinstance(self.xiaoxia_members, QTextEdit), "xiaoxia_members 必须是 QTextEdit 类型"
        self._members_highlighter = MembersSyntaxHighlighter(self.xiaoxia_members.document())
        self.xiaoxia_members.setPlaceholderText(
            "用于区分稿费，成员之间用逗号分隔。例如：张火火,曾浣浣"
        )

    def show_config_values(self):
        """显示配置值"""
        self.listen_port.setText(str(read_config("listen_port")))
        self.max_timeout_s.setText(str(read_config("max_timeout_s")))
        self.max_retries.setText(str(read_config("max_retries")))
        self.fetch_interval_s.setText(str(read_config("fetch_interval_s")))
        self.max_article_count_per_request.setText(str(read_config("max_article_count_per_request")))
        self.max_llm_retries.setText(str(read_config("max_llm_retries")))
        self.llm_fetch_interval_s.setText(str(read_config("llm_fetch_interval_s")))
        self.glm_model.setText(read_config("glm_model"))
        self.glm_backup_model.setText(read_config("glm_backup_model"))
        self.fee_base.setText(str(read_config("fee_base")))
        self.glm_api_key.setText(read_config("glm_api_key"))
        # QTextEdit 使用 setPlainText / toPlainText，而非 setText / text
        members_val = read_config("xiaoxia_members", "") or ""
        self.xiaoxia_members.setPlainText(members_val)

    def _get_widget_text(self, widget) -> str:
        """统一的取值辅助函数：自动区分 QLineEdit 和 QTextEdit"""
        if isinstance(widget, QTextEdit):
            return widget.toPlainText().strip()
        return widget.text().strip()

    def apply_settings(self):
        """应用设置：校验输入合法性 → 写入配置文件"""
        logger.info("应用设置")

        # 小夏成员名单(QTextEdit)：先单独做非法字符检查
        members_text = self.xiaoxia_members.toPlainText()
        members_re = QRegularExpression(_MEMBERS_LEGAL_PATTERN)
        if members_re.isValid():
            illegal_match = members_re.match(members_text)
            if illegal_match.hasMatch():
                bad_char = illegal_match.captured(0)
                QMessageBox.warning(
                    self, "小夏成员名单含非法字符",
                    f"检测到非法字符【{bad_char}】，\n仅允许中文、英文、数字和中英文逗号/分号分隔符。"
                )
                self.xiaoxia_members.setFocus()
                return

        # 字段必填/合法性校验
        validations = [
            (self.listen_port, "监听端口", True, "int"),
            (self.max_timeout_s, "最大超时时间", True, "float"),
            (self.max_retries, "最大重试次数", True, "int"),
            (self.fetch_interval_s, "请求间隔", True, "float"),
            (self.max_article_count_per_request, "每次请求文章数", True, "int"),
            (self.max_llm_retries, "LLM最大重试次数", True, "int"),
            (self.llm_fetch_interval_s, "LLM请求间隔", True, "float"),
            (self.glm_model, "首选模型", True, "str"),
            (self.glm_backup_model, "备选模型", False, "str"),
            (self.fee_base, "稿费基数", True, "int"),
            (self.glm_api_key, "GLM API Key", True, "str"),
            (self.xiaoxia_members, "小夏成员名单", False, "str"),
        ]

        for widget, name, required, typ in validations:
            text = self._get_widget_text(widget)
            if required and not text:
                QMessageBox.warning(self, "配置项不完整", f"请填写【{name}】")
                widget.setFocus()
                return
            if not text:
                continue
            if typ == "int":
                try:
                    int(text)
                except ValueError:
                    QMessageBox.warning(self, "配置项格式错误", f"【{name}】必须是整数")
                    widget.setFocus()
                    return
            elif typ == "float":
                try:
                    float(text)
                except ValueError:
                    QMessageBox.warning(self, "配置项格式错误", f"【{name}】必须是数字")
                    widget.setFocus()
                    return

        # 全部校验通过，写入配置
        config_kv = {
            "listen_port": self._get_widget_text(self.listen_port),
            "max_timeout_s": self._get_widget_text(self.max_timeout_s),
            "max_retries": self._get_widget_text(self.max_retries),
            "fetch_interval_s": self._get_widget_text(self.fetch_interval_s),
            "max_article_count_per_request": self._get_widget_text(self.max_article_count_per_request),
            "max_llm_retries": self._get_widget_text(self.max_llm_retries),
            "llm_fetch_interval_s": self._get_widget_text(self.llm_fetch_interval_s),
            "glm_model": self._get_widget_text(self.glm_model),
            "glm_backup_model": self._get_widget_text(self.glm_backup_model),
            "fee_base": self._get_widget_text(self.fee_base),
            "glm_api_key": self._get_widget_text(self.glm_api_key),
            "xiaoxia_members": (self._get_widget_text(self.xiaoxia_members)
                                .replace(r"\n", ",").replace("，", ",").replace("、", ",")
                                .replace(";", ",")).replace("；", ","),
        }
        try:
            write_config(config_kv)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            logger.error(f"写入配置失败: {ex}")
            QMessageBox.critical(self, "写入配置失败", str(ex))
            return

        msg = QMessageBox.information(self, "设置已保存", "配置已保存，请重启本软件以应用设置！", QMessageBox.StandardButton.Ok)
        if msg == QMessageBox.StandardButton.Ok:
            self.close()

    def set_default_settings(self):
        """恢复默认设置（与 constants.py 的 DEFAULT_CONFIG 保持一致）"""
        logger.info("恢复默认设置")
        defaults = {
            "listen_port": "8082",
            "max_article_count_per_request": "10",
            "max_timeout_s": "6",
            "max_retries": "3",
            "fetch_interval_s": "2",
            "max_llm_retries": "99",
            "llm_fetch_interval_s": "1.5",
            "glm_api_key": "00ebdd968b7742babfa0a6e04b33a0e4.ZrdN0x9z5M5dbNsq",
            "glm_model": "glm-4.7",
            "glm_backup_model": "glm-5",
            "xiaoxia_members": "",
            "fee_base": "100",
        }
        self.listen_port.setText(defaults["listen_port"])
        self.max_article_count_per_request.setText(defaults["max_article_count_per_request"])
        self.max_timeout_s.setText(defaults["max_timeout_s"])
        self.max_retries.setText(defaults["max_retries"])
        self.fetch_interval_s.setText(defaults["fetch_interval_s"])
        self.max_llm_retries.setText(defaults["max_llm_retries"])
        self.llm_fetch_interval_s.setText(defaults["llm_fetch_interval_s"])
        self.glm_api_key.setText(defaults["glm_api_key"])
        self.glm_model.setText(defaults["glm_model"])
        self.glm_backup_model.setText(defaults["glm_backup_model"])
        # QTextEdit 使用 setPlainText
        self.xiaoxia_members.setPlainText(defaults["xiaoxia_members"])
        self.fee_base.setText(defaults["fee_base"])

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