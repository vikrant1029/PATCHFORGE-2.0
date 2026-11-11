
from pathlib import Path
from collections import Counter


class RepositoryAnalyzer:
    """
    PatchForge Repository Intelligence Engine.

    Analyzes project structure, file metadata,
    extensions and repository statistics.

    Does not modify source files or expose file contents.
    """

    EXCLUDED_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "coverage",
        ".tox"
    }

    EXCLUDED_FILES = {
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        "id_rsa",
        "id_ed25519"
    }

    ALLOWED_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".html",
        ".css",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".md",
        ".txt",
        ".sql",
        ".sh",
        ".ps1",
        ".ini",
        ".cfg"
    }

    MAX_FILES = 500
    MAX_FILE_SIZE = 1_000_000

    def __init__(self, root_path: str):

        self.root = Path(root_path).resolve()

        if not self.root.exists():
            raise ValueError("Repository path does not exist")

        if not self.root.is_dir():
            raise ValueError("Repository path must be a directory")

    def analyze(self):

        files = []
        extensions = Counter()

        total_size = 0
        skipped_files = 0

        for path in self.root.rglob("*"):

            relative = path.relative_to(self.root)

            # Ignore excluded directories
            if any(
                part in self.EXCLUDED_DIRS
                for part in relative.parts
            ):
                continue

            if not path.is_file():
                continue

            # Ignore sensitive files
            if path.name in self.EXCLUDED_FILES:
                continue

            if path.name.startswith(".env"):
                continue

            # Allow only selected source/config extensions
            if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                continue

            try:

                # Prevent following files outside repository
                resolved_path = path.resolve()

                if not resolved_path.is_relative_to(self.root):
                    skipped_files += 1
                    continue

                size = resolved_path.stat().st_size

                if size > self.MAX_FILE_SIZE:
                    skipped_files += 1
                    continue

                extension = path.suffix.lower()

                files.append({
                    "path": relative.as_posix(),
                    "extension": extension,
                    "size_bytes": size
                })

                extensions[extension] += 1
                total_size += size

                if len(files) >= self.MAX_FILES:
                    break

            except OSError:
                skipped_files += 1

        return {
            "repository": self.root.name,
            "repository_path": str(self.root),
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 2),
            "extensions": dict(extensions),
            "skipped_files": skipped_files,
            "file_limit": self.MAX_FILES,
            "files": files,
            "status": "analysis_completed"
        }
