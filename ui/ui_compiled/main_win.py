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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QDateEdit,
    QDateTimeEdit, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QTableView, QTextBrowser,
    QVBoxLayout, QWidget)
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
        self.textBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textBrowser.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByMouse)

        self.verticalLayout_7.addWidget(self.textBrowser)

        self.widget_3 = QWidget(self.content)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_6.setSpacing(5)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, 3, -1, 3)
        self.label_4 = QLabel(self.widget_3)
        self.label_4.setObjectName(u"label_4")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setPointSize(14)
        self.label_4.setFont(font1)
        self.label_4.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_6.addWidget(self.label_4, 0, Qt.AlignmentFlag.AlignVCenter)

        self.biz_display_label = QLabel(self.widget_3)
        self.biz_display_label.setObjectName(u"biz_display_label")
        sizePolicy3.setHeightForWidth(self.biz_display_label.sizePolicy().hasHeightForWidth())
        self.biz_display_label.setSizePolicy(sizePolicy3)
        self.biz_display_label.setFont(font1)
        self.biz_display_label.setStyleSheet(u"color:rgb(121, 139, 163);\n"
"")

        self.horizontalLayout_6.addWidget(self.biz_display_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self.reget_biz_btn = QPushButton(self.widget_3)
        self.reget_biz_btn.setObjectName(u"reget_biz_btn")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.reget_biz_btn.sizePolicy().hasHeightForWidth())
        self.reget_biz_btn.setSizePolicy(sizePolicy4)
        self.reget_biz_btn.setMinimumSize(QSize(110, 30))
        font2 = QFont()
        font2.setPointSize(11)
        font2.setBold(True)
        self.reget_biz_btn.setFont(font2)
        self.reget_biz_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.reget_biz_btn.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);\n"
