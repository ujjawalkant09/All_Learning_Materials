from sqlalchemy import Column, Integer, ForeignKey
from dbs.database import Base
from .base_models import TimestampMixin

class AgentTool(Base,TimestampMixin):
    __tablename__ = "agent_tools"

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        primary_key=True,
    )
    tool_id = Column(
        Integer,
        ForeignKey("tools.id"),
        primary_key=True,
    )
