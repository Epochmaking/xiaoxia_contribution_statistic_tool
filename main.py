import sys
from PySide6.QtWidgets import QApplication

from ui.ui_components import MainWindow
from controllers.proxy import unset_network_proxy
from utils.logging import get_logger

logger = get_logger(__name__)

def main(argv: list[str]):
    """主函数"""
    app = QApplication(argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main(sys.argv)
    finally:
        unset_network_proxy()
