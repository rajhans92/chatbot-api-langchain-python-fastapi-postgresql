from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.helper.databaseConnection import get_db
from app.schema.chatbotSchema import (HeaderDetail,SessionRequest, HeaderDetailOnlyUser)
from app.helper.config import (
    LAST_N_MESSAGES,
    NO_OF_ROW_SUMMARY
)
from app.helper.helper import (
    get_header_without_session_details, 
    get_header_with_session_details
    )
from app.controller.chatbotController import (
    chatHistoryList,
    listofSummariazationMessages,
    prepareChatPromptTemplate,
    stream_llm_response,
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
async def chatbot(message: str, getHeaderDetail: HeaderDetail = Depends(get_header_with_session_details), db: AsyncSession = Depends(get_db)):
    last_n_messages = LAST_N_MESSAGES
    noOfRow = NO_OF_ROW_SUMMARY
    listofMessages, summariazationMessage, sementicSearchResult = await asyncio.gather(
        chatHistoryList(last_n_messages, getHeaderDetail["sessionId"], db),
        listofSummariazationMessages(noOfRow, getHeaderDetail["sessionId"], db),
        sementicSearch(message, getHeaderDetail["sessionId"], getHeaderDetail["userId"], db)
    )

    preparedTemplate = prepareChatPromptTemplate(message,listofMessages, summariazationMessage, sementicSearchResult) 

    return StreamingResponse(
        stream_llm_response(preparedTemplate, getHeaderDetail["userId"], getHeaderDetail["sessionId"], message, db),
        media_type="text/event-stream"
    )