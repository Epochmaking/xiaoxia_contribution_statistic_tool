from datetime import datetime
from constants import MAX_ARTICLE_COUNT_PER_REQUEST
from models.mapping import article_type_mapping

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
