"""编译UI文件的工具模块"""

import os
from pathlib import Path
from .logging import get_logger

logger = get_logger(__name__)

UI_DESIGN_FOLDER_PATH = Path(__file__).parent.parent / "ui" / "ui_design"
UI_COMPILED_FOLDER_PATH = Path(__file__).parent.parent / "ui" / "ui_compiled"
UI_RESOURCE_FILE = Path(__file__).parent.parent / "ui" / "ui_res.qrc"

def ui_to_py(ui_file: Path):
    """将UI文件转换为Python代码"""
    cmd = f"pyside6-uic {ui_file} -o {UI_COMPILED_FOLDER_PATH / ui_file.with_suffix('.py').name} --from-imports"
    os.system(cmd)

def ui_to_py_all():
    """批量转换UI文件"""
    for ui_file in UI_DESIGN_FOLDER_PATH.glob("*.ui"):
        logger.info("正在编译UI文件: %s", ui_file)
        ui_to_py(ui_file)

def ui_resource_compile():
    """编译UI资源文件"""
    logger.info("正在编译UI资源文件: %s", UI_RESOURCE_FILE)
    cmd = f"pyside6-rcc {UI_RESOURCE_FILE} -o {UI_COMPILED_FOLDER_PATH / 'ui_res_rc.py'}"
    os.system(cmd)

if __name__ == "__main__":
    logger.info("开始编译UI文件")
    ui_resource_compile()
    ui_to_py_all()
    logger.info("UI文件编译完成")
