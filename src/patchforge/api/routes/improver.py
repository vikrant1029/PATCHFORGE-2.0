
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from patchforge.agents.code_improver import CodeImprover
from patchforge.agents.code_analyzer import CodeQualityAnalyzer


router = APIRouter(
    prefix="/improver",
    tags=["AI Code Improvement"]
)


# ============================================================
# REQUEST MODELS
# ============================================================

class FixPreviewRequest(BaseModel):
    file_path: str = Field(..., min_length=1)


class FixApplyRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    approved: bool = False


class BackupRestoreRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    backup_path: str = Field(..., min_length=1)
    approved: bool = False


# ============================================================
# ENGINE
# ============================================================

def get_improver():
    return CodeImprover(".")


# ============================================================
# ANALYZE REPOSITORY
# ============================================================

@router.post("/analyze")
async def generate_improvements():
    try:
        analyzer = CodeQualityAnalyzer(".")
        quality_report = analyzer.analyze_repository()

        improver = get_improver()
        result = improver.improve_repository(quality_report)

        return {
            "success": True,
            "platform": "PATCHFORGE 2.0",
            "team": "KRYNEXA",
            "improvement_report": result
        }

    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# SAFE FIX PREVIEW
# ============================================================

@router.post("/preview")
async def preview_safe_fix(request: FixPreviewRequest):
    try:
        improver = get_improver()

        result = improver.preview_fix(request.file_path)

        return {
            "success": True,
            "platform": "PATCHFORGE 2.0",
            "team": "KRYNEXA",
            "preview_result": result
        }

    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# APPROVED SAFE FIX APPLY
# ============================================================

@router.post("/apply")
async def apply_safe_fix(request: FixApplyRequest):
    try:
        if not request.approved:
            raise HTTPException(
                status_code=403,
                detail="Explicit approval is required before applying a fix."
            )

        improver = get_improver()

        result = improver.apply_fix(
            request.file_path,
            approved=True
        )

        return {
            "success": True,
            "platform": "PATCHFORGE 2.0",
            "team": "KRYNEXA",
            "apply_result": result
        }

    except HTTPException:
        raise

    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# BACKUP RESTORE
# ============================================================

@router.post("/restore")
async def restore_safe_backup(request: BackupRestoreRequest):
    try:
        if not request.approved:
            raise HTTPException(
                status_code=403,
                detail="Explicit approval is required before restoring a backup."
            )

        improver = get_improver()

        result = improver.restore_backup(
            request.file_path,
            request.backup_path,
            approved=True
        )

        return {
            "success": True,
            "platform": "PATCHFORGE 2.0",
            "team": "KRYNEXA",
            "restore_result": result
        }

    except HTTPException:
        raise

    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# ENGINE STATUS
# ============================================================

@router.get("/status")
async def improver_status():
    try:
        return get_improver().get_status()

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
