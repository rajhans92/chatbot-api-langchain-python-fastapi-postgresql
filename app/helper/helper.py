from fastapi import Header, HTTPException
from app.schema.header_schema import HeaderDetail

def get_header_details(header: HeaderDetail =  Header(...)):     
    try:
        sessionId = header.sessionId
        userId = header.userId
        return {"sessionId": sessionId, "userId": userId}
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid User Session")