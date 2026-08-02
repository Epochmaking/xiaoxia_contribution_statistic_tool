from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import Base

class Article(Base):
    """
    文章模型
    文章模型包含文章的标题、作者、发布时间时间、内容URL、类型、作者列表、阅读量等字段。
    """
    __tablename__ = 'articles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str] = mapped_column(String(64), index=True, nullable=True)
    publishing_time: Mapped[DateTime] = mapped_column(DateTime, index=True)
    content_url: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[str] = mapped_column(String(16), index=True)
    creators_list: Mapped[str] = mapped_column(String(512), index=True, nullable=True)
    formatted_creators_list: Mapped[str] = mapped_column(String(512), index=True, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    like_count: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    heart_count: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    share_count: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    collect_count: Mapped[int] = mapped_column(Integer, nullable=True, default=None)

class Creator(Base):
    """
    作者模型
    """
    __tablename__ = 'creators'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    is_xiaoxia: Mapped[bool] = mapped_column(Boolean, index=True)
    fee: Mapped[int] = mapped_column(Integer, nullable=True, default=None)

class ArticleCreatorLink(Base):
    """
    文章作者关联模型
    """
    __tablename__ = 'article_creator_links'

    article_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
