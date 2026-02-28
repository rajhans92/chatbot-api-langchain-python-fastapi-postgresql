from dotenv import load_dotenv
from fastapi import HTTPException
from app.helper.helper import db
from langchain.chat_models import init_chat_model
from app.model.chatModel import (
    ChatMessage,
    ChatSummary
)
import json
load_dotenv()

model = init_chat_model("gpt-4.1")

def chatHistoryList(lastNmessages,sessionId):
    
    listOfMessageWithRole = []

    try:
        listOfMessage = db.query(ChatMessage).filter( ChatMessage.session_id == sessionId).order_by(ChatMessage.message_order.desc()).limit(lastNmessages).all()

        for message in listOfMessage:
            listOfMessageWithRole.append({"role": message.role, "content": message.message})

        return listOfMessageWithRole
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching chat history: " + str(e))

def listofSummariazationMessages(sessionId):     
    try:
        summarizationMessage = db.query(ChatSummary).filter( ChatSummary.session_id == sessionId).order_by(ChatSummary.id.desc()).first()

        return summarizationMessage[0].summary_text if summarizationMessage else ""
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching summarized messages: " + str(e))
    
def prepareChatPromptTemplate(queryMessage, listOfMessages, summariazationMessage, sementicSearchResult):
    try:
        promptTemplate = f"""
        You are a helpful assistant. Use the following information to answer the user's question.

        1. Chat History (most recent messages first):
        {listOfMessages}

        2. Summarization of previous conversation:
        {summariazationMessage}

        3. Relevant information from user's documents:
        {sementicSearchResult}

        Now, based on the above information, answer the user's question.

        Question: {queryMessage}
        """

        return promptTemplate
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error preparing chat prompt template: " + str(e))  

def chatLLM(preparedTemplate):
    try:
        response = model.invoke(preparedTemplate)
        return response.content if response else "Sorry, I couldn't generate a response at this time."
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error during LLM processing: " + str(e))