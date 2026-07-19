import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from PySide6.QtCore import Qt

from models.ui_models import ArticleListViewModel

def export_to_file(folder_path: Path, to_calc_fee: bool = False):
    """
    导出文章列表到Excel文件
    """
    article_list_path = folder_path / f"作品清单_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    article_model = ArticleListViewModel(to_calc_fee=to_calc_fee)
    column_order = article_model.column_order
    if to_calc_fee:
        fee_model = ...
        fee_list_path = folder_path / f"稿费清单_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"

    row_cnt = article_model.row_count
    col_cnt = article_model.column_count

    wb = Workbook()
    ws = wb.active

    if ws is None:
        raise ValueError("ws is None")

    # 通用边框
    thin = Side(style="thin", color="cccccc")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    # 表头样式：加粗、居中、浅蓝底色
    header_font = Font(bold=True)
    header_align = Alignment(horizontal="center", vertical="center")
    header_fill = PatternFill("solid", start_color="DCE6F1")
    # 内容单元格居中并自动换行
    cell_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # 写入表头
    for c in range(col_cnt):
        cell = ws.cell(row=1, column=c+1, value=article_model.headerData(c, Qt.Orientation.Horizontal))
        cell.font = header_font
        cell.alignment = header_align
        cell.border = border
        cell.fill = header_fill

    # 写入表格数据
    for r in range(row_cnt):
        for c in range(col_cnt):
            key = column_order[c]

            if key == "content_url": # 内容链接需要写入完整链接
                val = article_model.index(r, c).data(role = Qt.ItemDataRole.UserRole)
            else:
                val = article_model.index(r, c).data()

            cell = ws.cell(row=r+2, column=c+1, value=val)
            cell.alignment = cell_align
            cell.border = border

    # 自适应列宽简易处理
    for col in range(1, col_cnt+1):
        ws.column_dimensions[chr(64+col)].width = 20

    wb.save(article_list_path)
