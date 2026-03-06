from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.helper.databaseConnection import get_db
from app.schema.chatbotSchema import (HeaderDetail,SessionRequest, HeaderDetailOnlyUser)
from app.helper.helper import (
    get_header_without_session_details, 
    get_header_with_session_details
    )
from app.controller.chatbotController import (
    chatHistoryList,
    listofSummariazationMessages,
    prepareChatPromptTemplate,
    chatLLM,
    storeHitory,
    callMidSummarization,
    callMemoryEvents,
    chatSessionIdCreate
)
from app.controller.sementicSerachController import (
    sementicSearch
)


router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/new-session")
async def new_chat_session(sessionData: SessionRequest, getHeaderDetail:HeaderDetailOnlyUser = Depends(get_header_without_session_details), db: AsyncSession = Depends(get_db)):
    userId = getHeaderDetail["userId"]

    sessionId = await chatSessionIdCreate(sessionData,getHeaderDetail["userId"], db)

    return {
        "status": "success",
        "message": f"New chat session started with sessionId: {sessionId} for userId: {userId}",
        "response": {
            sessionId: sessionId
        }
    }

@router.post("/")
async def chatbot(background_tasks: BackgroundTasks,message: str, getHeaderDetail: HeaderDetail = Depends(get_header_with_session_details), db: AsyncSession = Depends(get_db)):
    last_n_messages = 30
    noOfRow = 3
    listofMessages = await chatHistoryList(last_n_messages,getHeaderDetail["sessionId"], db)
    summariazationMessage = await listofSummariazationMessages(noOfRow, getHeaderDetail["sessionId"], db)
    sementicSearchResult = await sementicSearch(message, getHeaderDetail["sessionId"],getHeaderDetail["userId"],db)

    preparedTemplate = prepareChatPromptTemplate(message,listofMessages, summariazationMessage, sementicSearchResult) 

    chatResult = chatLLM(preparedTemplate)

    background_tasks.add_task(storeHitory, getHeaderDetail["sessionId"], message, chatResult, db)
    background_tasks.add_task(callMidSummarization, getHeaderDetail["sessionId"], db)
    background_tasks.add_task(callMemoryEvents, getHeaderDetail["userId"], getHeaderDetail["sessionId"], db)

    return {
        "status": "success",
        "response": {
            "role": "assistant",
            "content": chatResult
        }
    }
