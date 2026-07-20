import subprocess
import ctypes
import time
import shutil
from typing import TYPE_CHECKING
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from mitmproxy.certs import CertStore

from utils.logging import get_logger

if TYPE_CHECKING:
    from ui.ui_components import MainWindow

logger = get_logger(__name__)

CONF_DIR = Path.home() / ".mitmproxy"
CERT_PATH = CONF_DIR / "mitmproxy-ca-cert.p12"

SW_SHOWNORMAL = 1
SEE_MASK_NOCLOSEPROCESS = 0x00000040
INFINITE = -1

def ensure_cert_status(main_window: "MainWindow"): # type: ignore
    """确保证书状态"""
    # 1.检查系统是否已有证书
    has_cert = _check_cert_status()
    has_cert_file = CERT_PATH.exists()

    if not has_cert or not has_cert_file:
        logger.info("系统未安装证书，开始安装")
        msg_box = QMessageBox(parent=main_window)
        try:
            # 触发mitmproxy，生成%USERDATA%/.mitmproxy文件夹，.p12文件在这个文件夹下
            _trigger_cert_generation()
            if not CERT_PATH.exists():
                raise RuntimeError("证书生成失败")
            _install_cert()
            has_cert = _check_cert_status()
            if not has_cert:
                raise RuntimeError("安装证书失败")
        except Exception as e: # pylint: disable=broad-exception-caught
            logger.error(f"安装证书失败: {e}")
            msg_box.critical(main_window,
                "安装证书失败", f"请手动安装证书{CERT_PATH}至系统根证书存储中")
            main_window.close()

def _trigger_cert_generation() -> None:
    """触发证书生成"""
    logger.info("触发 mitmproxy 证书生成")

    # 确保目录存在
    CONF_DIR.mkdir(parents=True, exist_ok=True)

    # 正确用法：from_store(目录路径, CA主文件名)
    # 自动检测是否已有证书，没有则生成全套文件
    _ = CertStore.from_store(
        path=str(CONF_DIR),
        basename="mitmproxy",
        key_size=2048,
    )

    logger.info(f"证书生成完成: {CONF_DIR.resolve()}")

