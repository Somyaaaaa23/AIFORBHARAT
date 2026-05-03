from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class AuditEntry(BaseModel):
    id: str
    ubid: str
    department_id: str
    action: str
    timestamp: datetime
    status: str
    payload_snapshot: dict

@router.get("/logs", response_model=List[AuditEntry])
async def get_audit_logs(ubid: Optional[str] = None):
    # Mock data
    return [
        {
            "id": "1",
            "ubid": ubid or "UBID-12345",
            "department_id": "FACTORIES-01",
            "action": "ADDRESS_SYNC",
            "timestamp": datetime.now(),
            "status": "SUCCESS",
            "payload_snapshot": {"old": "...", "new": "..."}
        }
    ]
