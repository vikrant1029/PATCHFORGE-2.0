
import ast
import difflib
import hashlib
import os
import re
import tempfile

from pathlib import Path
from datetime import datetime, timezone
from typing import Any


class CodeImprover:
    """
    PATCHFORGE 2.0
    Safe Code Improvement & Fixing Engine

    Features:
    - Code improvement recommendations
    - Safe whitespace fixes
    - Before/After diff
    - Backup creation
    - User approval before modification
    - Python syntax validation
    - Automatic rollback on failed validation
    """

    ENGINE_NAME = "PATCHFORGE Safe Code Improver 2.0"

    SEVERITY_PRIORITY = {
        "CRITICAL": 1,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 4
    }

    EXCLUDED_DIRS = {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "node_modules",
        "build",
        "dist",
        ".pytest_cache",
        ".patchforge_backups"
    }

    SAFE_FIX_TYPES = {
        "TRAILING_WHITESPACE",
        "MISSING_FINAL_NEWLINE"
    }

    def __init__(self, repository_path: str = "."):

        self.repository_path = Path(
            repository_path
        ).resolve()

        self.suggestions: list[dict[str, Any]] = []

        self.last_fix_report: dict[str, Any] = {}

        self.backup_directory = (
            self.repository_path / ".patchforge_backups"
        )

    # ========================================================
    # FILE SAFETY
    # ========================================================

    def _resolve_file(self, file_path: str) -> Path:

        if not file_path or not isinstance(file_path, str):
            raise ValueError("A valid file path is required.")

        candidate = Path(file_path)

        if candidate.is_absolute():
            resolved = candidate.resolve()
        else:
            resolved = (
                self.repository_path / candidate
            ).resolve()

        try:
            resolved.relative_to(self.repository_path)
        except ValueError:
            raise ValueError(
                "Access denied: file is outside the repository."
            )

        if not resolved.is_file():
            raise FileNotFoundError(
                f"File not found: {resolved}"
            )

        if resolved.suffix.lower() != ".py":
            raise ValueError(
                "Only Python source files are supported."
            )

        if any(
            part in self.EXCLUDED_DIRS
            for part in resolved.parts
        ):
            raise ValueError(
                "This file belongs to an excluded directory."
            )

        return resolved

    def _read_source(self, path: Path) -> str:

        try:
            return path.read_bytes().decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(
                "Only UTF-8 Python source files are supported."
            ) from error

    # ========================================================
    # SAFE FIX GENERATOR
    # ========================================================

    def _generate_safe_candidate(
        self,
        source: str
    ) -> dict[str, Any]:

        lines = source.splitlines(keepends=True)

        fixed_lines = []
        changes = []

        for index, line in enumerate(lines, start=1):

            if line.endswith("\r\n"):
                ending = "\r\n"
                content = line[:-2]

            elif line.endswith("\n"):
                ending = "\n"
                content = line[:-1]

            elif line.endswith("\r"):
                ending = "\r"
                content = line[:-1]

            else:
                ending = ""
                content = line

            cleaned = content.rstrip(" \t")

            if cleaned != content:

                changes.append({
                    "type": "TRAILING_WHITESPACE",
                    "line": index,
                    "description": (
                        "Removed trailing spaces or tabs."
                    )
                })

            fixed_lines.append(cleaned + ending)

        candidate = "".join(fixed_lines)

        if candidate and not candidate.endswith(("\n", "\r")):

            candidate += "\n"

            changes.append({
                "type": "MISSING_FINAL_NEWLINE",
                "line": len(fixed_lines),
                "description": (
                    "Added a final newline."
                )
            })

        return {
            "candidate": candidate,
            "changes": changes
        }

    # ========================================================
    # IMPROVEMENT RECOMMENDATIONS
    # ========================================================

    def generate_suggestion(
        self,
        issue: dict[str, Any]
    ) -> dict[str, Any]:

        issue_type = str(
            issue.get("type", "")
        ).upper()

        severity = str(
            issue.get("severity", "LOW")
        ).upper()

        suggestions = {

            "LONG_FUNCTION": {
                "title": "Refactor Long Function",
                "recommendation": (
                    "Break the function into smaller, "
                    "reusable helper functions."
                ),
                "action": "FUNCTION_REFACTORING"
            },

            "LONG_LINE": {
                "title": "Improve Code Readability",
                "recommendation": (
                    "Split long lines carefully without "
                    "changing string literals or program behavior."
                ),
                "action": "CODE_FORMATTING"
            },

            "PENDING_TASK": {
                "title": "Resolve Pending Task",
                "recommendation": (
                    "Review the TODO/FIXME comment and "
                    "implement or remove the pending task."
                ),
                "action": "TASK_RESOLUTION"
            },

            "SYNTAX_ERROR": {
                "title": "Fix Syntax Error",
                "recommendation": (
                    "Inspect the reported line and correct "
                    "the Python syntax."
                ),
                "action": "SYNTAX_CORRECTION"
            },

            "IMPORT_ERROR": {
                "title": "Resolve Import Issue",
                "recommendation": (
                    "Verify the module path and ensure "
                    "the required package is installed."
                ),
                "action": "IMPORT_CORRECTION"
            },

            "TRAILING_WHITESPACE": {
                "title": "Remove Trailing Whitespace",
                "recommendation": (
                    "Remove unnecessary spaces and tabs "
                    "at the ends of lines."
                ),
                "action": "SAFE_WHITESPACE_FIX"
            },

            "MISSING_FINAL_NEWLINE": {
                "title": "Add Final Newline",
                "recommendation": (
                    "Add a newline at the end of the Python file."
                ),
                "action": "SAFE_NEWLINE_FIX"
            }
        }

        recommendation = suggestions.get(
            issue_type,
            {
                "title": "Review Code Issue",
                "recommendation": (
                    "Inspect the affected code and review "
                    "possible improvements."
                ),
                "action": "MANUAL_REVIEW"
            }
        )

        automatic_fix = (
            issue_type in self.SAFE_FIX_TYPES
        )

        return {
            "file": issue.get("file", "Unknown"),
            "line": issue.get("line"),
            "issue_type": issue_type or "UNKNOWN",
            "severity": severity,
            "priority": self.SEVERITY_PRIORITY.get(
                severity, 5
            ),
            "title": recommendation["title"],
            "recommendation": recommendation["recommendation"],
            "action": recommendation["action"],
            "status": "SUGGESTION_GENERATED",
            "automatic_fix": automatic_fix
        }

    # ========================================================
    # REPOSITORY IMPROVEMENT ANALYSIS
    # ========================================================

    def improve_repository(
        self,
        quality_report: dict[str, Any]
    ) -> dict[str, Any]:

        self.suggestions = []

        if not isinstance(quality_report, dict):
            raise ValueError("Invalid quality report.")

        if not quality_report.get("success"):
            raise ValueError(
                "Quality analysis was unsuccessful."
            )

        issues = quality_report.get("issues", [])

        if not isinstance(issues, list):
            raise ValueError("Invalid issues data.")

        for issue in issues:

            if not isinstance(issue, dict):
                continue

            self.suggestions.append(
                self.generate_suggestion(issue)
            )

        self.suggestions.sort(
            key=lambda item: item["priority"]
        )

        severity_summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        for suggestion in self.suggestions:

            severity = suggestion["severity"]

            if severity in severity_summary:
                severity_summary[severity] += 1

        return {
            "success": True,
            "engine": self.ENGINE_NAME,
            "repository": str(self.repository_path),
            "total_issues": len(issues),
            "total_suggestions": len(self.suggestions),
            "severity_summary": severity_summary,

            # Keep both keys for dashboard compatibility.
            "suggestions": self.suggestions,
            "recommendations": self.suggestions,

            "execution_mode": "SAFE_RECOMMENDATION_AND_APPROVED_FIX",
            "files_modified": 0
        }

    # ========================================================
    # PREVIEW SAFE FIX
    # ========================================================

    def preview_fix(
        self,
        file_path: str
    ) -> dict[str, Any]:

        path = self._resolve_file(file_path)

        original = self._read_source(path)

        generated = self._generate_safe_candidate(
            original
        )

        candidate = generated["candidate"]
        changes = generated["changes"]

        # Never apply a candidate that fails Python parsing.
        try:
            ast.parse(
                candidate,
                filename=str(path)
            )

        except SyntaxError as error:

            return {
                "success": False,
                "status": "VALIDATION_FAILED",
                "file": str(path),
                "error": str(error),
                "changes": [],
                "diff": ""
            }

        diff = "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                candidate.splitlines(keepends=True),
                fromfile="BEFORE",
                tofile="AFTER"
            )
        )

        return {
            "success": True,
            "status": (
                "FIX_AVAILABLE"
                if changes else "NO_CHANGES_REQUIRED"
            ),
            "file": str(path),
            "original_hash": hashlib.sha256(
                original.encode("utf-8")
            ).hexdigest(),
            "changes": changes,
            "total_changes": len(changes),
            "diff": diff,
            "preview": candidate,
            "approval_required": True,
            "file_modified": False
        }

    # ========================================================
    # APPLY APPROVED FIX
    # ========================================================

    def apply_fix(
        self,
        file_path: str,
        approved: bool = False
    ) -> dict[str, Any]:

        if approved is not True:

            return {
                "success": False,
                "status": "APPROVAL_REQUIRED",
                "message": (
                    "User approval is required before "
                    "modifying source files."
                ),
                "file_modified": False
            }

        path = self._resolve_file(file_path)

        original = self._read_source(path)

        preview = self.preview_fix(file_path)

        if not preview.get("success"):
            return preview

        if preview["status"] == "NO_CHANGES_REQUIRED":

            return {
                "success": True,
                "status": "NO_CHANGES_REQUIRED",
                "file": str(path),
                "file_modified": False
            }

        # Ensure the source did not change after preview.
        current_hash = hashlib.sha256(
            self._read_source(path).encode("utf-8")
        ).hexdigest()

        if current_hash != preview["original_hash"]:

            return {
                "success": False,
                "status": "SOURCE_CHANGED",
                "message": (
                    "Source changed during processing. "
                    "Generate a new preview."
                ),
                "file_modified": False
            }

        backup_path = None
        temp_path = None

        try:

            # Create backup.
            self.backup_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            timestamp = datetime.now(
                timezone.utc
            ).strftime("%Y%m%d_%H%M%S_%f")

            backup_name = (
                f"{path.name}.{timestamp}.bak"
            )

            backup_path = (
                self.backup_directory / backup_name
            )

            backup_path.write_bytes(
                path.read_bytes()
            )

            candidate = preview["preview"]

            # Write candidate to a temporary file.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                suffix=".tmp",
                prefix="patchforge_",
                dir=str(path.parent),
                delete=False
            ) as temp_file:

                temp_file.write(candidate)
                temp_path = Path(temp_file.name)

            # Validate temporary source.
            ast.parse(
                temp_path.read_text(encoding="utf-8"),
                filename=str(path)
            )

            # Atomic replacement.
            os.replace(
                temp_path,
                path
            )

            temp_path = None

            # Validate final source.
            ast.parse(
                self._read_source(path),
                filename=str(path)
            )

            report = {
                "success": True,
                "status": "FIX_APPLIED",
                "engine": self.ENGINE_NAME,
                "file": str(path),
                "backup": str(backup_path),
                "changes": preview["changes"],
                "total_changes": preview["total_changes"],
                "diff": preview["diff"],
                "validation": "PYTHON_AST_VALIDATION_PASSED",
                "file_modified": True,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat()
            }

            self.last_fix_report = report

            return report

        except Exception as error:

            # Restore original source on failure.
            try:

                if backup_path and backup_path.exists():

                    path.write_bytes(
                        backup_path.read_bytes()
                    )

            except OSError as rollback_error:

                return {
                    "success": False,
                    "status": "ROLLBACK_FAILED",
                    "error": str(error),
                    "rollback_error": str(rollback_error),
                    "backup": str(backup_path),
                    "file_modified": True
                }

            return {
                "success": False,
                "status": "FIX_FAILED_ROLLED_BACK",
                "error": str(error),
                "backup": (
                    str(backup_path)
                    if backup_path else None
                ),
                "file_modified": False
            }

        finally:

            if temp_path and temp_path.exists():

                try:
                    temp_path.unlink()
                except OSError:
                    pass

    # ========================================================
    # RESTORE BACKUP
    # ========================================================

    def restore_backup(
        self,
        file_path: str,
        backup_path: str,
        approved: bool = False
    ) -> dict[str, Any]:

        if approved is not True:

            return {
                "success": False,
                "status": "APPROVAL_REQUIRED"
            }

        target = self._resolve_file(file_path)

        backup = Path(backup_path).resolve()

        try:
            backup.relative_to(
                self.backup_directory.resolve()
            )

        except ValueError:

            raise ValueError(
                "Backup must be inside PATCHFORGE backup directory."
            )

        if not backup.is_file():
            raise FileNotFoundError(
                "Backup file does not exist."
            )

        original_backup = backup.read_bytes()

        try:

            source_text = original_backup.decode("utf-8")

            ast.parse(
                source_text,
                filename=str(target)
            )

        except (UnicodeDecodeError, SyntaxError) as error:

            return {
                "success": False,
                "status": "BACKUP_VALIDATION_FAILED",
                "error": str(error)
            }

        current_backup = None

        try:

            if target.exists():

                current_backup = (
                    self.backup_directory /
                    f"{target.name}.before_restore."
                    f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.bak"
                )

                current_backup.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                current_backup.write_bytes(
                    target.read_bytes()
                )

            target.write_bytes(original_backup)

            return {
                "success": True,
                "status": "BACKUP_RESTORED",
                "file": str(target),
                "previous_version_backup": (
                    str(current_backup)
                    if current_backup else None
                )
            }

        except OSError as error:

            if current_backup and current_backup.exists():

                target.write_bytes(
                    current_backup.read_bytes()
                )

            return {
                "success": False,
                "status": "RESTORE_FAILED",
                "error": str(error)
            }

    # ========================================================
    # ENGINE STATUS
    # ========================================================

    def get_status(self) -> dict[str, Any]:

        return {
            "success": True,
            "engine": self.ENGINE_NAME,
            "status": "OPERATIONAL",
            "repository": str(self.repository_path),
            "total_suggestions": len(self.suggestions),
            "safe_fix_types": sorted(
                self.SAFE_FIX_TYPES
            ),
            "backup_directory": str(
                self.backup_directory
            ),
            "approval_required": True,
            "syntax_validation": True,
            "automatic_modification": False
        }


# ============================================================
# SHARED ENGINE INSTANCE
# ============================================================

code_improver = CodeImprover()
