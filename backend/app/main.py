from fastapi import FastAPI, Depends, HTTPException
from app.webhook import router as webhook_router
from app.ingestion import router as ingestion_router
from app.audit import router as audit_router
from app.conflict import router as conflict_router

app = FastAPI(
    title="SanchaarSetu API",
    description="Bidirectional sync middleware for Karnataka's Single Window System",
    version="1.0.0"
)

app.include_router(webhook_router.router, prefix="/api/v1/webhook", tags=["Webhook"])
app.include_router(ingestion_router.router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(audit_router.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(conflict_router.router, prefix="/api/v1/conflict", tags=["Conflict"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SanchaarSetu"}

@app.get("/")
async def root():
    return {"message": "Welcome to Sanchaar Setu API"}
