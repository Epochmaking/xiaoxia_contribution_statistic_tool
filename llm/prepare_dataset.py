"""
准备大模型SFT微调的数据集
"""

'''
你是专业公众号文末完整区块提取助手，严格遵守以下规则处理输入文本：
1. 完整保留文末所有关联内容：包含前置感谢语句、各类「标识：人名列表」创作者条目、图片备注说明、末尾出品版权语句；
2. 创作者条目规则：人名之间顿号分隔格式原样保留，同一标识下换行拆分的人名要合并为一行，删除条目内部换行；
3. 过滤正文祝福、星标引导、活动文案、上下篇导航、点赞分享按钮、发布时间等无关内容，只保留和创作者信息紧邻的配套文字、创作者条目、版权出品行；
4. 不删减原文存在的关联配套文字，不新增、不删减任何原文语句；
5. 去除多余空行，段落排版紧凑无空行；
6. 全文未找到任何创作者相关区块时，直接返回字符串None。
7. 输出结果中换行统一以\n表示。
'''

import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

from utils.logging import get_logger

logger = get_logger(__name__)

PAGE_URL = [
    "https://mp.weixin.qq.com/s/EDMDk0HD1KmjgLs-lXbCwg",
    "https://mp.weixin.qq.com/s/DHL06uIsxZH_aC9DgZ65uA",
    "https://mp.weixin.qq.com/s/A8KQLaCUVTQr4057aCWNIg",
]


EXTRACT_CHAR = 500

folder =  Path(__file__).resolve().parent / "plain_text"


if __name__ == "__main__":
    # 文件夹存在直接覆盖
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    for url in PAGE_URL:
        page.goto(url, wait_until="domcontentloaded")
        full_text = page.evaluate("() => document.body.innerText")
        test_text = full_text[-EXTRACT_CHAR:] # 提取后500个字符
        logger.info(f"链接{url}获取到文章内容: {test_text}")
        # 写入文件
        with (folder / f"{url.split('/')[-1]}.txt").open("w", encoding="utf-8") as f:
            f.write(test_text)
        logger.info(f"已将{url.split('/')[-1]}写入文件{folder / f"{url.split('/')[-1]}.txt"}")
