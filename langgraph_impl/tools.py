"""
Tool definitions for the LangGraph code review tool.

All tools are created via a factory function that captures repo_path and
model config via closures, so they can be used as standalone @tool functions.
"""

import os
import subprocess
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph_impl.config import get_model
from langgraph_impl.prompts import (
    QUALITY_REVIEWER_SYSTEM_PROMPT,
    SECURITY_REVIEWER_SYSTEM_PROMPT,
)

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


def create_tools(
    repo_path: str = ".", provider: str = None, model_id: str = None
) -> list:
    """
    Create all tools for the Judge agent.

    Returns a list of 7 @tool functions:
    - get_diff, get_changed_files, get_branches (git operations)
    - read_file, find_file (file operations)
    - quality_review, security_review (reviewer sub-agents)

    Args:
        repo_path: Path to the git repository
        provider: LLM provider for reviewer sub-agents
        model_id: Model ID for reviewer sub-agents
    """
    real_repo_path = os.path.realpath(repo_path)

    # --- Git tools ---

    @tool
    def get_diff(source_branch: str, target_branch: str) -> str:
        """Get the unified diff between two git branches.

        Args:
            source_branch: The source branch containing the changes
            target_branch: The target branch to compare against (e.g. main)
        """
        try:
            result = subprocess.run(
                ["git", "diff", f"{target_branch}...{source_branch}"],
                capture_output=True,
                text=True,
                cwd=real_repo_path,
                check=True,
            )
            if not result.stdout.strip():
                return "No differences found between branches."
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error getting diff: {e.stderr}"

    @tool
    def get_changed_files(source_branch: str, target_branch: str) -> str:
        """Get list of files changed between two branches.

        Args:
            source_branch: The source branch containing the changes
            target_branch: The target branch to compare against (e.g. main)
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "diff",
                    "--name-only",
                    f"{target_branch}...{source_branch}",
                ],
                capture_output=True,
                text=True,
                cwd=real_repo_path,
                check=True,
            )
            return result.stdout or "No files changed."
        except subprocess.CalledProcessError as e:
            return f"Error getting changed files: {e.stderr}"

    @tool
    def get_branches() -> str:
        """List all available git branches."""
        try:
            result = subprocess.run(
                ["git", "branch", "-a", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                cwd=real_repo_path,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error listing branches: {e.stderr}"

    # --- File tools ---

    @tool
    def read_file(file_path: str) -> str:
        """Read and return the contents of a file in the repository.
        The path is relative to the repository root.

        Args:
            file_path: Path to the file, relative to the repository root
        """
        try:
            resolved = os.path.realpath(
                os.path.join(real_repo_path, file_path)
            )
            if (
                not resolved.startswith(real_repo_path + os.sep)
                and resolved != real_repo_path
            ):
                return f"Error: path '{file_path}' is outside the repository."

            if not os.path.isfile(resolved):
                return f"Error: file '{file_path}' not found."

            size = os.path.getsize(resolved)
            if size > MAX_FILE_SIZE:
                return (
                    f"Error: file '{file_path}' is too large "
                    f"({size} bytes, max {MAX_FILE_SIZE})."
                )

            with open(resolved, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    @tool
    def find_file(filename: str) -> str:
        """Search the repository for files matching the given filename.

        Args:
            filename: The filename to search for (e.g. 'AGENTS.md')
        """
        matches: list[str] = []
        try:
            for dirpath, dirnames, filenames in os.walk(real_repo_path):
                dirnames[:] = [
                    d
                    for d in dirnames
                    if d not in SKIP_DIRS and not d.startswith(".")
                ]
                if filename in filenames:
                    full = os.path.join(dirpath, filename)
                    rel = os.path.relpath(full, real_repo_path)
                    matches.append(rel)
        except Exception as e:
            return f"Error searching for file: {e}"

        if not matches:
            return f"No files named '{filename}' found in the repository."
        return "\n".join(matches)

    # --- Reviewer sub-agent tools ---

    @tool
    def quality_review(context: str) -> str:
        """Invoke the Code Quality Reviewer to analyze code changes.
        Pass the full diff and any relevant context as the argument.

        Args:
            context: The code diff and context for the reviewer to analyze
        """
        try:
            reviewer_model = get_model(provider=provider, model_id=model_id)
            response = reviewer_model.invoke(
                [
                    SystemMessage(content=QUALITY_REVIEWER_SYSTEM_PROMPT),
                    HumanMessage(content=context),
                ]
            )
            return response.content
        except Exception as e:
            return f"Error during quality review: {e}"

    @tool
    def security_review(context: str) -> str:
        """Invoke the Security & Performance Reviewer to analyze code changes.
        Pass the full diff and any relevant context as the argument.

        Args:
            context: The code diff and context for the reviewer to analyze
        """
        try:
            reviewer_model = get_model(provider=provider, model_id=model_id)
            response = reviewer_model.invoke(
                [
                    SystemMessage(content=SECURITY_REVIEWER_SYSTEM_PROMPT),
                    HumanMessage(content=context),
                ]
            )
            return response.content
        except Exception as e:
            return f"Error during security review: {e}"

    return [
        get_diff,
        get_changed_files,
        get_branches,
        read_file,
        find_file,
        quality_review,
        security_review,
    ]
