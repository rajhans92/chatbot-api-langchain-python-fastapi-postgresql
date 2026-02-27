from fastapi import HTTPException
from app.helper.helper import db
from app.model.chatModel import (
    ChatMessage,
    ChatSummary
)

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
    

def messageTokenizer(message):
    # This is a placeholder function. You should replace it with your actual implementation.
    # For example, you might want to use a tokenizer from a library like Hugging Face's Transformers.
    return len(message.split())  # Simple tokenization based on whitespace

def sementicSearch(message, sessionId, userId):
    # This is a placeholder function. You should replace it with your actual implementation.
    # For example, you might want to perform a semantic search using a vector database or an embedding model.
    return [
        {"role": "assistant", "content": "Relevant information based on semantic search: ..."},
        # Add more relevant messages as needed
    ]

