
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from patchforge.core.orchestrator import orchestrator, TaskStatus

router = APIRouter(
    prefix="/orchestrator",
    tags=["AI Orchestrator"]
)

class IssueRequest(BaseModel):
    issue: str = Field(
        min_length=5,
        max_length=5000,
        description="Describe the software issue"
    )

@router.post("/plan")
async def create_plan(request: IssueRequest):
    try:
        plan = orchestrator.create_plan(request.issue)

        return {
            "success": True,
            "message": "Execution plan generated",
            "data": plan.model_dump()
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/execute")
async def execute_mission(request: IssueRequest):

    try:
        plan = orchestrator.execute_task(request.issue)

        return {
            "success": plan.status == TaskStatus.COMPLETED,
            "message": (
                "Engineering mission completed"
                if plan.status == TaskStatus.COMPLETED
                else "Engineering mission failed"
            ),
            "data": plan.model_dump()
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/tasks")
async def get_all_tasks():

    tasks = orchestrator.get_all_tasks()

    return {
        "success": True,
        "total": len(tasks),
        "tasks": [task.model_dump() for task in tasks]
    }

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):

    task = orchestrator.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "success": True,
        "data": task.model_dump()
    }

@router.get("/status")
async def orchestrator_status():

    return {
        "success": True,
        "data": orchestrator.get_system_status()
    }