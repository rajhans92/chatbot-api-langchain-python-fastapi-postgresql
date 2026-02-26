from dotenv import load_dotenv
from fastapi import FastAPI
from app.helper.databaseConnection import engine, Base

app  = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
@app.get("/")
def read_root():
    return {"Hello": "World"}
