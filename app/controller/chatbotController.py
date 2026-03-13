from dotenv import load_dotenv
import asyncio
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from langchain.chat_models import init_chat_model
from app.helper.config import (
    LLM_MODEL
)
from app.controller.sementicSerachController import (
    embeddedText
)
from app.model.chatModel import (
    ChatMessage,
    ChatSummary,
    ChatSession,
    MemoryEvents
)
load_dotenv()

 
model = init_chat_model(LLM_MODEL)

async def chatSessionIdCreate(sessionData, userId, db):
    try:
        
                # Store the summary in the database
        chat_session = ChatSession(user_id=userId, title=sessionData.title, model_name=sessionData.modelName)
        db.add(chat_session)

        await db.flush()   # sends INSERT to DB

        sessionId = chat_session.id
        await db.commit()

        return sessionId
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating chat session: " + str(e))

async def chatHistoryList(lastNmessages,sessionId, db):
    
    listOfMessageWithRole = []
    try:
        query = (
            select(ChatMessage)
            .filter(ChatMessage.session_id == sessionId)
            .order_by(ChatMessage.message_order.desc())
            .limit(lastNmessages)
        )
        result = await db.execute(query)
        # .scalars() extracts the ChatMessage objects from the result rows
        listOfMessage = result.scalars().all()
        
        for message in listOfMessage:
            listOfMessageWithRole.append({"role": message.role, "content": message.message})

        return listOfMessageWithRole
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching chat history: " + str(e))

async def listofSummariazationMessages(noOfRow, sessionId, db):     
    listofSummariazationMessages = []
    try:

        query = (
            select(ChatSummary)
            .filter( ChatSummary.session_id == sessionId)
            .order_by(ChatSummary.id.desc())
            .limit(noOfRow)
        )
        result = await db.execute(query)
        # .scalars() extracts the ChatMessage objects from the result rows
        summarizationMessage = result.scalars().all()

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

async def stream_llm_response(preparedTemplate, userId, sessionId, message, db):
    try:
        full_response = ""

        async for token in model.astream(preparedTemplate):

            full_response += token

            yield token

        # store conversation after completion
        asyncio.create_task(
            storeHitory(sessionId, message, full_response, db)
        )

        asyncio.create_task(
            callMidSummarization(sessionId, db)
        )

        asyncio.create_task(
            callMemoryEvents(userId, sessionId, db)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error during LLM processing: " + str(e))
    
async def storeHitory(sessionId, userMessage, assistantMessage, db):
    try:

        message_order_result = await db.execute(
            select(func.max(ChatMessage.message_order))
            .where(ChatMessage.session_id == sessionId)
        )

        max_order = (message_order_result.scalar() or 0) + 1

        # Store user message
        userChat = [
            ChatMessage(session_id=sessionId, role="user", message=userMessage, tokens_used=len(userMessage.split()), message_order=max_order, is_summarized=0),
            ChatMessage(session_id=sessionId, role="assistant", message=assistantMessage, tokens_used=len(assistantMessage.split()), message_order=(max_order+1), is_summarized=0)
        ]
        db.add_all(userChat)
        await db.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error storing chat history: " + str(e))
    
async def callMidSummarization(sessionId, db):
    try:
        # Fetch all messages for the session
        
        query = (
            select(ChatMessage)
            .filter( ChatMessage.session_id == sessionId, ChatMessage.is_summarized == 0)
            .order_by(ChatMessage.message_order)
        )
        result = await db.execute(query)
        # .scalars() extracts the ChatMessage objects from the result rows
        messages = result.scalars().all()

        if len(messages) != 0:

            total_tokens = sum(message.tokens_used for message in messages)

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
                await db.commit()

                db.query(ChatMessage).filter(ChatMessage.session_id == sessionId).update({"is_summarized": 1})
                await db.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error during mid-conversation summarization: " + str(e))
    
def callMemoryEvents(userId, sessionId, db):
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