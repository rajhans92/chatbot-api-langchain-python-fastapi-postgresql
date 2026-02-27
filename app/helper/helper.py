from fastapi import Request, HTTPException


def get_header_details(request: Request):     
    try:
        sessionId = request.headers.get("sessionId")
        userId = request.headers.get("userId")
        return {"sessionId": sessionId, "userId": userId}
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid User Session")