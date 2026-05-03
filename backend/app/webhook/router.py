from fastapi import APIRouter, Request, HTTPException
import json
import logging

router = APIRouter()

# Simple mock for Redis idempotency
processed_events = set()

@router.post("/sws")
async def sws_webhook_listener(request: Request):
    payload = await request.json()
    
    # 1. Idempotency Check
    event_id = payload.get("event_id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Missing event_id")
    
    if event_id in processed_events:
        return {"status": "skipped", "reason": "already processed"}
    
    # 2. PII Scrubbing (Call PII service)
    # 3. Queue to Kafka
    
    processed_events.add(event_id)
    
    return {
        "status": "accepted",
        "event_id": event_id,
        "message": "Event queued for transformation"
    }
