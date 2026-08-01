from sqlalchemy import Column, Integer, String, Text, Boolean
from dbs.database import Base
from .base_models import TimestampMixin

class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    model = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
