from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.helper.databaseConnection import get_db
from app.schema.chatbotSchema import HeaderDetail
from app.helper.helper import get_header_details
from app.controller.chatbotController import (
    chatHistoryList,
    listofSummariazationMessages,
    prepareChatPromptTemplate,
    chatLLM,
    StoreHitory,
    callMidSummarization,
    callMemoryEvents
)
from app.controller.sementicSerachController import (
    sementicSearch
)


router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/")
async def chatbot(background_tasks: BackgroundTasks,message: str, getHeaderDetail: HeaderDetail = Depends(get_header_details), db: AsyncSession = Depends(get_db)):
    last_n_messages = 30
    noOfRow = 3
    listofMessages = await chatHistoryList(last_n_messages,getHeaderDetail["sessionId"], db)
    summariazationMessage = listofSummariazationMessages(noOfRow, getHeaderDetail["sessionId"], db)
    sementicSearchResult = sementicSearch(message, getHeaderDetail["userId"])

    preparedTemplate = prepareChatPromptTemplate(message,listofMessages, summariazationMessage, sementicSearchResult) 

    chatResult = chatLLM(preparedTemplate)

    background_tasks.add_task(StoreHitory, getHeaderDetail["sessionId"], message, chatResult, db)
    background_tasks.add_task(callMidSummarization, getHeaderDetail["sessionId"], db)
    background_tasks.add_task(callMemoryEvents, getHeaderDetail["userId"], getHeaderDetail["sessionId"], db)

    return {
        "status": "success",
        "response": {
            "role": "assistant",
            "content": chatResult
        }
    }
