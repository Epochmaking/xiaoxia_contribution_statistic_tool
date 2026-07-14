from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime

class Base(DeclarativeBase):
    """
    基础模型
    """
    create_time = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        """
        将模型转换为字典
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