"	background: rgb(67, 67, 67);\n"
"	border-radius: 5px;\n"
"	font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background: rgb(76, 76, 76);\n"
"}")

        self.horizontalLayout_6.addWidget(self.reget_biz_btn, 0, Qt.AlignmentFlag.AlignLeft)


        self.verticalLayout_7.addWidget(self.widget_3)


        self.verticalLayout_6.addWidget(self.content)

        self.btn_container = QWidget(self.page_1)
        self.btn_container.setObjectName(u"btn_container")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.btn_container.sizePolicy().hasHeightForWidth())
        self.btn_container.setSizePolicy(sizePolicy5)
        self.btn_container.setMinimumSize(QSize(0, 80))
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
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 5)
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.step_one_btn = QPushButton(self.btn_container)
        self.step_one_btn.setObjectName(u"step_one_btn")
        sizePolicy.setHeightForWidth(self.step_one_btn.sizePolicy().hasHeightForWidth())
        self.step_one_btn.setSizePolicy(sizePolicy)
        self.step_one_btn.setMinimumSize(QSize(200, 50))
        self.step_one_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout.addWidget(self.step_one_btn)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)


        self.verticalLayout_6.addWidget(self.btn_container, 0, Qt.AlignmentFlag.AlignBottom)

        self.stackedWidget.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_3 = QVBoxLayout(self.page_2)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.content_2 = QWidget(self.page_2)
        self.content_2.setObjectName(u"content_2")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.content_2.sizePolicy().hasHeightForWidth())
        self.content_2.setSizePolicy(sizePolicy6)
        self.verticalLayout_8 = QVBoxLayout(self.content_2)
        self.verticalLayout_8.setSpacing(2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(50, 9, 50, 0)
        self.textBrowser_2 = QTextBrowser(self.content_2)
        self.textBrowser_2.setObjectName(u"textBrowser_2")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.textBrowser_2.sizePolicy().hasHeightForWidth())
        self.textBrowser_2.setSizePolicy(sizePolicy7)
        self.textBrowser_2.setMaximumSize(QSize(16777215, 90))
        self.textBrowser_2.setMouseTracking(False)
        self.textBrowser_2.setAcceptDrops(False)
        self.textBrowser_2.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByMouse)

        self.verticalLayout_8.addWidget(self.textBrowser_2, 0, Qt.AlignmentFlag.AlignTop)


        self.verticalLayout_3.addWidget(self.content_2)

        self.widget = QWidget(self.page_2)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"")
        self.horizontalLayout_5 = QHBoxLayout(self.widget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(50, -1, 50, -1)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        font3 = QFont()
        font3.setPointSize(16)
        self.label.setFont(font3)
        self.label.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_5.addWidget(self.label)

        self.date_edit = QDateEdit(self.widget)
        self.date_edit.setObjectName(u"date_edit")
        font4 = QFont()
        self.date_edit.setFont(font4)
        self.date_edit.setStyleSheet(u"QDateEdit {\n"
"	font-size: 16px;\n"
"}\n"
"\n"
"/*\u6807\u9898\u680f\u7684\u6837\u5f0f*/\n"
"QCalendarWidget QWidget#qt_calendar_navigationbar\n"
"{ \n"
"  background-color: rgb(6, 173, 86);\n"
"}\n"
"\n"
"/*\u65e5\u5386\u90e8\u5206*/\n"
"#qt_calendar_calendarview {\n"
"    background-color: rgb(71, 71, 71);	/*\u80cc\u666f\u989c\u8272*/\n"
"    font: 16px;								/*\u5b57\u4f53*/\n"
"}\n"
"\n"
"/*\u8fd9\u91cc\u662f\u6fc0\u6d3b\u7684\u65e5\u671f\u7684\u6837\u5f0f\u4e5f\u5c31\u662f\u5f53\u524d\u8fd9\u4e2a\u6708*/\n"
"QCalendarWidget QAbstractItemView:enabled \n"
" {\n"
"	selection-background-color: rgb(6, 173, 86);\n"
"    selection-color: rgb(255, 255, 255);\n"
"   	font-size:16px;  \n"
"   	color: rgb(255, 255, 255); \n"
" }\n"
"  \n"
" /*\u8fd9\u91cc\u662f\u5176\u4ed6\u6708\u4efd\u7684\u6837\u5f0f*/\n"
"QCalendarWidget QAbstractItemView:disabled \n"
"{ \n"
"	color: rgb(134, 134, 134);\n"
"}\n"
"")
        self.date_edit.setWrapping(False)
        self.date_edit.setFrame(False)
        self.date_edit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.date_edit.setAccelerated(False)
        self.date_edit.setProperty(u"showGroupSeparator", False)
        self.date_edit.setCurrentSection(QDateTimeEdit.Section.YearSection)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setTimeSpec(Qt.TimeSpec.UTC)

        self.horizontalLayout_5.addWidget(self.date_edit)

        self.label_5 = QLabel(self.widget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font3)
        self.label_5.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_5.addWidget(self.label_5)

        self.to_calc_fee = QCheckBox(self.widget)
        self.to_calc_fee.setObjectName(u"to_calc_fee")
        sizePolicy.setHeightForWidth(self.to_calc_fee.sizePolicy().hasHeightForWidth())
        self.to_calc_fee.setSizePolicy(sizePolicy)
        self.to_calc_fee.setMinimumSize(QSize(15, 15))
        self.to_calc_fee.setStyleSheet(u"QCheckBox {\n"
"    font-size: 12px;\n"
"    color: #333333;\n"
"    spacing: 8px; /* \u65b9\u6846\u548c\u6587\u5b57\u95f4\u8ddd */\n"
"}\n"
"/* \u590d\u9009\u6846\u65b9\u6846\u57fa\u7840 */\n"
"QCheckBox::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"    border: 3px solid #666666;\n"
"    border-radius: 4px; /* \u5706\u89d2\u65b9\u6846 */\n"
"    border-color: rgb(212, 212, 212);\n"
"    background-color: white;\n"
"}\n"
"/* \u9f20\u6807\u60ac\u6d6e\u672a\u9009\u4e2d */\n"
"QCheckBox::indicator:hover {\n"
"    border-color: rgb(6, 173, 86);\n"
"}\n"
"/* \u9009\u4e2d\u72b6\u6001\uff1a\u7eff\u8272\u80cc\u666f+\u7eff\u8272\u8fb9\u6846\uff0c\u539f\u751f\u767d\u8272\u5bf9\u52fe\u81ea\u52a8\u51fa\u73b0 */\n"
"QCheckBox::indicator:checked {\n"
"    border-color: rgb(6, 173, 86);\n"
"    background-color: rgb(6, 173, 86);\n"
"    /* \u66ff\u6362image\uff0c\u4f7f\u7528Qt\u5185\u7f6e\u52fe\u9009\u7b26\u53f7\uff0c\u767d\u8272 */\n"
"    border-image: none;\n"
"    image: url(\":/images/checkmark_white\");\n"
""
                        "}\n"
"")
        self.to_calc_fee.setTristate(False)

        self.horizontalLayout_5.addWidget(self.to_calc_fee)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addWidget(self.widget, 0, Qt.AlignmentFlag.AlignTop)

        self.widget_2 = QWidget(self.page_2)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_4 = QVBoxLayout(self.widget_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(50, -1, 50, -1)
        self.label_2 = QLabel(self.widget_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font3)
        self.label_2.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.verticalLayout_4.addWidget(self.label_2)

        self.article_list_url = QLabel(self.widget_2)
        self.article_list_url.setObjectName(u"article_list_url")
        palette2 = QPalette()
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush5)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush5)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush5)
        brush10 = QBrush(QColor(7, 188, 91, 255))
        brush10.setStyle(Qt.BrushStyle.SolidPattern)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, brush10)
        brush11 = QBrush(QColor(6, 173, 86, 128))
        brush11.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush11)
