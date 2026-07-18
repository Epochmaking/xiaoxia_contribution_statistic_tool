from PySide6.QtWidgets import QTableView, QHeaderView
from PySide6.QtCore import Qt
from models.ui_models import ArticleListViewModel, HyperlinkDelegate

def set_article_confirm_table(article_confirm_table: QTableView, all_articles: list[dict] | None = None):
    """设置文章确认表格"""
    # 设置表格模型
    article_list_view = ArticleListViewModel(all_articles)
    article_confirm_table.setModel(article_list_view)

    # 设置超链接委托
    article_confirm_table.setItemDelegateForColumn(article_list_view.COLUMN_ORDER.index("content_url"), HyperlinkDelegate())

    # 设置表格样式
    article_confirm_table.setStyleSheet("""
        /* 表格空白底层底色 */
        QTableView {
            background-color: #F7F8FA;
            gridline-color: #E5E7EB;
            border: none;
        }
        /* 普通单元格 */
        QTableView::item {
            text-align: left;
            padding: 2px 5px;
            white-space: nowrap;
            color: #191919;
            background-color: #FFFFFF;
        }
        /* 鼠标悬浮未选中行 */
        QTableView::item:hover:!selected {
            background-color: #E8EBF0;
        }
        /* 选中行微信浅绿高亮 */
        QTableView::item:selected {
            background-color: #D6F3E2;
            color: #191919;
        }
        /* 表头样式 */
        QHeaderView::section {
            background-color: #F7F8FA;
            color: #191919;
            padding: 4px;
            font-size: 12px;
            border: none;
            border-bottom: 1px solid #E5E7EB;
        }
        /* 垂直滚动条整体 */
        QTableView QScrollBar:vertical {
            background-color: #F7F8FA;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        /* 水平滚动条整体 */
        QTableView QScrollBar:horizontal {
            background-color: #F7F8FA;
            height: 10px;
            margin: 0px 0px 0px 0px;
        }
        /* 滚动条滑块（未按下） */
        QTableView QScrollBar::handle:vertical,
        QTableView QScrollBar::handle:horizontal {
            background-color: #C8CCD1;
            min-height: 20px;
            min-width: 20px;
            border-radius: 5px;
            margin: 2px 2px 2px 2px;
        }
        /* 滚动条滑块（鼠标悬浮） */
        QTableView QScrollBar::handle:vertical:hover,
        QTableView QScrollBar::handle:horizontal:hover {
            background-color: #A8ADB5;
        }
        /* 滚动条滑块（按下） */
        QTableView QScrollBar::handle:vertical:pressed,
        QTableView QScrollBar::handle:horizontal:pressed {
            background-color: #8D9299;
        }
        /* 滚动条上下/左右箭头按钮 */
        QTableView QScrollBar::add-line:vertical,
        QTableView QScrollBar::sub-line:vertical,
        QTableView QScrollBar::add-line:horizontal,
        QTableView QScrollBar::sub-line:horizontal {
            background: none;
            width: 0px;
            height: 0px;
        }
        /* 滚动条两端的空白区域（点击可以跳转） */
        QTableView QScrollBar::add-page:vertical,
        QTableView QScrollBar::sub-page:vertical,
        QTableView QScrollBar::add-page:horizontal,
        QTableView QScrollBar::sub-page:horizontal {
            background-color: #F7F8FA;
        }
    """)

    # 自动换行内容
    article_confirm_table.setWordWrap(True)

    # 设置滚动模式为像素级连续滚动（替代默认的按行/单元格步进）
    article_confirm_table.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
    article_confirm_table.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

    # 允许用户拖拽调整所有列宽（Interactive 模式）
    article_confirm_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    # 允许用户通过拖拽列标题来交换列顺序
    article_confirm_table.horizontalHeader().setSectionsMovable(True)
    # 列宽不小于最小可见宽度，避免被用户拖到看不见
    article_confirm_table.horizontalHeader().setMinimumSectionSize(60)
    article_confirm_table.horizontalHeader().setStretchLastSection(True)

    # 内容自适应作为初始列宽
    article_confirm_table.resizeColumnsToContents()

    # 允许用户拖拽调整行高
    article_confirm_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    article_confirm_table.verticalHeader().setMinimumSectionSize(24)
    # 初始行高按内容自适应
    article_confirm_table.resizeRowsToContents()

    # 显示网格线
    article_confirm_table.setShowGrid(True)

    # 给标题列一个较宽的初始值，便于自动换行
    title_col = article_list_view.COLUMN_ORDER.index("title")
    article_confirm_table.setColumnWidth(title_col, 320)

    # 文本省略模式设为不省略，便于观察自动换行效果
    article_confirm_table.setTextElideMode(Qt.TextElideMode.ElideNone)