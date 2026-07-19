import json
from datetime import datetime

from PySide6.QtGui import (
    QPainter, QStandardItemModel, QStandardItem,
    QColor, QMouseEvent, QDesktopServices, QFont
)
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt, QEvent
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle

from models.mapping import article_mapping
from helpers.helpers import get_article_list_from_db

from utils.logging import get_logger
from utils.format import pretty_json

logger = get_logger(__name__)


class ArticleListViewModel(QStandardItemModel):
    """文章列表视图模型, 用于显示文章列表"""
    # 定义固定的列顺序
    COLUMN_ORDER = [
        "publishing_time", "title", "author", "content_url", "type", "creators_list",
        "formatted_creators_list", "view_count", "like_count", "heart_count", "share_count", "collect_count"
    ]

    def __init__(self, article_list: list[dict] | None = None, to_calc_fee: bool = False, parent=None):
        if not article_list:
            try:
                article_list = get_article_list_from_db()
            except Exception as e:
                logger.error("从数据库获取文章列表失败: %s", e)
                raise e
 
        # 拷贝一份列顺序到实例级别，避免修改类属性导致的跨实例互相影响
        column_order = list(self.COLUMN_ORDER)
        if not to_calc_fee and "formatted_creators_list" in column_order:
            column_order.remove("formatted_creators_list")
        self.column_order = column_order

        self.row_count = len(article_list)
        self.column_count = len(self.column_order)
        super().__init__(self.row_count, self.column_count, parent)

        self.setHorizontalHeaderLabels(
            [article_mapping[key] if key in article_mapping else key for key in self.column_order]
        )

        for row, article in enumerate(article_list):
            for col, key in enumerate(self.column_order):
                item = QStandardItem()
                if key == "content_url":
                    item.setForeground(QColor(121, 139, 163))
                    item.setData(article.get(key, ""), Qt.ItemDataRole.UserRole)
                    item.setData("点击访问", Qt.ItemDataRole.DisplayRole)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

                elif key == "title":
                    title = article.get(key, "")
                    item.setText(f"《{title}》")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                elif key == "publishing_time":
                    # 格式化发布时间：兼容字符串时间戳和 datetime 对象（从数据库读回时）
                    _pt = article.get(key)
                    if _pt:
                        if isinstance(_pt, datetime):
                            _dt = _pt
                        else:
                            try:
                                _dt = datetime.fromtimestamp(int(_pt))
                            except (ValueError, TypeError):
                                _dt = None
                        if _dt:
                            item.setText(_dt.strftime("%Y-%m-%d\n %H:%M"))
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

                elif key == "author":
                    item.setText(str(article.get(key, "")))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

                elif key == "type":
                    item.setText(str(article.get(key, "")))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

                elif key == "view_count":

                    count = article.get(key, "")
                    if count > 100000:
                        item.setText("10万+")
                    else:
                        item.setText(str(count))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                elif key in ["like_count", "heart_count", "share_count", "collect_count"]:
                    item.setText(str(article.get(key, "")))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                elif key == "formatted_creators_list":
                    formatted_creators_list = article.get(key, "")
                    if formatted_creators_list:
                        try:
                            parsed = json.loads(formatted_creators_list)
                            formatted_creators_list = pretty_json(parsed, indent=2)
                        except json.JSONDecodeError:
                            pass
                    item.setText(formatted_creators_list)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                else:
                    text = article.get(key, "")
                    if not text or text == "None":
                        text = "无"
                    item.setText(str(text))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

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