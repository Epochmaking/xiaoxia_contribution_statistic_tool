from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

from models.mapping import article_mapping

class ArticleListViewModel(QStandardItemModel):
    """文章列表视图模型, 用于显示文章列表"""
    def __init__(self, article_list: list[dict], parent=None):
        self.row_count = len(article_list)
        self.column_count = len(article_list[0])
        super().__init__(self.row_count, self.column_count, parent)

        self.setHorizontalHeaderLabels(
            [article_mapping[key] if key in article_mapping else key for key in article_list[0]]
        )

        for row, article in enumerate(article_list):
            for col, key in enumerate(article):
                item = QStandardItem(article[key])
                item.setEditable(False)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                self.setItem(row, col, item)
