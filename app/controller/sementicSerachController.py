from dotenv import load_dotenv
from fastapi import HTTPException
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select
from app.helper.helper import db
from app.model.chatModel import (
    ChatSummary,
    MemoryEvents
)
load_dotenv()

embeddings = OpenAIEmbeddings(
    model="GPT-4o mini"
)

def sementicSearch(message, sessionId, userId):
    
    try:
        listOfMessage = []
        query_vector = embeddings.embed_query(message)
        stmt = (
            select(MemoryEvents)
            .where(MemoryEvents.user_id == userId)
            .order_by(MemoryEvents.text_embedding.cosine_distance(query_vector))
            .limit(2)
        )

        result = db.execute(stmt)
        results = result.scalars().all()
        
        for r in results:
            listOfMessage.append(r.text)

        stmt = (
            select(ChatSummary)
            .where(ChatSummary.sessionId == sessionId)
            .order_by(ChatSummary.summary_embedding.cosine_distance(query_vector))
            .limit(4)
        )

        result = db.execute(stmt)
        results = result.scalars().all()
        
        for r in results:
            listOfMessage.append(r.summary_text)

        return listOfMessage
    except Exception as e:
        print(f"Error during semantic search: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during semantic search.")
                
    
def embeddedText(text):
    try:
        return embeddings.embed_query(text)
    except Exception as e:
        print(f"Error during text embedding: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during text embedding.")