def _check_cert_status() -> bool:
    """检查系统是否已有证书"""
    try:
        cert_path_str = str(CERT_PATH.resolve())
        result = subprocess.run(
            ["certutil", "-verify", cert_path_str],
            capture_output=True,
            text=True,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0 and (
            "验证成功" in output
            or "Verified" in output
            or "CERT_TRUST_IS_SELF_SIGNED" in output
            or "CERT_TRUST_HAS_EXACT_NAME_CONSTRAINT" in output
            or "---- 已验证的证书 ----" in output
        ):
            logger.info("证书验证成功")
            return True

        search_result = subprocess.run(
            ["certutil", "-store", "root"],
            capture_output=True,
            text=True,
            check=False,
        )
        store_output = (search_result.stdout or "") + (search_result.stderr or "")
        if "mitmproxy" in store_output:
            logger.info("证书验证成功")
            return True
        logger.info("证书验证失败，未在系统根证书存储中找到，开始安装")
        return False
    except Exception as e:
        logger.warning("检查证书状态时发生异常: %s", e)
        return False

def _is_admin() -> bool:
    """检测当前进程是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e: # pylint: disable=broad-exception-caught
        logger.warning("检测管理员权限失败: %s", e)
        return False


def _runas_install_cert(cert_path_str: str) -> None:
    """以管理员权限（UAC 提升）运行 PowerShell 安装证书（对 p12/pfx 支持更好）"""
    class SHELLEXECUTEINFO(ctypes.Structure):
        """ShellExecuteEx 结构体"""
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("fMask", ctypes.c_ulong),
            ("hwnd", ctypes.c_void_p),
            ("lpVerb", ctypes.c_wchar_p),
            ("lpFile", ctypes.c_wchar_p),
            ("lpParameters", ctypes.c_wchar_p),
            ("lpDirectory", ctypes.c_wchar_p),
            ("nShow", ctypes.c_int),
            ("hInstApp", ctypes.c_void_p),
            ("lpIDList", ctypes.c_void_p),
            ("lpClass", ctypes.c_void_p),
            ("hkeyClass", ctypes.c_void_p),
            ("dwHotKey", ctypes.c_ulong),
            ("DUMMYUNIONNAME", ctypes.c_void_p),
            ("hProcess", ctypes.c_void_p),
        ]

    ps_script = (
        "$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2;"
        f"$cert.Import('{cert_path_str}', '', "
        "[System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet);"
        "$store = New-Object System.Security.Cryptography.X509Certificates.X509Store('Root', 'LocalMachine');"
        "$store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite);"
        "$store.Add($cert);"
        "$store.Close();"
    )

    # pylint: disable=attribute-defined-outside-init
    # pylint: disable=invalid-name
    sei = SHELLEXECUTEINFO()
    sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
    sei.fMask = SEE_MASK_NOCLOSEPROCESS
    sei.hwnd = None
    sei.lpVerb = "runas"
    sei.lpFile = "powershell.exe"
    sei.lpParameters = f'-NoProfile -ExecutionPolicy Bypass -Command "{ps_script}"'
    sei.lpDirectory = None
    sei.nShow = SW_SHOWNORMAL
    sei.hInstApp = None
    sei.hProcess = None
    # pylint: enable=invalid-name
    # pylint: enable=attribute-defined-outside-init

    if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei)):
        error_code = ctypes.windll.kernel32.GetLastError()
        raise RuntimeError(f"无法启动管理员权限安装流程 (error={error_code})")

    if not sei.hProcess:
        raise RuntimeError("未获取到子进程句柄，无法追踪安装结果")

    ctypes.windll.kernel32.WaitForSingleObject(sei.hProcess, INFINITE)

    exit_code = ctypes.c_ulong(0)
    if not ctypes.windll.kernel32.GetExitCodeProcess(
        sei.hProcess, ctypes.byref(exit_code)
    ):
        logger.warning("无法获取子进程退出码，将通过证书检测验证结果")
    else:
        logger.info("管理员模式 PowerShell 退出码: %d", exit_code.value)

    ctypes.windll.kernel32.CloseHandle(sei.hProcess)
    time.sleep(0.5)


def _install_with_certutil(cert_path_str: str) -> bool:
    """策略一：使用 certutil -addstore -f（带强制参数写入本地计算机根存储）"""
    for args in [
        ["-addstore", "-f", "root", cert_path_str],
        ["-addstore", "root", cert_path_str],
        ["-addstore", "-f", "-enterprise", "root", cert_path_str],
    ]:
        result = subprocess.run(
            ["certutil"] + args,
            capture_output=True,
            text=True,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            logger.info("certutil 安装成功: %s", " ".join(args))
            return True
        logger.warning(
            "certutil 失败 (exit=%d, args=%s): %s",
            result.returncode,
            " ".join(args),
            output.strip().splitlines()[-1] if output.strip() else "",
        )
    return False


def _install_with_powershell(cert_path_str: str) -> bool:
    """策略二：使用 PowerShell + X509Certificate2 API（对 p12/pfx 最可靠）"""
    ps_script = (
        "$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2;"
        f"$cert.Import('{cert_path_str}', '', "
        "[System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet);"
        "$store = New-Object System.Security.Cryptography.X509Certificates.X509Store('Root', 'LocalMachine');"
        "$store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite);"
        "$store.Add($cert);"
        "$store.Close();"
    )
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            ps_script,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode == 0:
        logger.info("PowerShell 安装成功")
        return True
    logger.warning("PowerShell 失败 (exit=%d): %s", result.returncode, output)
    return False


def _install_cert() -> None:
    """安装证书：按策略依次尝试，非管理员时通过 UAC 提升后再安装"""
    cert_path_str = str(CERT_PATH.resolve())

    if _is_admin():
        # 策略一：certutil（传统方式，速度快但对 p12 支持不稳定）
        if _install_with_certutil(cert_path_str):
            return
        # 策略二：PowerShell + .NET X509Store（对 p12/pfx 最可靠，无需额外 Python 包）
        if _install_with_powershell(cert_path_str):
            return
        # 三种方式都失败，拷贝cert到assets目录，手动安装
        shutil.copy(CERT_PATH, Path("assets") / "mitmproxy-ca-cert.p12")
        raise RuntimeError("所有证书安装策略均失败")

    logger.info("当前未以管理员权限运行，将通过 UAC 申请管理员权限安装证书")
    _runas_install_cert(cert_path_str)
