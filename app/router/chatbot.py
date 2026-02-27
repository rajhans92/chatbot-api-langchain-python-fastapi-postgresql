from fastapi import APIRouter, Depends
from app.schema.chatbotSchema import HeaderDetail
from app.helper.helper import get_header_details
from app.controller.chatbotController import (
    chatHistoryList,
    listofSummariazationMessages,
    # messageTokenizer,
    # sementicSearch,
    # prepareChatPromptTemplate,
    # chatLLM,
    # reviewChatResult,
    # StoreHitory,
    # callMidSummarization,
    # callLongSummarization
)


router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/")
async def chatbot(message: str, getHeaderDetail: HeaderDetail = Depends(get_header_details)):
    last_n_messages = 30
    listofMessages = chatHistoryList(last_n_messages,getHeaderDetail["sessionId"],getHeaderDetail["sessionId"])
    lastSummariazationMessage = listofSummariazationMessages(getHeaderDetail["sessionId"])
    # currentMessageTokenizer = messageTokenizer(message)

    # sementicSearchResult = sementicSearch(lmessage,getHeaderDetail["sessionId"], getHeaderDetail["userId"])

    # preparedTemplate = prepareChatPromptTemplate(listofMessages, lastSummariazationMessage, sementicSearchResult, currentMessageTokenizer) 

    # chatResult = chatLLM(preparedTemplate)

    # reviewChatResult = reviewChatResult(chatResult)    

    # return {"response": reviewChatResult}

    # StoreHitory(getHeaderDetail["sessionId"], message, reviewChatResult)
    # callMidSummarization(getHeaderDetail["sessionId"])
    # callLongSummarization(getHeaderDetail["userId"], getHeaderDetail["sessionId"])

    return {"response": "This is a placeholder response. Replace it with actual chatbot logic."}