from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.helper.config import (
    API_VERSION,
    API_BASE_NAME
)
from app.helper.exceptionHelper import (
    http_exception_handler,
    validation_exception_handler,
    value_error_handler,
    global_exception_handler
)
from app.helper.databaseConnection import initialize_database
from app.router import (chatbot)

app  = FastAPI()

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.post("/setup/database", tags=["system"])
async def setup_database():
    try:
        return await initialize_database()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database setup failed: {exc}",
        ) from exc

app.include_router(chatbot.router, prefix=f'/{API_BASE_NAME}/{API_VERSION}')

@app.get("/")
def read_root():
    return {"Hello": "World"}
