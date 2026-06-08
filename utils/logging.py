"""
日志模块
"""

import logging

# 1. 配置日志器
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()

# 2. 日志格式
# 文件日志：普通格式
file_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
# 控制台日志：带颜色格式
console_formatter = logging.Formatter(
    "\033[32m%(asctime)s\033[0m - "
    "[%(levelname_color)s] - "
    "\033[37m%(message)s\033[0m"
)

# 3. 文件处理器（写入文件，不带颜色）
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setFormatter(file_formatter)

# 4. 控制台处理器（带颜色）
class ColorHandler(logging.StreamHandler):
    """自定义控制台处理器，给不同级别的日志添加颜色"""
    def format(self, record):
        # 给不同级别日志分配颜色
        colors = {
            logging.DEBUG: "\033[36mDEBUG\033[0m",   # 青色
            logging.INFO: "\033[32mINFO\033[0m",     # 绿色
            logging.WARNING: "\033[93mWARNING\033[0m", # 黄色
            logging.ERROR: "\033[31mERROR\033[0m",     # 红色
            logging.CRITICAL: "\033[35mCRITICAL\033[0m"# 紫色
        }
        record.levelname_color = colors.get(record.levelno, record.levelname)
        return super().format(record)

console_handler = ColorHandler()
console_handler.setFormatter(console_formatter)

# 5. 添加两个处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """
    全局获取日志器实例
    
    :param name: 日志器名称
    :type name: str
    :return: 日志器实例
    :rtype: Logger
    """
    return logging.getLogger(name)
