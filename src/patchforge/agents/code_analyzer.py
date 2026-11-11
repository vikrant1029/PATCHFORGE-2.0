
import ast
from pathlib import Path
from typing import Any


class CodeQualityAnalyzer:
    """
    PATCHFORGE 2.0
    Static Code Quality Intelligence Engine
    """

    EXCLUDED_DIRS = {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "node_modules",
        "build",
        "dist",
        ".pytest_cache"
    }

    MAX_LINE_LENGTH = 100

    def __init__(self, repository_path: str = "."):
        self.repository_path = Path(repository_path).resolve()
        self.results: list[dict[str, Any]] = []
        self.issues: list[dict[str, Any]] = []

    def analyze_file(self, file_path: Path) -> dict[str, Any]:

        try:
            source = file_path.read_text(encoding="utf-8")
            lines = source.splitlines()
            tree = ast.parse(source, filename=str(file_path))

        except SyntaxError as error:
            return {
                "file": str(file_path.relative_to(self.repository_path)),
                "status": "SYNTAX_ERROR",
                "error": str(error),
                "quality_score": 0
            }

        except (OSError, UnicodeError) as error:
            return {
                "file": str(file_path.relative_to(self.repository_path)),
                "status": "READ_ERROR",
                "error": str(error),
                "quality_score": 0
            }

        function_count = 0
        class_count = 0
        import_count = 0
        complexity = 0
        issues = []

        for node in ast.walk(tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_count += 1

                if len(node.body) > 50:
                    issues.append({
                        "type": "LONG_FUNCTION",
                        "line": node.lineno,
                        "severity": "MEDIUM",
                        "message": f"Function '{node.name}' is too long."
                    })

            elif isinstance(node, ast.ClassDef):
                class_count += 1

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_count += 1

            elif isinstance(
                node,
                (ast.If, ast.For, ast.AsyncFor, ast.While,
                 ast.ExceptHandler, ast.IfExp)
            ):
                complexity += 1

            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1

        for line_number, line in enumerate(lines, start=1):

            if len(line) > self.MAX_LINE_LENGTH:
                issues.append({
                    "type": "LONG_LINE",
                    "line": line_number,
                    "severity": "LOW",
                    "message": "Line exceeds 100 characters."
                })

            if "TODO" in line or "FIXME" in line:
                issues.append({
                    "type": "PENDING_TASK",
                    "line": line_number,
                    "severity": "LOW",
                    "message": "Unresolved TODO/FIXME comment."
                })

        critical_count = sum(
            1 for issue in issues
            if issue["severity"] == "CRITICAL"
        )

        medium_count = sum(
            1 for issue in issues
            if issue["severity"] == "MEDIUM"
        )

        low_count = sum(
            1 for issue in issues
            if issue["severity"] == "LOW"
        )

        quality_score = max(
            0,
            100 - (
                critical_count * 25
                + medium_count * 10
                + low_count * 2
                + max(0, complexity - 10)
            )
        )

        return {
            "file": str(file_path.relative_to(self.repository_path)),
            "status": "ANALYZED",
            "quality_score": quality_score,
            "metrics": {
                "lines_of_code": len(lines),
                "functions": function_count,
                "classes": class_count,
                "imports": import_count,
                "complexity_indicator": complexity
            },
            "issues": issues,
            "issue_count": len(issues)
        }

    def analyze_repository(self) -> dict[str, Any]:

        self.results = []
        self.issues = []

        if not self.repository_path.is_dir():
            raise ValueError("Repository directory does not exist.")

        python_files = [
            path
            for path in self.repository_path.rglob("*.py")
            if not any(
                part in self.EXCLUDED_DIRS
                for part in path.parts
            )
        ]

        for file_path in python_files:

            result = self.analyze_file(file_path)
            self.results.append(result)

            for issue in result.get("issues", []):
                self.issues.append({
                    "file": result["file"],
                    **issue
                })

        analyzed_files = [
            result for result in self.results
            if result["status"] == "ANALYZED"
        ]

        scores = [
            result["quality_score"]
            for result in analyzed_files
        ]

        average_score = (
            round(sum(scores) / len(scores), 2)
            if scores else 0
        )

        return {
            "success": True,
            "engine": "PATCHFORGE Code Quality Analyzer 2.0",
            "repository": str(self.repository_path),
            "total_files": len(python_files),
            "analyzed_files": len(analyzed_files),
            "failed_files": len(python_files) - len(analyzed_files),
            "average_quality_score": average_score,
            "total_issues": len(self.issues),
            "files": self.results,
            "issues": self.issues
        }
