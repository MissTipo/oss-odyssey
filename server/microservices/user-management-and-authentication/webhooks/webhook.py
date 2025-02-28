from fastapi import APIRouter, Request, HTTPException
import logging

router = APIRouter()

@router.post("/webhook")
async def github_webhook(request: Request):
    event_type = request.headers.get("X-GitHub-Event")
    signature = request.headers.get("X-Hub-Signature-256")
    
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload format")
    
    logging.info(f"Received GitHub event: {event_type}")
    logging.info(f"Payload: {payload}")
    
    # Process the event as needed.
    
    return {"status": "ok"}

