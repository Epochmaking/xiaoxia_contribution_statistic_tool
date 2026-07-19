import dotenv

from utils.logging import get_logger
from constants.constants import CONFIG_FILE

logger = get_logger("config_setting")

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
