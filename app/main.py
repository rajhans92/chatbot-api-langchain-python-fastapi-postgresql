from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.helper.exceptionHelper import (
    http_exception_handler,
    validation_exception_handler,
    value_error_handler,
    global_exception_handler
)
from app.helper.databaseConnection import engine, Base

app  = FastAPI()

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



@app.get("/")
def read_root():
    return {"Hello": "World"}
