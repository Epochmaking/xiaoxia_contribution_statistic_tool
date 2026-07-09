from datetime import datetime

from PySide6.QtGui import (
    QPainter, QStandardItemModel, QStandardItem, 
    QColor, QMouseEvent, QDesktopServices
)
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt, QEvent
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle

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
                    item.setForeground(QColor(121, 139, 163))
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

class HyperlinkDelegate(QStyledItemDelegate):
    """链接委托类"""
    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex
    ):
        """重写绘制方法，支持前景色"""
        option = QStyleOptionViewItem(option)
        self.initStyleOption(option, index)
        painter.save()
        painter.setFont(option.font)
        pen = painter.pen()
        pen.setColor(QColor(121, 139, 163))
        painter.setPen(pen)

        # 计算带边距的绘制区域，与其他单元格保持一致
        margin = option.widget.style().pixelMetric(
            QStyle.PixelMetric.PM_FocusFrameHMargin, None, option.widget
        ) if option.widget else 4
        text_rect = option.rect.adjusted(margin, 0, -margin, 0)

        painter.drawText(text_rect, int(option.displayAlignment), str(option.text))
        painter.restore()

    def editorEvent( # pylint: disable=invalid-name
        self, event: QEvent, model,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex
    ):
        """处理鼠标点击事件"""
        # 处理鼠标点击事件
        if isinstance(event, QMouseEvent) and event.type() == QEvent.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton:
                url = index.data(Qt.ItemDataRole.UserRole)
                if url:
                    # 打开链接
                    QDesktopServices.openUrl(url)
                    return True
        return super().editorEvent(event, model, option, index)