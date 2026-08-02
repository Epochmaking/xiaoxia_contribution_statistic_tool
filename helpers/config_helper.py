import os
import dotenv
from utils.logging import get_logger


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
        from constants.constants import CONFIG_FILE # pylint: disable=import-outside-toplevel
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
    from constants.constants import CONFIG_FILE # pylint: disable=import-outside-toplevel
    for key, value in kv.items():
        dotenv.set_key(CONFIG_FILE, key, value)
        logger.info("写入配置: %s = %s", key, value)

def del_config(key: str):
    """
    删除配置文件中的键值对

    Args:
        key (str): 键名
    """
    from constants.constants import CONFIG_FILE # pylint: disable=import-outside-toplevel
    dotenv.unset_key(CONFIG_FILE, key)
    logger.info("删除配置: %s", key)

def read_xiaoxia_members() -> list[str] | None:
    """
    解析非小夏成员名单

    Returns:
        list[str] | None: 小夏成员名单
    """
    xiaoxia_members = str(os.getenv("xiaoxia_members"))
    if xiaoxia_members is None or xiaoxia_members in ["None", "none", "null", "Null", "空"]:
        logger.warning("小夏成员名单为空，将默认所有成员都是小夏")
        return None
    xiaoxia_member_list =  xiaoxia_members.replace("，", ",").split(",")
    for (i, member) in enumerate(xiaoxia_member_list):
        xiaoxia_member_list[i] = member.replace(" ", "")
    if len(xiaoxia_member_list) == 0:
        logger.warning("小夏成员名单为空，将默认所有成员都是小夏")
        return None
    logger.info("小夏成员名单: %s", xiaoxia_member_list)
    return xiaoxia_member_list
