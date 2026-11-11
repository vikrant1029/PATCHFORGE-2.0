
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ==========================================
# PATCHFORGE 2.0 | TEAM KRYNEXA
# Autonomous AI Software Engineering Platform
# ==========================================

from patchforge.api.routes.health import router as health_router
from patchforge.api.routes.orchestrator import router as orchestrator_router
from patchforge.api.routes.repository import router as repository_router
from patchforge.api.routes.bugs import router as bugs_router
from patchforge.api.routes.quality import router as quality_router
from patchforge.api.routes.improver import router as improver_router

from patchforge.core.database import database
from patchforge.core.orchestrator import orchestrator


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

APP_NAME = "PATCHFORGE 2.0"
API_PREFIX = "/api/v1"
VERSION = "2.0.0"

app = FastAPI(
    title=APP_NAME,
    description=(
        "Autonomous AI Software Engineering Platform "
        "developed by Team KRYNEXA. "
        "Build. Evolve. Protect."
    ),
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# API ROUTER REGISTRATION
# ==========================================

app.include_router(health_router, prefix=API_PREFIX)
app.include_router(orchestrator_router, prefix=API_PREFIX)
app.include_router(repository_router, prefix=API_PREFIX)
app.include_router(bugs_router, prefix=API_PREFIX)
app.include_router(quality_router, prefix=API_PREFIX)
app.include_router(improver_router, prefix=API_PREFIX)


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/", tags=["System"])
async def root():
    return {
        "success": True,
        "project": APP_NAME,
        "team": "KRYNEXA",
        "mission": "Build. Evolve. Protect.",
        "platform": "AI Software Engineering",
        "architecture": "Multi-Agent AI",
        "status": "ONLINE",
        "version": VERSION,
        "documentation": "/docs"
    }


# ==========================================
# SYSTEM INFORMATION
# ==========================================

@app.get(f"{API_PREFIX}/system/info", tags=["System"])
async def system_info():
    return {
        "success": True,
        "name": APP_NAME,
        "team": "KRYNEXA",
        "version": VERSION,
        "architecture": "Multi-Agent",
        "modules": [
            "Health Monitoring",
            "AI Orchestrator",
            "Repository Intelligence",
            "Bug Detection",
            "Code Quality Analysis",
            "AI Code Improvement",
            "SQLite Database Intelligence"
        ],
        "status": "OPERATIONAL"
    }


# ==========================================
# SYSTEM STATUS
# ==========================================

@app.get(f"{API_PREFIX}/system/status", tags=["System"])
async def system_status():

    try:
        db_status = database.get_database_status()
        engine_status = orchestrator.get_system_status()

        return {
            "success": True,
            "platform": APP_NAME,
            "team": "KRYNEXA",
            "api": "OPERATIONAL",
            "status": "ONLINE",
            "version": VERSION,
            "database": db_status,
            "orchestrator": engine_status
        }

    except Exception as error:
        return {
            "success": False,
            "platform": APP_NAME,
            "status": "DEGRADED",
            "error": str(error)
        }


# ==========================================
# DATABASE INTELLIGENCE API
# ==========================================

@app.get(f"{API_PREFIX}/database/status", tags=["Database Intelligence"])
async def database_status():

    try:
        return {
            "success": True,
            "data": database.get_database_status()
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(error)}"
        )


@app.get(f"{API_PREFIX}/database/overview", tags=["Database Intelligence"])
async def database_overview():

    try:
        tasks = database.get_all_tasks()

        completed = sum(
            task["status"] == "completed"
            for task in tasks
        )

        failed = sum(
            task["status"] == "failed"
            for task in tasks
        )

        running = sum(
            task["status"] == "running"
            for task in tasks
        )

        return {
            "success": True,
            "data": {
                "total_tasks": len(tasks),
                "completed_tasks": completed,
                "failed_tasks": failed,
                "running_tasks": running,
                "pending_tasks": len(tasks) - completed - failed - running,
                "database": database.get_database_status()
            }
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Database overview failed: {str(error)}"
        )


@app.get(f"{API_PREFIX}/database/tasks", tags=["Database Intelligence"])
async def database_tasks():

    try:
        tasks = database.get_all_tasks()

        return {
            "success": True,
            "total": len(tasks),
            "tasks": tasks
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch database tasks: {str(error)}"
        )


@app.get(
    f"{API_PREFIX}/database/tasks/{{task_id}}",
    tags=["Database Intelligence"]
)
async def database_task_detail(task_id: str):

    try:
        task = database.get_task(task_id)

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found."
            )

        return {
            "success": True,
            "data": task
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# APPLICATION STARTUP
# ==========================================

@app.on_event("startup")
async def startup_event():

    print("=" * 55)
    print(" PATCHFORGE 2.0 STARTING...")
    print(" TEAM KRYNEXA")
    print(" BUILD. EVOLVE. PROTECT.")
    print(" CODE QUALITY ENGINE: REGISTERED")
    print(" AI CODE IMPROVER: REGISTERED")
    print(" SQLITE DATABASE: CONNECTED")
    print(" DATABASE INTELLIGENCE: REGISTERED")
    print("=" * 55)


# ==========================================
# APPLICATION SHUTDOWN
# ==========================================

@app.on_event("shutdown")
async def shutdown_event():
    print("PATCHFORGE 2.0 SHUTTING DOWN...")
