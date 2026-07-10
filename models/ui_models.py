from datetime import datetime

from PySide6.QtGui import (
    QPainter, QStandardItemModel, QStandardItem,
    QColor, QMouseEvent, QDesktopServices, QFont
)
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt, QEvent
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle

from models.mapping import article_mapping

from utils.logging import get_logger

logger = get_logger(__name__)

class ArticleListViewModel(QStandardItemModel):
    """文章列表视图模型, 用于显示文章列表"""
    # 定义固定的列顺序
    COLUMN_ORDER = ["title", "author", "publishing_time", "type", "content_url"]

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
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                elif key == "publishing_time":
                    # 格式化发布时间（字符串时间戳转换为datetime）
                    item.setText(datetime.fromtimestamp(int(article[key])).strftime("%Y-%m-%d %H:%M"))
                elif key == "author":
                    if article[key]:
                        author = article[key]
                    elif article[key] == "" and article["type"] == "小绿书":
                        author = "小绿书"
                    else:
                        author = "转载"
                    item.setText(author)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                elif key == "type":
                    item.setText(article[key])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setText(article[key])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)

                cell_font = QFont()
                cell_font.setPointSize(10)
                item.setFont(cell_font)
                item.setEditable(False)
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
        # ========== 使用表头单元格标准边距 ==========
        # if option.widget:
        #     style = option.widget.style()
        #     # QTableView单元格统一标准左右内边距
        #     margin = style.pixelMetric(QStyle.PixelMetric.PM_HeaderGripMargin, None, option.widget)
        # else:
        #     margin = 5  # 无控件时兜底默认值

        margin = 5  # 无控件时兜底默认值

        # 文字绘制矩形，和原生单元格偏移量完全一致
        text_rect = option.rect.adjusted(margin, 0, -margin, 0)

        # 超链接字体（加下划线）
        link_font = QFont(option.font)
        link_font.setUnderline(True)
        painter.setFont(link_font)

        # 鼠标悬浮变色逻辑
        if option.state & QStyle.StateFlag.State_MouseOver:
            pen_color = QColor(160, 185, 215)
        else:
            pen_color = QColor(121, 139, 163)

        pen = painter.pen()
        pen.setColor(pen_color)
        painter.setPen(pen)

        # 绘制文字，对齐方式沿用单元格原生对齐
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