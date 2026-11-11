
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["System Health"])


@router.get("/health")
async def health_check():
    return {
        "success": True,
        "project": "PATCHFORGE 2.0",
        "team": "KRYNEXA",
        "status": "OPERATIONAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0"
    }
