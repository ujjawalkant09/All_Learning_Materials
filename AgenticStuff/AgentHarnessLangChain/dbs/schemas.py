import ast
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from datetime import datetime

# Tool Schemas
class ToolCreate(BaseModel):
    name: str
    description: str
    tool_type: Optional[str] = "SCRIPT"
    code: str
    tags: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = True

    @field_validator("code")
    @classmethod
    def validate_python_code(cls, value: str) -> str:
        try:
            ast.parse(value)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e.msg} (line {e.lineno})")
        return value

class ToolResponse(BaseModel):
    id: int
    name: str
    description: str
    tool_type: str
    code: str
    tags: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Agent Schemas
class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    model: str
    is_active: Optional[bool] = True

class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    system_prompt: str
    model: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ToolExecute(BaseModel):
    id:int
    inp_data:Optional[Dict[str,Any]] = None