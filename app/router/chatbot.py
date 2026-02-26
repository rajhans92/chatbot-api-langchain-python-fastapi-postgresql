from fastapi import APIRouter, Depends
from app.helper.helper import get_header_details


router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/")
async def chatbot(message: str, getHeaderDetail: Depends(get_header_details)):
    last_n_messages = 30
    listofMessages = chatHistoryList(last_n_messages,getHeaderDetail["sessionId"])
    lastSummariazationMessage = listofSummariazationMessages(getHeaderDetail["sessionId"])
    currentMessageTokenizer = messageTokenizer(message)

    sementicSearchResult = sementicSearch(lmessage,getHeaderDetail["sessionId"], getHeaderDetail["userId"])

    preparedTemplate = prepareChatPromptTemplate(listofMessages, lastSummariazationMessage, sementicSearchResult, currentMessageTokenizer) 

    chatResult = chatLLM(preparedTemplate)

    reviewChatResult = reviewChatResult(chatResult)    

    return {"response": reviewChatResult}

    StoreHitory(getHeaderDetail["sessionId"], message, reviewChatResult)
    callMidSummarization(getHeaderDetail["sessionId"])
    callLongSummarization(getHeaderDetail["userId"], getHeaderDetail["sessionId"])