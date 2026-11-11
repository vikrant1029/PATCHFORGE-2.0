
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import uuid4
from typing import Any

from pydantic import BaseModel, Field

from patchforge.core.database import database

from patchforge.agents.bug_detector import BugDetector
from patchforge.agents.code_analyzer import CodeQualityAnalyzer
from patchforge.agents.code_improver import CodeImprover


class TaskStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStep(BaseModel):
    step_id: int
    agent_name: str
    action: str
    status: StepStatus = StepStatus.PENDING
    result: dict[str, Any] | None = None


class ExecutionPlan(BaseModel):
    task_id: str
    issue: str
    status: TaskStatus
    created_at: str
    total_steps: int
    steps: list[AgentStep]
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class PatchForgeOrchestrator:

    def __init__(self, repository_path: str = "."):
        self.name = "PatchForge AI Orchestrator"
        self.version = "2.0.0"
        self.repository_path = Path(repository_path).resolve()
        self.max_retries = 3
        self.tasks: dict[str, ExecutionPlan] = {}

    # ==========================================
    # DATABASE PERSISTENCE
    # ==========================================

    def _persist_task(self, plan: ExecutionPlan):
        database.save_task(plan)

    # ==========================================
    # CREATE EXECUTION PLAN
    # ==========================================

    def create_plan(self, issue: str) -> ExecutionPlan:

        if not issue or not issue.strip():
            raise ValueError("Issue description is required.")

        steps = [
            AgentStep(
                step_id=1,
                agent_name="Issue Intelligence Agent",
                action="Validate and understand the submitted issue"
            ),
            AgentStep(
                step_id=2,
                agent_name="Repository Intelligence Agent",
                action="Inspect repository and discover Python files"
            ),
            AgentStep(
                step_id=3,
                agent_name="Bug Detection Agent",
                action="Scan source code for potential bugs and security risks"
            ),
            AgentStep(
                step_id=4,
                agent_name="Code Quality Agent",
                action="Analyze syntax, structure and code quality"
            ),
            AgentStep(
                step_id=5,
                agent_name="Code Improvement Agent",
                action="Generate prioritized safe improvement recommendations"
            ),
            AgentStep(
                step_id=6,
                agent_name="Mission Report Agent",
                action="Compile all engineering analysis results"
            )
        ]

        plan = ExecutionPlan(
            task_id=str(uuid4()),
            issue=issue.strip(),
            status=TaskStatus.PLANNED,
            created_at=datetime.now(timezone.utc).isoformat(),
            total_steps=len(steps),
            steps=steps
        )

        self.tasks[plan.task_id] = plan
        self._persist_task(plan)

        return plan

    # ==========================================
    # EXECUTE AGENT STEP
    # ==========================================

    def _run_step(self, plan, step_id, operation):

        step = plan.steps[step_id - 1]
        step.status = StepStatus.RUNNING

        self._persist_task(plan)

        try:
            result = operation()

            step.result = result
            step.status = StepStatus.COMPLETED

            self._persist_task(plan)

            return result

        except Exception as error:

            step.status = StepStatus.FAILED
            step.result = {"error": str(error)}

            self._persist_task(plan)

            raise

    # ==========================================
    # AUTONOMOUS ENGINEERING EXECUTION
    # ==========================================

    def execute_task(self, issue: str) -> ExecutionPlan:

        plan = self.create_plan(issue)

        plan.status = TaskStatus.RUNNING
        self._persist_task(plan)

        try:

            # STEP 1: ISSUE INTELLIGENCE

            issue_result = self._run_step(
                plan,
                1,
                lambda: {
                    "success": True,
                    "issue": plan.issue,
                    "message": "Issue accepted for engineering analysis."
                }
            )

            # STEP 2: REPOSITORY INTELLIGENCE

            def inspect_repository():

                if not self.repository_path.is_dir():
                    raise ValueError(
                        "Repository directory does not exist."
                    )

                excluded_dirs = {
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    "node_modules",
                    "build",
                    "dist",
                    ".pytest_cache",
                    ".mypy_cache"
                }

                files = [
                    path
                    for path in self.repository_path.rglob("*.py")
                    if not any(
                        part in excluded_dirs
                        for part in path.parts
                    )
                ]

                return {
                    "success": True,
                    "repository": str(self.repository_path),
                    "python_files_found": len(files),
                    "sample_files": [
                        str(path.relative_to(self.repository_path))
                        for path in files[:30]
                    ]
                }

            repository_result = self._run_step(
                plan,
                2,
                inspect_repository
            )

            # STEP 3: BUG DETECTION

            bug_result = self._run_step(
                plan,
                3,
                lambda: BugDetector(
                    self.repository_path
                ).scan_repository()
            )

            # STEP 4: CODE QUALITY ANALYSIS

            quality_result = self._run_step(
                plan,
                4,
                lambda: CodeQualityAnalyzer(
                    str(self.repository_path)
                ).analyze_repository()
            )

            # STEP 5: CODE IMPROVEMENT

            improvement_result = self._run_step(
                plan,
                5,
                lambda: CodeImprover(
                    str(self.repository_path)
                ).improve_repository(quality_result)
            )

            # STEP 6: FINAL MISSION REPORT

            report = {
                "success": True,
                "task_id": plan.task_id,
                "issue": plan.issue,
                "repository": str(self.repository_path),

                "issue_analysis": issue_result,
                "repository_analysis": repository_result,
                "bug_detection": bug_result,
                "quality_analysis": quality_result,
                "improvement_analysis": improvement_result,

                "execution_mode": "SAFE_ANALYSIS_ONLY",
                "files_modified": 0,

                "generated_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }

            self._run_step(
                plan,
                6,
                lambda: {
                    "success": True,
                    "message": "Engineering mission report generated."
                }
            )

            plan.result = report
            plan.status = TaskStatus.COMPLETED

        except Exception as error:

            plan.status = TaskStatus.FAILED
            plan.error = str(error)

            plan.result = {
                "success": False,
                "error": str(error)
            }

        finally:

            # Save final task state to SQLite
            self._persist_task(plan)

        return plan

    # ==========================================
    # GET SINGLE TASK
    # ==========================================

    def get_task(self, task_id: str):

        record = database.get_task(task_id)

        if record is None:
            return None

        task = ExecutionPlan.model_validate(record["data"])

        self.tasks[task_id] = task

        return task

    # ==========================================
    # GET ALL TASKS
    # ==========================================

    def get_all_tasks(self):

        records = database.get_all_tasks()

        tasks = []

        for record in records:

            task = self.get_task(record["task_id"])

            if task is not None:
                tasks.append(task)

        return tasks

    # ==========================================
    # SYSTEM STATUS
    # ==========================================

    def get_system_status(self):

        all_tasks = self.get_all_tasks()

        completed = sum(
            task.status == TaskStatus.COMPLETED
            for task in all_tasks
        )

        failed = sum(
            task.status == TaskStatus.FAILED
            for task in all_tasks
        )

        running = sum(
            task.status == TaskStatus.RUNNING
            for task in all_tasks
        )

        return {
            "orchestrator": self.name,
            "version": self.version,
            "status": "operational",
            "repository": str(self.repository_path),

            "total_tasks": len(all_tasks),
            "completed_tasks": completed,
            "failed_tasks": failed,
            "running_tasks": running,

            "database": database.get_database_status(),

            "execution_engine": "ACTIVE",
            "persistence": "SQLITE_ENABLED"
        }


# ==========================================
# GLOBAL ORCHESTRATOR INSTANCE
# ==========================================

orchestrator = PatchForgeOrchestrator()
