from fastapi import APIRouter, Depends
from app.schema.chatbotSchema import HeaderDetail
from app.helper.helper import get_header_details
from app.controller.chatbotController import (
    chatHistoryList,
    listofSummariazationMessages,
    prepareChatPromptTemplate,
    chatLLM,
    # reviewChatResult,
    # StoreHitory,
    # callMidSummarization,
    # callLongSummarization
)
from app.controller.sementicSerachController import (
    sementicSearch
)


router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/")
async def chatbot(message: str, getHeaderDetail: HeaderDetail = Depends(get_header_details)):
    last_n_messages = 30
    listofMessages = chatHistoryList(last_n_messages,getHeaderDetail["sessionId"],getHeaderDetail["sessionId"])
    summariazationMessage = listofSummariazationMessages(getHeaderDetail["sessionId"])
    sementicSearchResult = sementicSearch(message, getHeaderDetail["userId"])

    preparedTemplate = prepareChatPromptTemplate(message,listofMessages, summariazationMessage, sementicSearchResult) 

    chatResult = chatLLM(preparedTemplate)

    return {
        "status": "success",
        "response": {
            "role": "assistant",
            "content": chatResult
        }
    }

    # StoreHitory(getHeaderDetail["sessionId"], message, reviewChatResult)
    # callMidSummarization(getHeaderDetail["sessionId"])
    # callLongSummarization(getHeaderDetail["userId"], getHeaderDetail["sessionId"])

    return {"response": "This is a placeholder response. Replace it with actual chatbot logic."}