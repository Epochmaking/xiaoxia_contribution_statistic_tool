# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_win.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLayout, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QTextBrowser, QVBoxLayout, QWidget)
from . import ui_res_rc

class Ui_MainForm(object):
    def setupUi(self, MainForm):
        if not MainForm.objectName():
            MainForm.setObjectName(u"MainForm")
        MainForm.setWindowModality(Qt.WindowModality.NonModal)
        MainForm.resize(1000, 700)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainForm.sizePolicy().hasHeightForWidth())
        MainForm.setSizePolicy(sizePolicy)
        MainForm.setMinimumSize(QSize(1000, 700))
        MainForm.setMaximumSize(QSize(1000, 700))
        MainForm.setBaseSize(QSize(600, 400))
        palette = QPalette()
        brush = QBrush(QColor(248, 249, 250, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(56, 63, 70, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        brush2 = QBrush(QColor(120, 120, 120, 0))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush2)
        brush3 = QBrush(QColor(223, 223, 223, 0))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush3)
        brush4 = QBrush(QColor(255, 255, 255, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush4)
        brush5 = QBrush(QColor(6, 173, 86, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush5)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush4)
        brush6 = QBrush(QColor(33, 37, 41, 0))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush6)
        brush7 = QBrush(QColor(0, 0, 0, 0))
        brush7.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush7)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, brush5)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, brush4)
        brush8 = QBrush(QColor(255, 255, 255, 9))
        brush8.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush8)
        brush9 = QBrush(QColor(85, 255, 127, 128))
        brush9.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush9)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Accent, brush5)
