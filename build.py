import os
import sys
import subprocess

from utils.logging import get_logger

logger = get_logger(__name__)

def main():
    # 项目根目录
    root = os.path.abspath(".")
    # 输出目录
    output_dir = os.path.join(root, "build")
    # 图标路径，不存在就自动移除该参数
    ico_path = os.path.join(root, "app.ico")

    # 构造 nuitka 参数列表
    args = [
        sys.executable, "-m", "nuitka", "main.py",
        "--standalone",
        "--windows-disable-console",
        "--enable-plugin=pyside6",
        "--enable-plugin=playwright",
        f"--include-data-dir={os.environ['LOCALAPPDATA']}\\ms-playwright=ms-playwright",
        "--deployment",
        "--lto=auto",
        "--remove-output",
        "--show-progress",
        "--show-memory",
        f"--output-dir={output_dir}"
    ]

    # 如果图标存在，追加图标参数
    if os.path.exists(ico_path):
        args.append(f"--windows-icon-from-ico={ico_path}")
    else:
        logger.warning("警告：未找到 app.ico，跳过程序图标设置")

    logger.info("===== 开始执行 Nuitka 打包 =====")
    logger.info("执行命令：")
    logger.info(" ".join(args))
    logger.info("=" * 50)

    # 调用打包
    ret = subprocess.run(args, cwd=root)
    if ret.returncode == 0:
        logger.info(f"\n打包完成！产物输出目录：{output_dir}")
    else:
        logger.error(f"\n打包失败，错误码：{ret.returncode}")
        sys.exit(ret.returncode)

if __name__ == "__main__":
    main()