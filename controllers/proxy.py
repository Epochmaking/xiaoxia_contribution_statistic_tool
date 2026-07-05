import winreg
import ctypes

from utils.logging import get_logger
logger = get_logger(__name__)

# WinINet 常量，用于刷新系统代理配置
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37

def _refresh_proxy():
    """刷新系统代理，使修改立即生效"""
    internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)

def set_network_proxy(host: str, port: int):
    """
    开启系统全局代理

    :param host: 代理主机地址
    :param port: 代理端口
    """
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
        # 启用代理
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        # 设置代理地址和端口
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{host}:{port}")
        # 可选：设置本地地址不经过代理
        # winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "localhost;127.0.0.1;<local>")
    _refresh_proxy()
    logger.info(f"系统代理已开启：{host}:{port}")

def unset_network_proxy():
    """关闭系统全局代理"""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
    _refresh_proxy()
    logger.info("系统代理已关闭")
