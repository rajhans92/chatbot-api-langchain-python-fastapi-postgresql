from fastapi import APIRouter, Depends, BackgroundTasks
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
async def chatbot(background_tasks: BackgroundTasks,message: str, getHeaderDetail: HeaderDetail = Depends(get_header_details)):
    last_n_messages = 30
    noOfRow = 3
    listofMessages = chatHistoryList(last_n_messages,getHeaderDetail["sessionId"],getHeaderDetail["sessionId"])
    summariazationMessage = listofSummariazationMessages(noOfRow, getHeaderDetail["sessionId"])
    sementicSearchResult = sementicSearch(message, getHeaderDetail["userId"])

    preparedTemplate = prepareChatPromptTemplate(message,listofMessages, summariazationMessage, sementicSearchResult) 

    chatResult = chatLLM(preparedTemplate)

    background_tasks.add_task(StoreHitory, getHeaderDetail["sessionId"], message, chatResult)
    background_tasks.add_task(callMidSummarization, getHeaderDetail["sessionId"])
    background_tasks.add_task(callMemoryEvents, getHeaderDetail["userId"], getHeaderDetail["sessionId"])

    return {
        "status": "success",
        "response": {
            "role": "assistant",
            "content": chatResult
        }
    }
