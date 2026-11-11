
"""
PATCHFORGE 2.0
Intelligent Bug Detection Engine
Team KRYNEXA

Capabilities:
- Python syntax error detection
- Dangerous function detection
- Mutable default argument detection
- Bare exception detection
- Subprocess shell execution detection
- Structured severity-based reports
"""

import ast
import re
from pathlib import Path
from typing import Any


class BugDetector:

    EXCLUDED_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build"
    }

    MAX_FILE_SIZE = 1_000_000

    def __init__(self, root_path: str | Path | None = None):
        self.root_path = (
            Path(root_path).resolve()
            if root_path
            else Path.cwd().resolve()
        )

        self.issues: list[dict[str, Any]] = []

    def add_issue(
        self,
        file: str,
        line: int,
        severity: str,
        category: str,
        message: str,
        recommendation: str
    ) -> None:

        self.issues.append({
            "file": file,
            "line": line,
            "severity": severity,
            "category": category,
            "message": message,
            "recommendation": recommendation
        })

    # ----------------------------------
    # AST ANALYSIS
    # ----------------------------------

    def analyze_ast(
        self,
        tree: ast.AST,
        relative_path: str
    ) -> None:

        for node in ast.walk(tree):

            # 1. Dangerous eval()
            if isinstance(node, ast.Call):

                if isinstance(node.func, ast.Name):

                    if node.func.id == "eval":
                        self.add_issue(
                            relative_path,
                            node.lineno,
                            "HIGH",
                            "DANGEROUS_FUNCTION",
                            "Use of eval() detected.",
                            "Avoid eval(). Use safe parsing methods."
                        )

                    elif node.func.id == "exec":
                        self.add_issue(
                            relative_path,
                            node.lineno,
                            "HIGH",
                            "DANGEROUS_FUNCTION",
                            "Dynamic code execution using exec().",
                            "Avoid executing untrusted dynamic code."
                        )

                # 2. subprocess shell=True
                if isinstance(node.func, ast.Attribute):

                    if node.func.attr in {
                        "run",
                        "Popen",
                        "call",
                        "check_call",
                        "check_output"
                    }:

                        shell_enabled = any(
                            keyword.arg == "shell"
                            and isinstance(keyword.value, ast.Constant)
                            and keyword.value.value is True
                            for keyword in node.keywords
                        )

                        if shell_enabled:
                            self.add_issue(
                                relative_path,
                                node.lineno,
                                "HIGH",
                                "COMMAND_INJECTION_RISK",
                                "Subprocess call uses shell=True.",
                                "Avoid shell=True and pass commands "
                                "as argument lists."
                            )

            # 3. Bare except
            if isinstance(node, ast.ExceptHandler):

                if node.type is None:
                    self.add_issue(
                        relative_path,
                        node.lineno,
                        "MEDIUM",
                        "EXCEPTION_HANDLING",
                        "Bare except clause detected.",
                        "Catch specific exceptions instead."
                    )

            # 4. Mutable default arguments
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                positional_defaults = node.args.defaults

                keyword_defaults = [
                    value
                    for value in node.args.kw_defaults
                    if value is not None
                ]

                for default in positional_defaults + keyword_defaults:

                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        self.add_issue(
                            relative_path,
                            default.lineno,
                            "MEDIUM",
                            "MUTABLE_DEFAULT_ARGUMENT",
                            f"Mutable default argument in "
                            f"function '{node.name}'.",
                            "Use None as default and create "
                            "the object inside the function."
                        )

    # ----------------------------------
    # SECRET PATTERN ANALYSIS
    # ----------------------------------

    def analyze_patterns(
        self,
        content: str,
        relative_path: str
    ) -> None:

        patterns = [
            (
                r"""(?i)\b(?:api_key|secret_key|password)\s*=\s*["'][^"']{8,}["']""",
                "HIGH",
                "POSSIBLE_HARDCODED_SECRET",
                "Possible hardcoded credential detected.",
                "Use environment variables or a secret manager."
            )
        ]

        for pattern, severity, category, message, recommendation in patterns:

            for match in re.finditer(pattern, content):

                line = content.count("\n", 0, match.start()) + 1

                self.add_issue(
                    relative_path,
                    line,
                    severity,
                    category,
                    message,
                    recommendation
                )

    # ----------------------------------
    # FILE ANALYSIS
    # ----------------------------------

    def analyze_file(self, file_path: Path) -> None:

        try:

            if file_path.stat().st_size > self.MAX_FILE_SIZE:
                return

            content = file_path.read_text(
                encoding="utf-8",
                errors="replace"
            )

            relative_path = str(
                file_path.relative_to(self.root_path)
            )

            self.analyze_patterns(content, relative_path)

            try:
                tree = ast.parse(
                    content,
                    filename=relative_path
                )

            except SyntaxError as error:

                self.add_issue(
                    relative_path,
                    error.lineno or 0,
                    "CRITICAL",
                    "SYNTAX_ERROR",
                    error.msg,
                    "Fix the Python syntax error."
                )

                return

            self.analyze_ast(tree, relative_path)

        except (OSError, UnicodeError, ValueError):
            return

    # ----------------------------------
    # REPOSITORY SCAN
    # ----------------------------------

    def scan_repository(self) -> dict[str, Any]:

        self.issues = []

        if not self.root_path.is_dir():
            raise ValueError(
                f"Repository path does not exist: {self.root_path}"
            )

        scanned_files = 0

        for file_path in self.root_path.rglob("*.py"):

            if any(
                part in self.EXCLUDED_DIRS
                for part in file_path.parts
            ):
                continue

            scanned_files += 1
            self.analyze_file(file_path)

        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        for issue in self.issues:
            severity_counts[issue["severity"]] += 1

        return {
            "success": True,
            "engine": "PATCHFORGE Bug Detector 2.0",
            "repository": str(self.root_path),
            "scanned_files": scanned_files,
            "total_issues": len(self.issues),
            "severity_summary": severity_counts,
            "issues": self.issues
        }