#endif
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush3)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush5)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush7)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, brush5)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush8)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush9)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Accent, brush5)
#endif
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush5)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush6)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush7)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush8)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush9)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Accent, brush5)
#endif
        MainForm.setPalette(palette)
        MainForm.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        MainForm.setWindowOpacity(1.000000000000000)
        MainForm.setAutoFillBackground(False)
        MainForm.setStyleSheet(u"\n"
"border: none;")
        self.horizontalLayout_3 = QHBoxLayout(MainForm)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.MainFrame = QFrame(MainForm)
        self.MainFrame.setObjectName(u"MainFrame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.MainFrame.sizePolicy().hasHeightForWidth())
        self.MainFrame.setSizePolicy(sizePolicy1)
        self.MainFrame.setStyleSheet(u"QFrame#MainFrame {\n"
"	border-radius: 15px;\n"
"	background: rgb(54, 54, 54);\n"
"}")
        self.MainFrame.setFrameShape(QFrame.Shape.Panel)
        self.MainFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.MainFrame.setLineWidth(0)
        self.verticalLayout = QVBoxLayout(self.MainFrame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.verticalLayout.setContentsMargins(0, 10, 0, 0)
        self.title_bar = QWidget(self.MainFrame)
        self.title_bar.setObjectName(u"title_bar")
        self.title_bar.setMaximumSize(QSize(16777215, 40))
        palette1 = QPalette()
        self.title_bar.setPalette(palette1)
        self.title_bar.setAutoFillBackground(False)
        self.title_bar.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"QPushButton:hover {\n"
"    color: rgb(6, 173, 86);             /* \u60ac\u505c\u5b57\u4f53\u8272\uff08\u53ef\u4e0d\u53d8\uff09 */\n"
"}")
        self.horizontalLayout_2 = QHBoxLayout(self.title_bar)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 0, 10, 0)
        self.main_title = QLabel(self.title_bar)
        self.main_title.setObjectName(u"main_title")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.main_title.setFont(font)
        self.main_title.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.main_title.setIndent(70)

        self.horizontalLayout_2.addWidget(self.main_title, 0, Qt.AlignmentFlag.AlignHCenter)

        self.minimize_win_btn = QPushButton(self.title_bar)
        self.minimize_win_btn.setObjectName(u"minimize_win_btn")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.minimize_win_btn.sizePolicy().hasHeightForWidth())
        self.minimize_win_btn.setSizePolicy(sizePolicy2)
        self.minimize_win_btn.setMaximumSize(QSize(20, 16777215))
        self.minimize_win_btn.setFont(font)
        self.minimize_win_btn.setAutoFillBackground(False)

        self.horizontalLayout_2.addWidget(self.minimize_win_btn)

        self.close_win_btn = QPushButton(self.title_bar)
        self.close_win_btn.setObjectName(u"close_win_btn")
        sizePolicy2.setHeightForWidth(self.close_win_btn.sizePolicy().hasHeightForWidth())
        self.close_win_btn.setSizePolicy(sizePolicy2)
        self.close_win_btn.setMaximumSize(QSize(20, 16777215))
        self.close_win_btn.setFont(font)
        self.close_win_btn.setAutoFillBackground(False)

        self.horizontalLayout_2.addWidget(self.close_win_btn)


        self.verticalLayout.addWidget(self.title_bar)

        self.container = QWidget(self.MainFrame)
        self.container.setObjectName(u"container")
        self.container.setAutoFillBackground(False)
        self.verticalLayout_2 = QVBoxLayout(self.container)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.stackedWidget = QStackedWidget(self.container)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setAutoFillBackground(False)
        self.stackedWidget.setStyleSheet(u"")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.page_1.setAutoFillBackground(False)
        self.verticalLayout_6 = QVBoxLayout(self.page_1)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.content = QWidget(self.page_1)
        self.content.setObjectName(u"content")
        self.verticalLayout_7 = QVBoxLayout(self.content)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(50, -1, 50, -1)
        self.textBrowser = QTextBrowser(self.content)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setMouseTracking(False)
        self.textBrowser.setAcceptDrops(False)
        self.textBrowser.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByMouse)

        self.verticalLayout_7.addWidget(self.textBrowser)


        self.verticalLayout_6.addWidget(self.content)

        self.btn_container = QWidget(self.page_1)
        self.btn_container.setObjectName(u"btn_container")
        self.btn_container.setMinimumSize(QSize(0, 100))
        self.btn_container.setStyleSheet(u"QPushButton {\n"
"	background: rgb(6, 173, 86);\n"
"	color: rgb(255, 255, 255);\n"
"	border-radius: 10px;\n"
"	font-size: 20px;\n"
"	font-weight: bold;\n"
"}\n"
"QPushButton:hover {\n"
"	background: rgb(6, 156, 76);\n"
"}")
        self.horizontalLayout = QHBoxLayout(self.btn_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.pushButton_3 = QPushButton(self.btn_container)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMinimumSize(QSize(200, 50))
        self.pushButton_3.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)


        self.verticalLayout_6.addWidget(self.btn_container, 0, Qt.AlignmentFlag.AlignBottom)

        self.stackedWidget.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.stackedWidget.addWidget(self.page_3)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.verticalLayout.addWidget(self.container)


        self.horizontalLayout_3.addWidget(self.MainFrame)


        self.retranslateUi(MainForm)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainForm)
    # setupUi

    def retranslateUi(self, MainForm):
        MainForm.setWindowTitle(QCoreApplication.translate("MainForm", u"Form", None))
        self.main_title.setText(QCoreApplication.translate("MainForm", u"\u5c0f\u590f\u63a8\u9001\u7edf\u8ba1\u5de5\u5177", None))
        self.minimize_win_btn.setText(QCoreApplication.translate("MainForm", u"-", None))
        self.close_win_btn.setText(QCoreApplication.translate("MainForm", u"\u00d7", None))
        self.textBrowser.setHtml(QCoreApplication.translate("MainForm", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:26pt; font-weight:700; color:#ffffff;\">\u7b2c\u4e00\u6b65  \u83b7\u53d6\u516c\u4f17\u53f7UID</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; color:#ffffff;\">1. \u542f\u52a8\u5e76\u767b\u5f55\u7535\u8111\u7aef\u5fae\u4fe1</span></p>"
                        "\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; color:#ffffff;\">2. \u5355\u51fb\u672c\u9875\u9762\u201c\u5f00\u59cb\u83b7\u53d6\u201d\u6309\u94ae</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; color:#ffffff;\">3. \u4ece\u516c\u4f17\u53f7\u5217\u8868\u5355\u51fb\u6253\u5f00\u4efb\u610f\u4e00\u7bc7\u56fe\u6587\uff08\u4e0d\u80fd\u662f\u8d34\u56fe\uff09</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; color:#ffffff;\">4. \u5355\u51fb\u672c\u9875\u9762\u201c\u505c\u6b62\u83b7\u53d6\u201d\u6309\u94ae</span></p>\n"
"<p align=\"center\" style=\" margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/images/ste"
                        "p_1\" width=\"600\" /></p></body></html>", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainForm", u"\u5f00\u59cb\u83b7\u53d6", None))
    # retranslateUi

