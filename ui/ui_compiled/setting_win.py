# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setting_win.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)
from . import ui_res_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(666, 584)
        icon = QIcon()
        icon.addFile(u":/icons/xiaoxia", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Form.setWindowIcon(icon)
        Form.setStyleSheet(u"border: none;")
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.setting_frame = QFrame(Form)
        self.setting_frame.setObjectName(u"setting_frame")
        self.setting_frame.setAutoFillBackground(False)
        self.setting_frame.setStyleSheet(u"QFrame {\n"
"	background-color: rgb(85, 85, 85);\n"
"	border-radius: 15px;\n"
"}")
        self.setting_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.setting_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.setting_frame)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.setting_frame)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid #888888;\n"
"    border-radius: 8px;\n"
"    background-color: #ffffff;\n"
"    padding: 1px;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QLabel {\n"
"	font-size: 16px;\n"
"	color: rgb(255, 255, 255);\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.title_bar = QWidget(self.widget)
        self.title_bar.setObjectName(u"title_bar")
        self.title_bar.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_13 = QHBoxLayout(self.title_bar)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(-1, 9, -1, 0)
        self.label_14 = QLabel(self.title_bar)
        self.label_14.setObjectName(u"label_14")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setMaximumSize(QSize(16777215, 40))
        font = QFont()
        self.label_14.setFont(font)
        self.label_14.setStyleSheet(u"color: rgb(255, 255, 255)")

        self.horizontalLayout_13.addWidget(self.label_14, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_2.addWidget(self.title_bar)

        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setStyleSheet(u"")
        self.gridLayout = QGridLayout(self.widget_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(30)
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setContentsMargins(15, -1, 15, -1)
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_11 = QLabel(self.widget_2)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_10.addWidget(self.label_11)

        self.glm_backup_model = QLineEdit(self.widget_2)
        self.glm_backup_model.setObjectName(u"glm_backup_model")
        self.glm_backup_model.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_10.addWidget(self.glm_backup_model)


        self.gridLayout.addLayout(self.horizontalLayout_10, 4, 1, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_4 = QLabel(self.widget_2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_3.addWidget(self.label_4)

        self.max_timeout_s = QLineEdit(self.widget_2)
        self.max_timeout_s.setObjectName(u"max_timeout_s")
        self.max_timeout_s.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_3.addWidget(self.max_timeout_s)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_5 = QLabel(self.widget_2)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_4.addWidget(self.label_5)

        self.max_retries = QLineEdit(self.widget_2)
        self.max_retries.setObjectName(u"max_retries")
        self.max_retries.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_4.addWidget(self.max_retries)


        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_9 = QLabel(self.widget_2)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_8.addWidget(self.label_9)

        self.llm_fetch_interval_s = QLineEdit(self.widget_2)
        self.llm_fetch_interval_s.setObjectName(u"llm_fetch_interval_s")
        self.llm_fetch_interval_s.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_8.addWidget(self.llm_fetch_interval_s)


        self.gridLayout.addLayout(self.horizontalLayout_8, 3, 1, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_10 = QLabel(self.widget_2)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_9.addWidget(self.label_10)

        self.glm_model = QLineEdit(self.widget_2)
        self.glm_model.setObjectName(u"glm_model")
        self.glm_model.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_9.addWidget(self.glm_model)


        self.gridLayout.addLayout(self.horizontalLayout_9, 4, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_7 = QLabel(self.widget_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_6.addWidget(self.label_7)

        self.max_llm_retries = QLineEdit(self.widget_2)
        self.max_llm_retries.setObjectName(u"max_llm_retries")
        self.max_llm_retries.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_6.addWidget(self.max_llm_retries)


        self.gridLayout.addLayout(self.horizontalLayout_6, 2, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.widget_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.max_article_count_per_request = QLineEdit(self.widget_2)
        self.max_article_count_per_request.setObjectName(u"max_article_count_per_request")
        self.max_article_count_per_request.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_2.addWidget(self.max_article_count_per_request)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_6 = QLabel(self.widget_2)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_5.addWidget(self.label_6)

        self.fetch_interval_s = QLineEdit(self.widget_2)
        self.fetch_interval_s.setObjectName(u"fetch_interval_s")
        self.fetch_interval_s.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_5.addWidget(self.fetch_interval_s)


        self.gridLayout.addLayout(self.horizontalLayout_5, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.widget_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.listen_port = QLineEdit(self.widget_2)
        self.listen_port.setObjectName(u"listen_port")
        self.listen_port.setMaximumSize(QSize(100, 30))

        self.horizontalLayout.addWidget(self.listen_port)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_8 = QLabel(self.widget_2)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_7.addWidget(self.label_8)

        self.fee_base = QLineEdit(self.widget_2)
        self.fee_base.setObjectName(u"fee_base")
        self.fee_base.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_7.addWidget(self.fee_base)


        self.gridLayout.addLayout(self.horizontalLayout_7, 3, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.widget_2)

        self.widget_3 = QWidget(self.widget)
        self.widget_3.setObjectName(u"widget_3")
        self.gridLayout_3 = QGridLayout(self.widget_3)
        self.gridLayout_3.setSpacing(20)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(15, -1, 15, -1)
        self.glm_api_key = QLineEdit(self.widget_3)
        self.glm_api_key.setObjectName(u"glm_api_key")

        self.gridLayout_3.addWidget(self.glm_api_key, 0, 1, 1, 1)

        self.label_12 = QLabel(self.widget_3)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_3.addWidget(self.label_12, 0, 0, 1, 1)

        self.label_13 = QLabel(self.widget_3)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_3.addWidget(self.label_13, 1, 0, 1, 1)

        self.xiaoxia_members = QTextEdit(self.widget_3)
        self.xiaoxia_members.setObjectName(u"xiaoxia_members")
        self.xiaoxia_members.setStyleSheet(u"QTextEdit {\n"
"border: 1px solid #888888;\n"
"border-radius: 8px; /* \u5916\u5c42\u5706\u89d2 */\n"
"background-color: #ffffff;\n"
"padding: 2px;\n"
"font-size: 14px;\n"
"}\n"
"\n"
"QTextEdit QWidget#qt_scrollarea_viewport {\n"
"background-color: rgb(255, 255, 255);\n"
"border-radius: 8px; \n"
"}\n"
"\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761\u6574\u4f53 */\n"
"        QTextEdit QScrollBar:vertical {\n"
"            background-color: #F7F8FA;\n"
"            width: 10px;\n"
"            margin: 0px 0px 0px 0px;\n"
"        }\n"
"\n"
"        /* \u6eda\u52a8\u6761\u6ed1\u5757\uff08\u672a\u6309\u4e0b\uff09 */\n"
"        QTextEdit QScrollBar::handle:vertical {\n"
"            background-color: #C8CCD1;\n"
"            min-height: 20px;\n"
"            min-width: 20px;\n"
"            border-radius: 5px;\n"
"            margin: 2px 2px 2px 2px;\n"
"        }\n"
"        /* \u6eda\u52a8\u6761\u6ed1\u5757\uff08\u9f20\u6807\u60ac\u6d6e\uff09 */\n"
"        QTextEdit QScrollBar::handle:vertical:hover {\n"
"            b"
                        "ackground-color: #A8ADB5;\n"
"        }\n"
"        /* \u6eda\u52a8\u6761\u6ed1\u5757\uff08\u6309\u4e0b\uff09 */\n"
"        QTextEdit QScrollBar::handle:vertical:pressed {\n"
"            background-color: #8D9299;\n"
"        }\n"
"        /* \u6eda\u52a8\u6761\u4e0a\u4e0b/\u5de6\u53f3\u7bad\u5934\u6309\u94ae */\n"
"        QTextEdit QScrollBar::add-line:vertical,\n"
"        QTextEdit QScrollBar::sub-line:vertical{\n"
"            background: none;\n"
"            width: 0px;\n"
"            height: 0px;\n"
"        }\n"
"        /* \u6eda\u52a8\u6761\u4e24\u7aef\u7684\u7a7a\u767d\u533a\u57df\uff08\u70b9\u51fb\u53ef\u4ee5\u8df3\u8f6c\uff09 */\n"
"        QTextEdit QScrollBar::add-page:vertical,\n"
"        QTextEdit QScrollBar::sub-page:vertical{\n"
"            background-color: #F7F8FA;\n"
"        }")

        self.gridLayout_3.addWidget(self.xiaoxia_members, 1, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.widget_3)

        self.widget_4 = QWidget(self.widget)
        self.widget_4.setObjectName(u"widget_4")
        self.widget_4.setStyleSheet(u"QPushButton {\n"
"	background: rgb(6, 173, 86);\n"
"	color: rgb(255, 255, 255);\n"
"	border-radius: 8px;\n"
"	font-size: 14px;\n"
"}\n"
"QPushButton:hover {\n"
"	background: rgb(6, 156, 76);\n"
"}")
        self.horizontalLayout_12 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_12.setSpacing(30)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(40, -1, 40, -1)
        self.cancel_btn = QPushButton(self.widget_4)
        self.cancel_btn.setObjectName(u"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0, 30))
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_12.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton(self.widget_4)
        self.apply_btn.setObjectName(u"apply_btn")
        self.apply_btn.setMinimumSize(QSize(0, 30))
        self.apply_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_12.addWidget(self.apply_btn)

        self.set_default_btn = QPushButton(self.widget_4)
        self.set_default_btn.setObjectName(u"set_default_btn")
        self.set_default_btn.setMinimumSize(QSize(0, 30))
        self.set_default_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_12.addWidget(self.set_default_btn)


        self.verticalLayout_2.addWidget(self.widget_4)


        self.verticalLayout_4.addWidget(self.widget)


        self.verticalLayout.addWidget(self.setting_frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"\u5907\u9009\u5927\u8bed\u8a00\u6a21\u578b", None))
#if QT_CONFIG(tooltip)
        self.glm_backup_model.setToolTip(QCoreApplication.translate("Form", u"\u667a\u8c31\u6e05\u8a00\u5907\u9009\u5927\u8bed\u8a00\u6a21\u578b", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("Form", u"\u6700\u5927\u8d85\u65f6(\u79d2)", None))
#if QT_CONFIG(tooltip)
        self.max_timeout_s.setToolTip(QCoreApplication.translate("Form", u"\u6700\u5927\u5141\u8bb8\u7684\u7f51\u7edc\u5ef6\u8fdf\u8d85\u65f6\u65f6\u95f4\n"
"\u8d85\u8fc7\u6b64\u65f6\u95f4\u5219\u5224\u5b9a\u4e3a\u8bf7\u6c42\u5931\u8d25", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("Form", u"\u6700\u5927\u8bf7\u6c42\u91cd\u8bd5\u6b21\u6570", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"\u843d\u6b3e\u89e3\u6790\u91cd\u8bd5\u95f4\u9694(\u79d2)", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"\u9996\u9009\u5927\u8bed\u8a00\u6a21\u578b", None))
#if QT_CONFIG(tooltip)
        self.glm_model.setToolTip(QCoreApplication.translate("Form", u"\u667a\u8c31\u6e05\u8a00\u9996\u9009\u5927\u8bed\u8a00\u6a21\u578b", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("Form", u"\u843d\u6b3e\u89e3\u6790\u91cd\u8bd5\u6b21\u6570", None))
#if QT_CONFIG(tooltip)
        self.max_llm_retries.setToolTip(QCoreApplication.translate("Form", u"\u843d\u6b3e\u89e3\u6790\u662f\u901a\u8fc7\u8c03\u7528\u667a\u8c31\u5927\u6a21\u578b\u5b9e\u73b0\u7684\n"
"\u6709\u65f6\u6a21\u578b\u62e5\u6324\u5931\u8d25\u7387\u9ad8\uff0c\u53ef\u4ee5\u628a\u8be5\u503c\u8c03\u5927", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("Form", u"\u5355\u6279\u8bf7\u6c42\u6570", None))
#if QT_CONFIG(tooltip)
        self.max_article_count_per_request.setToolTip(QCoreApplication.translate("Form", u"\u8bbe\u7f6e\u5355\u6b21\u83b7\u53d6\u63a8\u6587\u7d22\u5f15\u591a\u5c11\u6761\u3002\u6700\u5927\u503c\u4e3a10\u3002\n"
"\u4e0d\u5f71\u54cd\u83b7\u53d6\u603b\u6570\uff0c\u53ea\u5f71\u54cd\u65f6\u95f4\u957f\u77ed\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("Form", u"\u6bcf\u6b21\u8bf7\u6c42\u95f4\u9694(\u79d2)", None))
#if QT_CONFIG(tooltip)
        self.fetch_interval_s.setToolTip(QCoreApplication.translate("Form", u"\u5efa\u8bae\u95f4\u9694\u65f6\u95f4\u4e0d\u8981\u5c0f\u4e8e1\u79d2\n"
"\u4ee5\u514d\u88ab\u5fae\u4fe1\u5c01\u7981", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("Form", u"\u76d1\u542c\u7aef\u53e3", None))
#if QT_CONFIG(tooltip)
        self.listen_port.setToolTip(QCoreApplication.translate("Form", u"\u4efb\u610f\u56db\u4f4d\u6570\u5b57\uff0c\u5982\u9047\u5230\u7f51\u7edc\u5f02\u5e38\u53ef\u5c1d\u8bd5\u4fee\u6539", None))
#endif // QT_CONFIG(tooltip)
        self.label_8.setText(QCoreApplication.translate("Form", u"\u7a3f\u8d39\u57fa\u6570(\u5143)", None))
#if QT_CONFIG(tooltip)
        self.fee_base.setToolTip(QCoreApplication.translate("Form", u"\u53c2\u4e0e\u4e00\u7bc7\u6587\u7ae0\u7a3f\u8d39\u7b97\u591a\u5c11\u94b1", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.glm_api_key.setToolTip(QCoreApplication.translate("Form", u"\u4ece\u667a\u8c31\u6e05\u8a00\u5f00\u53d1\u8005\u5e73\u53f0\u83b7\u5f97", None))
#endif // QT_CONFIG(tooltip)
        self.label_12.setText(QCoreApplication.translate("Form", u"\u667a\u8c31\u5927\u6a21\u578b API KEY", None))
#if QT_CONFIG(tooltip)
        self.label_13.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("Form", u"\u5c0f\u590f\u6210\u5458\u540d\u5355", None))
#if QT_CONFIG(tooltip)
        self.xiaoxia_members.setToolTip(QCoreApplication.translate("Form", u"\u4eba\u540d\u4e4b\u95f4\u7528\u9017\u53f7\u9694\u5f00", None))
#endif // QT_CONFIG(tooltip)
        self.cancel_btn.setText(QCoreApplication.translate("Form", u"\u53d6\u6d88", None))
        self.apply_btn.setText(QCoreApplication.translate("Form", u"\u786e\u5b9a", None))
        self.set_default_btn.setText(QCoreApplication.translate("Form", u"\u6062\u590d\u9ed8\u8ba4", None))
    # retranslateUi

