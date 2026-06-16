from threading import Thread
from PySide6.QtCore import Signal
from PySide6.QtCore import QThread

from controllers.crawler import MpBizCrawler

from utils import logging

logger = logging.get_logger(__name__)

class GetMpBizThread(QThread):
    """获取微信公众号BIZ"""
    task_over = Signal(str)

    def __init__(self):
        super().__init__()
        self.to_stop = False # 停止thread标志
        self.crawler = MpBizCrawler()

    def run(self):
        """线程运行方法"""
        self.to_stop = False
        Thread(target=self.crawler.start, daemon=True).start()
        while True:
            if self.to_stop:
                self.crawler.stop()
                logger.info("停止获取微信公众号BIZ")
                break
            mp_biz = self.crawler.get_mp_biz()
            if mp_biz is not None:
                self.to_stop = True
                self.crawler.stop()
                logger.info("获取到微信公众号BIZ: %s", mp_biz)
                self.task_over.emit(mp_biz)
                break
    
    def stop(self):
        """停止线程"""
        self.to_stop = True
        self.wait()

