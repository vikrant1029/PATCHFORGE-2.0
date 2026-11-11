
from pathlib import Path

from fastapi import APIRouter, HTTPException

from patchforge.agents.repository_analyzer import (
    RepositoryAnalyzer
)


router = APIRouter(
    prefix="/repository",
    tags=["Repository Intelligence"]
)


def get_project_root() -> Path:

    # repository.py -> routes -> api -> patchforge -> src -> project root

    return Path(__file__).resolve().parents[4]


@router.get("/scan")
async def scan_repository():

    try:

        project_root = get_project_root()

        analyzer = RepositoryAnalyzer(
            root_path=str(project_root)
        )

        report = analyzer.analyze()

        return {
            "success": True,
            "message": "Repository analysis completed successfully",
            "data": report
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except OSError:

        raise HTTPException(
            status_code=500,
            detail="Repository scanning failed"
        )


@router.get("/summary")
async def repository_summary():

    try:

        project_root = get_project_root()

        analyzer = RepositoryAnalyzer(
            root_path=str(project_root)
        )

        report = analyzer.analyze()

        return {
            "success": True,
            "repository": report["repository"],
            "total_files": report["total_files"],
            "total_size_kb": report["total_size_kb"],
            "extensions": report["extensions"],
            "status": report["status"]
        }

    except (ValueError, OSError) as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
