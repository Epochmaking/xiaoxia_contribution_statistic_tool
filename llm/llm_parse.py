import time
import json
import requests

from constants import GLM_API_KEY, MAX_LLM_RETRIES, LLM_MODEL, LLM_BACKUP_MODEL, MAX_TIMEOUT_S, LLM_FETCH_INTERVAL_S
from utils.logging import get_logger

logger = get_logger(__name__)


LLM_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 首选glm-4.7-flash模型
MODEL = LLM_MODEL
# 备选模型glm-4.7-flashx
BACKUP_MODEL = LLM_BACKUP_MODEL

HEADERS = {
    "Authorization": f"Bearer {GLM_API_KEY}",
    "Content-Type": "application/json"
}

def llm_request(system_prompt: str, user_prompt: str, temperature: float = 0.1, response_format: str = "text") -> str:
    """
    调用LLM模型，返回模型回复
    :param system_prompt: 系统提示
    :param user_prompt: 用户提示
    :param temperature: 温度参数，0.1-0.9之间
    :return: 模型回复
    """

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "stream": False,
        "temperature": temperature,
        "thinking": { "type": "disabled" },
        "response_format": { "type": response_format }
    }

    logger.info("开始调用模型")

    MAX_MODEL_RETRIES = MAX_LLM_RETRIES // 2
    MAX_BACKUP_MODEL_RETRIES = MAX_LLM_RETRIES - MAX_MODEL_RETRIES

    for i in range(MAX_MODEL_RETRIES):
        try:
            response = requests.post(LLM_URL, headers=HEADERS, json=payload, timeout=MAX_TIMEOUT_S)
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                logger.info(f"LLM模型调用成功，调用模型： {MODEL}, 回复： {result}")
                return result
            else:
                logger.warning(f"LLM模型调用失败，状态码： {response.status_code}")
                logger.info(f"第 {i + 1} 次重试")
                time.sleep(LLM_FETCH_INTERVAL_S)
                continue
        except requests.exceptions.RequestException as e:
            logger.warning(f"LLM模型调用失败，异常信息：{e}")
            logger.info(f"第 {i + 1} 次重试")
            time.sleep(LLM_FETCH_INTERVAL_S)
            continue

    # 尝试备用模型
    payload["model"] = BACKUP_MODEL
    logger.info(f"尝试备用模型： {BACKUP_MODEL}")
    for i in range(MAX_BACKUP_MODEL_RETRIES):
        try:
            response = requests.post(LLM_URL, headers=HEADERS, json=payload, timeout=MAX_TIMEOUT_S)
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                logger.info(f"备用模型调用成功，调用模型： {BACKUP_MODEL}, 回复： {result}")
                return result
            else:
                logger.warning(f"备用模型调用失败，状态码： {response.status_code}")
                logger.info(f"第 {i + 1 + MAX_MODEL_RETRIES} 次重试")
                time.sleep(LLM_FETCH_INTERVAL_S)
                continue
        except requests.exceptions.RequestException as e:
            logger.warning(f"备用模型调用失败，异常信息：{e}")

    logger.error("所有模型调用失败")
    return ""


def parse_creator_list_by_llm(content: str) -> str:
    """
    解析文章内容中的作者列表
    :param content: 文章内容
    :return: 作者列表字符串
    """
    system_prompt = """
    你是专业公众号文末落款区块提取助手，只提取文章**最末尾集中成片的落款区块**，严格遵守所有强制规则，违规输出直接判定错误：
    【强制范围铁则（最高优先级，违背即输出错误）】
    1. 仅提取整篇文本**最底部连续成片**的落款内容；严禁提取文章中部、导语、新闻标题、正文段落里零散出现的单行；
    2. 正文、活动导语、新闻标题、上下篇导航、点赞按钮、星标指引、留言引导、活动预告、采访正文全部属于无关内容，**一字都不能混入输出**。

    【内容处理规则】
    3. 完整保留落款内配套文字：包含和文章创作相关的感谢语、图片备注、单位说明、出品版权行等；
    4. 创作者条目格式：人名顿号原样保留，同一条目内换行人名合并为一行，删除条目内部换行；
    5. 剔除所有空行，输出段落紧凑无空白；
    6. 全文末尾无符合标准的成片落款区块，直接返回纯字符串None，禁止编造任何人名/标签。

    【输出格式强制规则】
    7. 输出内换行统一用\n，不输出多余空行、解释、前言、注释、JSON、markdown；
    8. 禁止自创不存在标签（如标识、作者等），仅保留原文自带字段；
    9. 输出只由落款原文文本+换行符\n组成，无额外修饰字符。

    【正确输出示例】
    【示例一】
    视频策划单位：党委宣传部
    视频支持单位：招生与考试办公室、新闻传播学院
    排版：林雨歆
    动图制作：蔡一凡
    责编：曾文萃
    厦门大学党委宣传部出品
    【示例二】
    文：郑巧燕
    摄影：苏彦凯、雷子歆、李佳彤、钟勋、郑伊韬、曾文希
    排版：郑巧燕、陈语涵
    责编：曾文萃
    厦门大学党委宣传部出品
    【示例三】
    感谢所有提供素材的小伙伴们！
    排版：郑巧燕
    责编：曾文萃
    厦门大学党委宣传部出品
    【示例四】
    来源：新华社、厦门日报、福建发布
    责编：张友友、曾文萃
    厦门大学党委宣传部出品
    """

    user_prompt = f"待提取的公众号文末原文：\n{content}"
    creator_list = llm_request(system_prompt, user_prompt, temperature=0.3, response_format="text")
    if creator_list == "None":
        return ""
    return creator_list

