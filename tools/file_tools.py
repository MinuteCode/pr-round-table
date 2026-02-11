"""
File tools for reading and discovering files in a repository.
"""

import os
from agno.tools import Toolkit
from agno.utils.log import logger

MAX_FILE_SIZE = 50 * 1024  # 50 KB

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".build",
    ".venv",
    "venv",
    ".tox",
    "Pods",
    "DerivedData",
}


class FileTools(Toolkit):
    """Toolkit for reading and discovering files in a repository."""

    def __init__(self, repo_path: str = "."):
        super().__init__(
            name="file_tools",
            tools=[self.read_file, self.find_file],
        )
        self.repo_path = os.path.realpath(repo_path)

    def read_file(self, file_path: str) -> str:
        """
        Read and return the contents of a file in the repository.

        The path is resolved relative to the repository root. Paths that
        attempt to escape the repository via '..' traversal are rejected.

        Args:
            file_path: Path to the file, relative to the repository root.

        Returns:
            The file contents as a string, or an error message.
        """
        logger.info(f"Reading file: {file_path}")
        try:
            resolved = os.path.realpath(os.path.join(self.repo_path, file_path))
            if not resolved.startswith(self.repo_path + os.sep) and resolved != self.repo_path:
                return f"Error: path '{file_path}' is outside the repository."

            if not os.path.isfile(resolved):
                return f"Error: file '{file_path}' not found."

            size = os.path.getsize(resolved)
            if size > MAX_FILE_SIZE:
                return f"Error: file '{file_path}' is too large ({size} bytes, max {MAX_FILE_SIZE})."

            with open(resolved, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def find_file(self, filename: str) -> str:
        """
        Search the repository for files matching the given filename.

        Hidden directories (.git, etc.), node_modules, __pycache__, and other
        common noise directories are skipped.

        Args:
            filename: The filename to search for (e.g. 'AGENTS.md').

        Returns:
            A newline-separated list of matching relative paths, or a message
            if no matches are found.
        """
        logger.info(f"Searching for file: {filename}")
        matches: list[str] = []
        try:
            for dirpath, dirnames, filenames in os.walk(self.repo_path):
                # Prune skipped directories in-place
                dirnames[:] = [
                    d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
                ]
                if filename in filenames:
                    full = os.path.join(dirpath, filename)
                    rel = os.path.relpath(full, self.repo_path)
                    matches.append(rel)
        except Exception as e:
            return f"Error searching for file: {e}"

        if not matches:
            return f"No files named '{filename}' found in the repository."
        return "\n".join(matches)
