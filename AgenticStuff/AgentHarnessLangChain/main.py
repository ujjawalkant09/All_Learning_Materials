from fastapi import FastAPI
from dbs.database import session
app = FastAPI()

@app.get("/")
async def home_page():
    return {"data":"Home Page"}

@app.get("/create_tools")
async def create_tools():
    return {"status":"Done"}

@app.get("/create_agent")
async def create_agent():
    return {"status":"agent_created"}

@app.get("/bind_tools")
async def bind_tools():
    return {"status":"tools_binded"}


@app.get("/dbs")
def dbs():
    return {"data":"db"}