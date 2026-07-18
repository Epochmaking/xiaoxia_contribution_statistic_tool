from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants import TEMP_DB_PATH
from models.base_model import Base

from utils.logging import get_logger

logger = get_logger(__name__)

ENGINE = None

def init_database():
    """
    初始化数据库
    """
    global ENGINE # pylint: disable=global-statement
    db_path = TEMP_DB_PATH
    # db_path = Path(__file__).parent.parent / 'xiaoxia_tool.db' # 测试路径
    try:
        if db_path.exists():
            db_path.unlink()
        if ENGINE is None:
            ENGINE = create_engine(f"sqlite:///{db_path}")

        # 创建数据库表
        Base.metadata.create_all(ENGINE)
        logger.info("数据库初始化成功")

    except Exception as e: # pylint: disable=broad-exception-caught
        logger.error(f"数据库初始化失败, {e}")
        raise e

def get_session():
    """
    获取数据库会话

    :return: 数据库会话
    """
    if ENGINE is None:
        init_database()
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
    return session_local()
