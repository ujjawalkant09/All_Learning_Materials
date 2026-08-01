from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from dbs.database import get_db
from dbs.models import Tool
from dbs.schemas import ToolCreate, ToolResponse

app = FastAPI()

@app.get("/")
async def home_page():
    return {"data":"Home Page"}

@app.post("/create_tools", response_model=ToolResponse)
async def create_tools(tool_in: ToolCreate, db: Session = Depends(get_db)):
    existing_tool = db.query(Tool).filter(Tool.name == tool_in.name).first()
    if existing_tool:
        raise HTTPException(status_code=400, detail="Tool with this name already exists")
    
    new_tool = Tool(
        name=tool_in.name,
        description=tool_in.description,
        tool_type=tool_in.tool_type,
        code=tool_in.code,
        tags=tool_in.tags,
        is_active=tool_in.is_active
    )
    
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)
    
    return new_tool

@app.get("/create_agent")
async def create_agent():
    return {"status":"agent_created"}

@app.get("/bind_tools")
async def bind_tools():
    return {"status":"tools_binded"}


@app.get("/dbs")
def dbs():
    return {"data":"db"}