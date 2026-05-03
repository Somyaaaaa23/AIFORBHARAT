from fastapi import APIRouter
import logging

router = APIRouter()

@router.get("/status")
async def ingestion_status():
    return {
        "tier1": "active",
        "tier2": "polling",
        "tier3": "ready"
    }

@router.post("/trigger/{tier}")
async def trigger_ingestion(tier: int):
    if tier not in [1, 2, 3]:
        return {"error": "Invalid tier"}
    return {"status": f"Tier {tier} ingestion triggered"}
