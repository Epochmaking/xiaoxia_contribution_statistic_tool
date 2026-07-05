import sys
from PySide6.QtWidgets import QApplication

from ui.ui_components import MainWindow
from controllers.proxy import unset_network_proxy
from utils.logging import get_logger

logger = get_logger(__name__)

def main(argv: list[str]):
    """主函数"""
    app = QApplication(argv)
    try:
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec())
    finally:
        unset_network_proxy()

if __name__ == "__main__":
    main(sys.argv)
