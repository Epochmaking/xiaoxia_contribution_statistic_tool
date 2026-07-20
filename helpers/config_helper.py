import dotenv

from utils.logging import get_logger
from constants.constants import CONFIG_FILE

logger = get_logger("config_setting")

def read_config(key: str, default: str | None = None) -> str | None:
    """
    读取配置文件中的值（直接从文件读取，不依赖启动时加载的环境变量）

    Args:
        key (str): 键名
        default (str | None): 默认值，未找到时返回

    Returns:
        str | None: 配置值
    """
    try:
        value = dotenv.get_key(CONFIG_FILE, key)
        return value if value is not None else default
    except Exception: # pylint: disable=broad-exception-caught
        return default

def write_config(kv: dict):
    """
    写入配置文件

    Args:
        kv (dict): 键值对字典
    """
    for key, value in kv.items():
        dotenv.set_key(CONFIG_FILE, key, value)
        logger.info("写入配置: %s = %s", key, value)

def del_config(key: str):
    """
    删除配置文件中的键值对

    Args:
        key (str): 键名
    """
    dotenv.unset_key(CONFIG_FILE, key)
    logger.info("删除配置: %s", key)