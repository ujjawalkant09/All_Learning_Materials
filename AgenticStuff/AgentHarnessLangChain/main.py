from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from dbs.database import get_db
from dbs.models import Tool
from dbs.schemas import ToolCreate, ToolResponse, AgentCreate, AgentResponse,ToolExecute
from typing import Optional

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

@app.get("/tools")
def get_all_tools(db: Session = Depends(get_db),is_active:Optional[bool] = True):
    if is_active:
        tools = db.query(Tool).filter(Tool.is_active == True).all()
    else:
        tools = db.query(Tool).all()
    return tools

@app.get("/tool/{tool_id}")
def get_tool_by_id(tool_id: int, db: Session = Depends(get_db)):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@app.put("/tool/{tool_id}")
def update_tool(tool_id: int, tool_in: ToolCreate, db: Session = Depends(get_db)):
    existing_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    existing_tool.name = tool_in.name
    existing_tool.description = tool_in.description
    existing_tool.tool_type = tool_in.tool_type
    existing_tool.code = tool_in.code
    existing_tool.tags = tool_in.tags
    existing_tool.is_active = tool_in.is_active
    db.commit()
    db.refresh(existing_tool)
    
    return existing_tool

@app.delete("/tool/{tool_id}")
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    existing_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    db.delete(existing_tool)
    db.commit()
    
    return {"message": "Tool deleted successfully"}

# Agent Endpoints
@app.post("/agents")
async def create_agent(agent_in:AgentResponse, db: Session = Depends(get_db)):
    existing_agent = db.query(Agent).filter(Agent.name == agent_in.name).first()
    if existing_agent:
        raise HTTPException(status_code=400, detail="Agent with this name already exists")
    new_agent = Agent(
        name=agent_in.name,
        description=agent_in.description,
        system_prompt=agent_in.system_prompt,
        model=agent_in.model,
        is_active=agent_in.is_active
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent

@app.get("/agents")
async def get_all_agents(db: Session = Depends(get_db), is_active: Optional[bool] = True):
    if is_active:
        agents = db.query(Agent).filter(Agent.is_active == True).all()
    else:
        agents = db.query(Agent).all()
    return agents

@app.get("/agent/{agent_id}")
async def get_agent_by_id(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.put("/agent/{agent_id}")
async def update_agent(agent_id: int, agent_in: AgentCreate, db: Session = Depends(get_db)):
    existing_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    existing_agent.name = agent_in.name
    existing_agent.description = agent_in.description
    existing_agent.system_prompt = agent_in.system_prompt
    existing_agent.model = agent_in.model
    existing_agent.is_active = agent_in.is_active
    db.commit()
    db.refresh(existing_agent)
    
    return existing_agent

@app.delete("/agent/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    existing_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(existing_agent)
    db.commit()
    return {"message": "Agent deleted successfully"}

# Agent-Tool Binding Endpoints
@app.post("/agent_tools")
async def create_agent_tool(agent_id: int, tool_id: int, db: Session = Depends(get_db)):
    existing_binding = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id,
        AgentTool.tool_id == tool_id
    ).first()
    if existing_binding:
        raise HTTPException(status_code=400, detail="This agent-tool binding already exists")
    # Check if agent and tool exist
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    new_binding = AgentTool(
        agent_id=agent_id,
        tool_id=tool_id
    )
    db.add(new_binding)
    db.commit()
    return {"message": "Tool bound to agent successfully", "agent_id": agent_id, "tool_id": tool_id}

@app.get("/agent/{agent_id}/tools")
async def get_agent_tools(agent_id: int, db: Session = Depends(get_db)):
    # Get all tools bound to this agent
    tools = db.query(Tool).join(AgentTool).filter(
        AgentTool.agent_id == agent_id
    ).all()
    return tools

@app.get("/tools/{tool_id}/agents")
async def get_tools_agents(tool_id: int, db: Session = Depends(get_db)):
    # Get all agents bound to this tool
    agents = db.query(Agent).join(AgentTool).filter(
        AgentTool.tool_id == tool_id
    ).all()
    return agents

@app.delete("/agent_tools/{agent_id}/{tool_id}")
async def delete_agent_tool(agent_id: int, tool_id: int, db: Session = Depends(get_db)):
    binding = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id,
        AgentTool.tool_id == tool_id
    ).first()
    
    if not binding:
        raise HTTPException(status_code=404, detail="Agent-tool binding not found")
    
    db.delete(binding)
    db.commit()
    
    return {"message": "Binding deleted successfully"}

@app.post("/execute_tools")
def execute_tools(
    tool_in: ToolExecute,
    db: Session = Depends(get_db),
):
    tool = db.query(Tool).filter(Tool.id == tool_in.id).first()

    if not tool:
        raise HTTPException(404, "Tool not found")

    namespace = {}

    exec(tool.code, namespace)

    if "execute" not in namespace:
        raise HTTPException(
            400,
            "Tool must define execute() function"
        )

    execute_fn = namespace["execute"]
    result = execute_fn(**(tool_in.inp_data or {}))

    return {
        "result": result
    }
