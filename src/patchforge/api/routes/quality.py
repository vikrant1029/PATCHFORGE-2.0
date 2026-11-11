
from fastapi import APIRouter, HTTPException

from patchforge.agents.code_analyzer import CodeQualityAnalyzer

router = APIRouter(
    prefix="/quality",
    tags=["Code Quality Intelligence"]
)


@router.get("/analyze")
async def analyze_code_quality():

    try:
        analyzer = CodeQualityAnalyzer(".")
        report = analyzer.analyze_repository()

        return {
            "success": True,
            "engine": "PATCHFORGE Code Quality Analyzer 2.0",
            "data": report
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@router.get("/status")
async def quality_status():

    return {
        "success": True,
        "module": "Code Quality Intelligence",
        "engine": "PATCHFORGE Code Analyzer 2.0",
        "status": "ONLINE"
    }
