from PySide6.QtWidgets import QTableView
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
    """)

    # 自动换行内容
    article_confirm_table.setWordWrap(True)

    # 自适应列宽
    article_confirm_table.horizontalHeader().setStretchLastSection(True)

    # 双击列分隔自动适配内容宽度
    article_confirm_table.resizeColumnsToContents()

    # 行高自适应
    article_confirm_table.resizeRowsToContents()

    # 显示网格线
    article_confirm_table.setShowGrid(True)
