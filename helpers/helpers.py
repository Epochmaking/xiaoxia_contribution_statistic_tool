from datetime import datetime
import requests
from urllib.parse import urlparse, parse_qs

from constants import MAX_ARTICLE_COUNT_PER_REQUEST
from models.mapping import article_type_mapping
from models.article_models import Article

from database.db import get_session
from utils.logging import get_logger

logger = get_logger(__name__)

def parse_and_crop_article_list(
        articles: list[dict],
        target_time: datetime,
        current_offset: int,
        current_count: int,
    ) -> tuple[int, int]:
    """
    作用：
    1. 解析文章列表，仅保留title、content_url，author, datetime字段
    2. 裁剪文章列表，只保留指定月份的文章
    3. 返回下一步的offset和count
    (如果不再需要拉取更多文章，返回0, 0，条件是列表中出现了datetime小于target_month的文章，说明已经拉取到所有文章了)
    """
    to_stop = False
    target_month = target_time.month
    index_to_crop = []

    # 获取到的原始文章数量小于最大请求数量，说明已经到头了
    if current_count < MAX_ARTICLE_COUNT_PER_REQUEST:
        to_stop = True

    for i, article in enumerate(articles):
        datetime_stamp = article.get('comm_msg_info', {}).get('datetime', None)
        if datetime_stamp is None:
            raise ValueError("article datetime is None")
        datetime_obj = datetime.fromtimestamp(datetime_stamp)

        # 分两种情况，一种是晚于目标月份，一种是早于目标月份
        # 晚于目标月份，删除但不停止继续
        if datetime_obj.month > target_month:
            index_to_crop.append(i)
            continue
        # 早于目标月份，删除并停止继续
        if datetime_obj.month < target_month:
            to_stop = True
            index_to_crop.append(i)
            continue

        # 相同月份，保留并解析
        articles[i] = parse_article(article)

    # 删除指定索引的文章
    for i in index_to_crop[::-1]:
        articles.pop(i)

    # 如果需要停止继续，返回0, 0
    if to_stop:
        return 0, 0

    # 更新offset和count
    new_offset = current_offset + current_count
    new_count = MAX_ARTICLE_COUNT_PER_REQUEST

    return new_offset, new_count

def parse_article(article: dict) -> dict:
    """
    作用：
    1. 解析文章，仅保留title、content_url，author, datetime字段
    """
    logger.info("parse article: %s", article)
    new_dict = {
        "title": article["app_msg_ext_info"]["title"],
        "author": article["app_msg_ext_info"]["author"],
        "publishing_time": str(article["comm_msg_info"]["datetime"]),
        "content_url": article["app_msg_ext_info"]["content_url"],
        "type": article_type_mapping.get(str(article["app_msg_ext_info"]["item_show_type"]), "未知类型"),
    }

    return new_dict

def get_reader_stats(content_url: str, cookies: str, user_agent: str, appmsg_token: str) -> dict:
    """
    作用：
    1. 从公众号文末原文中提取读者统计信息
    :param content_url: 公众号文末原文URL
    :param cookies: 会话cookie
    :param user_agent: 用户代理
    :return: 读者统计信息字典
    """
    # 1. 解析链接参数
    params = parse_qs(urlparse(content_url).query)
    biz = params["__biz"][0]
    mid = params["mid"][0]
    idx = params["idx"][0]
    sn = params["sn"][0]

    headers = {
        "Cookie": cookies,
        "User-Agent": user_agent,
    }

    # 3. 请求阅读量接口
    api_url = "https://mp.weixin.qq.com/mp/getappmsgext"
    data = {
        "__biz": biz,
        "mid": mid,
        "idx": idx,
        "sn": sn,
        "appmsg_token": appmsg_token,
        "x5": "0",
        "scene": "27"
    }

    stat = None
    try:
        res = requests.post(api_url, headers=headers, data=data, timeout=10).json()
        stat = res["appmsgstat"]
    except Exception as e:
        logger.warning("get reader stats failed: %s", e)

    # 4. 解取阅读量、点赞量、旧点赞量
    if stat is None:
        return {
            "view_count": 0,
            "like_count": 0,
            "old_like_count": 0,
        }

    view_count = stat["read_num"] or 0
    like_count = stat["like_num"] or 0
    old_like_count = stat["old_like_num"] or 0


    return {
        "view_count": view_count,
        "like_count": like_count,
        "old_like_count": old_like_count,
    }

def persist_articles_to_db(article_list: list[dict]) -> None:
    """
    作用：
    将文章列表持久化到数据库
    """
    try:
        with get_session() as session:
            for article in article_list:
                article_in_db = Article(**article)
                article_in_db.publishing_time = datetime.fromtimestamp(int(article["publishing_time"])) # type: ignore
                session.add(article_in_db)
            session.commit()
    except Exception as e:
        logger.error("persist articles to db failed: %s", e)
        raise e

    logger.info(f"{len(article_list)} 篇文章已持久化到数据库")