def format_creator_list_by_llm(creator_list: str) -> dict[str, list[str]]:
    """
    格式化作者列表字符串为字典
    :param creator_list: 作者列表字符串
    :return: 作者列表字典
    """

    system_prompt = """
    你是公众号创作者信息结构化提取助手，严格执行以下强制规则：
    1. 仅提取具体人名的创作个体，直接忽略个体中的：各类单位/组织名称、责编、出品版权行、感谢语、图片备注、来源单位、新闻机构、策划单位、支持单位等不含人名的条目；
    2. 只保留字段名与人名，组织、部门、机构、新闻出版社等文字全部丢弃；
    3. 同一字段下多个人名拆分为字符串数组，数组内使用英文双引号，逗号为英文逗号；
    4. 最终仅输出标准JSON文本，无任何多余文字、解释、换行注释；
    5. 原文无符合要求的人名条目或输入None，输出空对象{}；
    6. 字段名严格沿用原文标识，不要修改名称。
    7. 不要出现责编字段。
    【示例输入1】
    视频策划单位：党委宣传部
    视频支持单位：招生与考试办公室、新闻传播学院
    排版：林雨歆
    动图制作：蔡一凡
    责编：曾文萃
    厦门大学党委宣传部出品
    【示例输出1】
    {
        "排版": ["林雨歆"],
        "动图制作": ["蔡一凡"]
    }
    【示例输入2】
    文：郑巧燕、人民日报
    摄影：苏彦凯、雷子歆、李佳彤、钟勋、郑伊韬、曾文希、小夏图库
    排版：郑巧燕、陈语涵
    责编：曾文萃
    厦门大学党委宣传部出品
    【示例输出2】
    {
        "文": ["郑巧燕"],
        "摄影": ["苏彦凯", "雷子歆", "李佳彤", "钟勋", "郑伊韬", "曾文希"],
        "排版": ["郑巧燕", "陈语涵"]
    }
    【示例输入3】
    感谢所有提供素材的小伙伴们！
    部分素材来源于厦门日报
    文：蔡艺彤、席铃珊
    图：受访者提供
    责编：曾文萃
    厦门大学党委宣传部出品
    【示例输出3】
    {
        "文": ["蔡艺彤", "席铃珊"]
    }
    【示例输入4】
    None
    【示例输出4】
    {}
    """

    user_prompt = f"请处理下面的落款文本，按规则输出纯JSON：\n{creator_list}"
    formatted_creator_list = llm_request(system_prompt, user_prompt, temperature=0.3, response_format="json_object")

    try:
        json_text = formatted_creator_list.strip()
        # 处理可能的 markdown 代码块标记
        if json_text.startswith("```"):
            json_text = json_text[json_text.find("\n")+1:]
            if json_text.endswith("```"):
                json_text = json_text[:json_text.rfind("```")]
        # 尝试找到第一个 { 和最后一个 } 之间的内容
        start_idx = json_text.find("{")
        end_idx = json_text.rfind("}")
        if start_idx != -1 and end_idx != -1:
            json_text = json_text[start_idx:end_idx+1]
        formatted_creator_list = json.loads(json_text)
    except json.JSONDecodeError:
        formatted_creator_list = {}

    return formatted_creator_list
