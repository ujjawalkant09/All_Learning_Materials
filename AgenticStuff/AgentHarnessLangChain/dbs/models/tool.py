from sqlalchemy import Column, Integer, String, Text, JSON, Boolean
from dbs.database import Base
from .base_models import TimestampMixin

class Tool(Base, TimestampMixin):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    tool_type = Column(
        String(50),
        nullable=False,
        default="SCRIPT",
    )
    code = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
