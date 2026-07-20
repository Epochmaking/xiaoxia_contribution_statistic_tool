from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mitmproxy.http import HTTPFlow

from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests


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
    title = article["app_msg_ext_info"]["title"]
    content_url = article["app_msg_ext_info"]["content_url"]
    publishing_time = str(article["comm_msg_info"]["datetime"])
    _item_show_type = str(article["app_msg_ext_info"]["item_show_type"])
    _type = article_type_mapping.get(_item_show_type, "未知类型")
    author = article["app_msg_ext_info"]["author"]

    if not author:
        if _type == "小绿书":
            author = "小绿书"
        else:
            author = "转载"

    new_dict = {
        "title": title,
        "author": author,
        "publishing_time": publishing_time,
        "content_url": content_url,
        "type": _type,
    }

    return new_dict

def get_reader_stats(content_url: str, template_flow: "HTTPFlow") -> dict:
    """
    作用：
    1. 从公众号文末原文中提取读者统计信息
    :param content_url: 公众号文末原文URL
    :param cookies: 会话cookie
    :param user_agent: 用户代理
    :return: 读者统计信息字典
    """
    logger.info("try to get reader stats from %s", content_url)
    try:
        # 1. 解析链接参数
        content_url = content_url.replace("&amp;", "&")
        params = parse_qs(urlparse(content_url).query)
        biz = params["__biz"][0]
        mid = params["mid"][0]
        idx = params["idx"][0]
        sn = params["sn"][0]

        cookies_md = template_flow.request.cookies
        cookies_str = "; ".join(f"{k}={v}" for k, v in cookies_md.items(multi=True)) if cookies_md else ""

        appmsg_token_values = template_flow.request.query.get_all("appmsg_token")
        appmsg_token = appmsg_token_values[0] if appmsg_token_values else ""

        user_agent_values = template_flow.request.headers.get_all("User-Agent")
        user_agent = user_agent_values[0] if user_agent_values else ""

        headers = {
            "Cookie": cookies_str,
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
            "scene": "27",
            "is_only_read": "1",
            "is_temp_url": "0",
            "appmsg_type": "9",
        }

        logger.debug("\ncookies:\n%s\nuser-Agent:\n%s\ndata:\n%s\n", cookies_str, user_agent, data)

        stat = None
        resp = requests.post(api_url, headers=headers, data=data, timeout=10)
        logger.debug("get reader stats res: %s， status_code: %d", resp.text, resp.status_code)
        resp.raise_for_status()
        stat = resp.json()["appmsgstat"]

        # 4. 解取阅读量、点赞量、旧点赞量
        if stat is None:
            return {
                "view_count": 0,
                "like_count": 0,
                "old_like_count": 0,
                "share_num": 0,
                "comment_count": 0,
            }

        view_count = stat["read_num"] or 0
        like_count = stat["like_num"] or 0
        old_like_count = stat["old_like_num"] or 0
        share_num = stat["share_num"] or 0
        collect_count = stat["collect_num"] or 0


        return {
            "view_count": view_count, # 阅读量
            "heart_count": like_count, # 爱心量
            "like_count": old_like_count, # 在看量
            "share_count": share_num, # 分享量
            "collect_count": collect_count, # 收藏量
        }
    except Exception as e: # pylint: disable=broad-exception-caught
        logger.warning("get reader stats failed: %s", e)
        return {}

def persist_articles_to_db(article_list: list[dict]) -> None:
    """
    作用：
    将文章列表持久化到数据库
    """
    try:
        with get_session() as session:
            for article in article_list:
                if not article.get("type"):
                    article["type"] = "图文"
                article_in_db = Article(**article)
                article_in_db.publishing_time = datetime.fromtimestamp(int(article["publishing_time"])) # type: ignore
                session.add(article_in_db)
            session.commit()
    except Exception as e:
        logger.error("persist articles to db failed: %s", e)
        raise e

    logger.info(f"{len(article_list)} 篇文章已持久化到数据库")

def get_article_list_from_db() -> list[dict]:
    """从数据库获取文章列表"""
    with get_session() as session:
        articles = session.query(Article).all()
        article_list = [article.to_dict() for article in articles]
        return article_list
