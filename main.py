import sys
from PySide6.QtWidgets import QApplication

from ui.ui_components import MainWindow
from controllers.proxy import unset_network_proxy
from constants import TEMP_PATH
from utils.logging import get_logger

logger = get_logger(__name__)
app = None

def main(argv: list[str]):
    """主函数"""
    if not TEMP_PATH.exists():
        TEMP_PATH.mkdir(parents=True, exist_ok=True)
    if not TEMP_PATH.is_dir():
        # 临时目录不是目录，创建一个
        TEMP_PATH.unlink()
        TEMP_PATH.mkdir(parents=True, exist_ok=True)

    global app # pylint: disable=global-statement
    app = QApplication(argv)
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
