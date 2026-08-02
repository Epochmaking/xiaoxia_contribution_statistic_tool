import json
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from database.db import get_session
from models.article_models import Article, Creator, ArticleCreatorLink
from constants import FEE_BASE, XIAOXIA_MEMBERS

def calculate_fee() -> None:
    """
    计算稿费
    """
    with get_session() as session:
        articles = session.query(Article).all()
        _collect_creators(articles, session)
        _link_creators_to_articles(articles, session)
        _calculate_fee(session)  

def _collect_creators(articles: list[Article], session: Session)  -> None:
    """
    收集所有文章的作者，并写入数据库Creators表
    """
    creators_set = set()
    for article in articles:
        creators_dict: dict[str, list[str]] | None = json.loads(article.formatted_creators_list)
        if creators_dict is None:
            continue
        creators_set.update(_dict_to_list(creators_dict))
    for creator in creators_set:
        creator = Creator(name=creator)
        if XIAOXIA_MEMBERS is None or creator.name in XIAOXIA_MEMBERS:
            creator.is_xiaoxia = True
        else:
            creator.is_xiaoxia = False
        session.add(creator)
    session.commit()

def _link_creators_to_articles(articles: list[Article], session: Session) -> None:
    """
    关联所有文章的作者到ArticleCreatorLinks表
    """
    for article in articles:
        creators_dict: dict[str, list[str]] | None = json.loads(article.formatted_creators_list)
        if creators_dict is None:
            continue
        relevant_creators = session.scalars(
            select(Creator).where(Creator.name.in_(_dict_to_list(creators_dict)))
        ).all()
        for creator in relevant_creators:
            session.add(ArticleCreatorLink(article_id=article.id, creator_id=creator.id))
    session.commit()

def _calculate_fee(session: Session) -> None:
    """
    计算所有作者的稿费
    """
    for creator in session.query(Creator).all():
        involve_count = session.execute(
            select(func.count()).where(ArticleCreatorLink.creator_id == creator.id) # pylint: disable=not-callable
        ).scalar_one()
        creator.fee = FEE_BASE * involve_count
        session.add(creator)
    session.commit()

def _dict_to_list(d: dict[str, list[str]]) -> list:
    """
    将作者json扁平化转换为列表，每个元素为作者姓名
    """
    return [elem for lst in d.values() for elem in lst]