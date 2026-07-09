from datetime import datetime

from PySide6.QtGui import QPainter, QStandardItemModel, QStandardItem
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt, QEvent
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QApplication

from models.mapping import article_mapping

from utils.logging import get_logger

logger = get_logger(__name__)

class ArticleListViewModel(QStandardItemModel):
    """文章列表视图模型, 用于显示文章列表"""
    # 定义固定的列顺序
    COLUMN_ORDER = ["title", "author", "publishing_time", "content_url"]

    def __init__(self, article_list: list[dict], parent=None):
        self.row_count = len(article_list)
        self.column_count = len(article_list[0])
        super().__init__(self.row_count, self.column_count, parent)

        self.setHorizontalHeaderLabels(
            [article_mapping[key] if key in article_mapping else key for key in self.COLUMN_ORDER]
        )

        for row, article in enumerate(article_list):
            for col, key in enumerate(self.COLUMN_ORDER):
                item = QStandardItem()
                if key == "content_url":
                    item.setData(article[key], Qt.ItemDataRole.UserRole)
                    item.setData("点击访问", Qt.ItemDataRole.DisplayRole)
                elif key == "publishing_time":
                    # 格式化发布时间（字符串时间戳转换为datetime）
                    item.setText(datetime.fromtimestamp(int(article[key])).strftime("%Y-%m-%d %H:%M:%S"))
                elif key == "author":
                    author = article[key] if article[key] else "转载"
                    item.setText(author)
                else:
                    item.setText(article[key])

                item.setEditable(False)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                self.setItem(row, col, item)

        logger.info("文章列表视图模型初始化完成, 总行数: %d, 总列数: %d", self.row_count, self.column_count)

# class HyperlinkDelegate(QStyledItemDelegate):
#     """链接委托类"""
#     def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
#         """绘制表格单元格"""
#         url = index.data(Qt.ItemDataRole.UserRole)

#         if url:
#             # 使用富文本绘制超链接
#             doc = QTextDocument()
#             doc.setHtml(f'<a href="{url}">{index.data()}</a>')
            
#             # 设置绘制区域
#             painter.save()
            
#             # 设置选项
#             opt = QStyleOptionViewItem(option)
#             self.initStyleOption(opt, index)
            
#             # 绘制背景
#             opt.widget.style().drawControl(
#                 QStyleOptionViewItem.,
#                 opt, painter, opt.widget
#             )
            
#             # 绘制文本
#             painter.translate(opt.rect.left(), opt.rect.top())
#             clip_rect = QSize(opt.rect.width(), opt.rect.height())
#             doc.drawContents(painter, clip_rect)
            
#             painter.restore()
#         else:
#             # 非链接列使用默认绘制
#             super().paint(painter, option, index)

#     def editorEvent(self, event, model, option, index):
#         # 处理鼠标点击事件
#         if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
#             url = index.data(Qt.ItemDataRole.UserRole)
#             if url:
#                 # 打开链接
#                 QApplication.desktop().openUrl(url)
#                 return True
#         return super().editorEvent(event, model, option, index)