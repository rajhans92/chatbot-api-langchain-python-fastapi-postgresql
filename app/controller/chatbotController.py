from dotenv import load_dotenv
from fastapi import HTTPException
from app.helper.helper import db
from langchain.chat_models import init_chat_model
from app.controller.sementicSerachController import (
    embeddedText
)
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

def listofSummariazationMessages(noOfRow, sessionId):     
    listofSummariazationMessages = []
    try:
        summarizationMessage = db.query(ChatSummary).filter( ChatSummary.session_id == sessionId).order_by(ChatSummary.id.desc()).limit(noOfRow).all()

        for message in summarizationMessage:
            listofSummariazationMessages.append(message.summary_text)
            
        return listofSummariazationMessages
    
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
    
def StoreHitory(sessionId, userMessage, assistantMessage):
    try:
        # Store user message
        userChat = [
            ChatMessage(session_id=sessionId, role="user", message=userMessage),
            ChatMessage(session_id=sessionId, role="assistant", message=assistantMessage)
        ]
        db.add_all(userChat)
        db.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error storing chat history: " + str(e))
    
def callMidSummarization(sessionId):
    try:
        # Fetch all messages for the session
        messages = db.query(ChatMessage).filter(ChatMessage.session_id == sessionId, ChatMessage.is_summarized == 0).order_by(ChatMessage.message_order).all()
        
        if len(messages) != 0:

            total_tokens = sum(message.token_count for message in messages)

            if total_tokens > 3000:
                message_texts = [msg.message for msg in messages]

                # Create a summarization prompt
                summarization_prompt = f"Summarize the following conversation:\n\n{message_texts}"

                # Get the summary from the LLM
                summary_response = model.invoke(summarization_prompt)
                summary_text = summary_response.content if summary_response else "No summary available."
                summary_embedding = embeddedText(summary_text)

                # Store the summary in the database
                chat_summary = ChatSummary(session_id=sessionId, summary_text=summary_text, summary_embedding=summary_embedding, message_start_order=messages[0].message_order, message_end_order=messages[-1].message_order, token_count=total_tokens)
                db.add(chat_summary)
                db.commit()

                db.query(ChatMessage).filter(ChatMessage.session_id == sessionId).update({"is_summarized": 1})
                db.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error during mid-conversation summarization: " + str(e))
    
def callMemoryEvents(userId, sessionId):
    try:
        # Fetch all messages for the session
        # messages = db.query(ChatMessage).filter(ChatMessage.session_id == sessionId).order_by(ChatMessage.message_order).all()
        
        # for message in messages:
        #     memory_event = MemoryEvents(user_id=userId, text=message.message, text_embedding=embeddedText(message.message), importance_score=5)
        #     db.add(memory_event)

        # db.commit()
        print("Memory events created successfully for user_id:", userId)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error during memory event creation: " + str(e))