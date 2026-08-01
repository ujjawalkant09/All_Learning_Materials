import ast
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean
from sqlalchemy.orm import validates
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

    @validates("code")
    def validate_code(self, key, value):
        try:
            ast.parse(value)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax in 'code': {e.msg} (line {e.lineno})")
        return value
