from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Conflict(BaseModel):
    id: str
    ubid: str
    field: str
    sws_value: str
    dept_value: str
    timestamp: str

@router.get("/pending", response_model=List[Conflict])
async def get_conflicts():
    return [
        {
            "id": "c1",
            "ubid": "UBID-99",
            "field": "legal_name",
            "sws_value": "Acme Corp Ltd",
            "dept_value": "Acme Industries",
            "timestamp": "2026-05-03T10:00:00Z"
        }
    ]

@router.post("/resolve/{conflict_id}")
async def resolve_conflict(conflict_id: str, resolution: str):
    return {"status": "resolved", "conflict_id": conflict_id, "chosen": resolution}