#endif
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush5)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush5)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush5)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, brush10)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush11)
#endif
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush5)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush5)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush5)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush11)
#endif
        self.article_list_url.setPalette(palette2)
        font5 = QFont()
        font5.setPointSize(12)
        self.article_list_url.setFont(font5)
        self.article_list_url.setStyleSheet(u"color: rgb(6, 173, 86);")
        self.article_list_url.setWordWrap(True)
        self.article_list_url.setMargin(2)
        self.article_list_url.setIndent(2)
        self.article_list_url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout_4.addWidget(self.article_list_url)


        self.verticalLayout_3.addWidget(self.widget_2, 0, Qt.AlignmentFlag.AlignTop)

        self.btn_container_2 = QWidget(self.page_2)
        self.btn_container_2.setObjectName(u"btn_container_2")
        self.btn_container_2.setMinimumSize(QSize(0, 100))
        self.btn_container_2.setStyleSheet(u"QPushButton {\n"
"	background: rgb(6, 173, 86);\n"
"	color: rgb(255, 255, 255);\n"
"	border-radius: 10px;\n"
"	font-size: 20px;\n"
"	font-weight: bold;\n"
"}\n"
"QPushButton:hover {\n"
"	background: rgb(6, 156, 76);\n"
"}")
        self.horizontalLayout_4 = QHBoxLayout(self.btn_container_2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.step_two_btn = QPushButton(self.btn_container_2)
        self.step_two_btn.setObjectName(u"step_two_btn")
        sizePolicy.setHeightForWidth(self.step_two_btn.sizePolicy().hasHeightForWidth())
        self.step_two_btn.setSizePolicy(sizePolicy)
        self.step_two_btn.setMinimumSize(QSize(200, 50))
        self.step_two_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_4.addWidget(self.step_two_btn)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_6)


        self.verticalLayout_3.addWidget(self.btn_container_2, 0, Qt.AlignmentFlag.AlignBottom)

        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.verticalLayout_5 = QVBoxLayout(self.page_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_3 = QLabel(self.page_3)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setTextFormat(Qt.TextFormat.MarkdownText)

        self.verticalLayout_5.addWidget(self.label_3)

        self.article_confirm_table = QTableView(self.page_3)
        self.article_confirm_table.setObjectName(u"article_confirm_table")

        self.verticalLayout_5.addWidget(self.article_confirm_table)

        self.btn_container_3 = QWidget(self.page_3)
        self.btn_container_3.setObjectName(u"btn_container_3")
        self.btn_container_3.setStyleSheet(u"QPushButton {\n"
"	background: rgb(6, 173, 86);\n"
"	color: rgb(255, 255, 255);\n"
"	border-radius: 10px;\n"
"	font-size: 20px;\n"
"	font-weight: bold;\n"
"}\n"
"QPushButton:hover {\n"
"	background: rgb(6, 156, 76);\n"
"}")
        self.horizontalLayout_7 = QHBoxLayout(self.btn_container_3)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.step_three_btn = QPushButton(self.btn_container_3)
        self.step_three_btn.setObjectName(u"step_three_btn")
        sizePolicy.setHeightForWidth(self.step_three_btn.sizePolicy().hasHeightForWidth())
        self.step_three_btn.setSizePolicy(sizePolicy)
        self.step_three_btn.setMinimumSize(QSize(200, 50))
        self.step_three_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_7.addWidget(self.step_three_btn)


        self.verticalLayout_5.addWidget(self.btn_container_3)

        self.stackedWidget.addWidget(self.page_3)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.verticalLayout.addWidget(self.container)


        self.horizontalLayout_3.addWidget(self.MainFrame)


        self.retranslateUi(MainForm)

        self.stackedWidget.setCurrentIndex(1)


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
                        "p_1\" width=\"550\" /></p></body></html>", None))
        self.label_4.setText(QCoreApplication.translate("MainForm", u"\u5df2\u83b7\u53d6\u7684\u516c\u4f17\u53f7ID\uff1a", None))
        self.biz_display_label.setText(QCoreApplication.translate("MainForm", u"\u65e0", None))
        self.reget_biz_btn.setText(QCoreApplication.translate("MainForm", u"\u21bb \u91cd\u65b0\u83b7\u53d6", None))
        self.step_one_btn.setText(QCoreApplication.translate("MainForm", u"\u5f00\u59cb\u83b7\u53d6", None))
        self.textBrowser_2.setHtml(QCoreApplication.translate("MainForm", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:26pt; font-weight:700; color:#ffffff;\">\u7b2c\u4e8c\u6b65  \u83b7\u53d6\u516c\u4f17\u53f7\u5386\u53f2\u6587\u7ae0\u5217\u8868</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:15px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#ffffff;\"><br /></p></body></html>", None))
        self.label.setText(QCoreApplication.translate("MainForm", u"1. \u8bf7\u9009\u62e9\u8981\u7edf\u8ba1\u7684\u6708\u4efd\uff1a", None))
        self.date_edit.setDisplayFormat(QCoreApplication.translate("MainForm", u"yyyy/M", None))
        self.label_5.setText(QCoreApplication.translate("MainForm", u"   \u662f\u5426\u540c\u65f6\u7edf\u8ba1\u7a3f\u8d39", None))
        self.to_calc_fee.setText("")
        self.label_2.setText(QCoreApplication.translate("MainForm", u"3. \u8bf7\u7528\u9f20\u6807\u53f3\u952e\u4ee5\u4e0b\u94fe\u63a5\u590d\u5236\u5e76\u7c98\u8d34\u5230\u5fae\u4fe1\u804a\u5929\u6253\u5f00\uff1a", None))
        self.article_list_url.setText(QCoreApplication.translate("MainForm", u"[URL_HOLDER]", None))
        self.step_two_btn.setText(QCoreApplication.translate("MainForm", u"\u5f00\u59cb\u83b7\u53d6", None))
        self.label_3.setText(QCoreApplication.translate("MainForm", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700; color:#ffffff;\">\u7b2c\u4e09\u6b65 \u786e\u8ba4\u6587\u7ae0\u5217\u8868</span></p></body></html>", None))
        self.step_three_btn.setText(QCoreApplication.translate("MainForm", u"\u6211\u5df2\u786e\u8ba4", None))
    # retranslateUi

