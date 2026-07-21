import sys
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.ui_components import MainWindow
from controllers.proxy import unset_network_proxy
from constants import TEMP_PATH
from utils.logging import get_logger

logger = get_logger(__name__)
app = None

def main(argv: list[str]):
    """主函数"""
    if sys.platform == "win32":
        logger.info("设置应用用户模型ID为 com.xiaoxia.tool")
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.xiaoxia.tool")

    if not TEMP_PATH.exists():
        TEMP_PATH.mkdir(parents=True, exist_ok=True)
    if not TEMP_PATH.is_dir():
        # 临时目录不是目录，创建一个
        TEMP_PATH.unlink()
        TEMP_PATH.mkdir(parents=True, exist_ok=True)

    global app # pylint: disable=global-statement
    app = QApplication(argv)
    icon = QIcon(":/icons/xiaoxia.ico")
    app.setWindowIcon(icon)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception as e: # pylint: disable=broad-exception-caught
        logger.error("程序运行时发生异常: %s", e)
        if app:
            app.quit()
    finally:  
        # 重置网络代理
        unset_network_proxy()
