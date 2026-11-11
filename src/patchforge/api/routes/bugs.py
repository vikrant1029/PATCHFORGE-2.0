
from fastapi import APIRouter, HTTPException
from pathlib import Path
from datetime import datetime, timezone

from patchforge.agents.bug_detector import BugDetector

router = APIRouter(
    prefix="/bugs",
    tags=["Bug Intelligence"]
)


@router.post("/scan")
def scan_repository_bugs():

    try:
        project_root = Path.cwd()

        detector = BugDetector(str(project_root))

        report = detector.scan_repository()

        return {
            "success": True,
            "platform": "PATCHFORGE 2.0",
            "engine": "Bug Detector 2.0",
            "team": "KRYNEXA",
            "scan_timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "report": report
        }

    except (ValueError, OSError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Bug scanning failed: {error}"
        )
