"""
Git tools for fetching diffs and branch information.
"""

import subprocess
from agno.tools import Toolkit
from agno.utils.log import logger


class GitTools(Toolkit):
    """Toolkit for interacting with git repositories."""

    def __init__(self, repo_path: str = "."):
        super().__init__(
            name="git_tools",
            tools=[self.get_diff, self.get_branches, self.get_changed_files],
        )
        self.repo_path = repo_path

    def get_diff(self, source_branch: str, target_branch: str) -> str:
        """
        Get the unified diff between two git branches.

        Args:
            source_branch: The source branch (e.g., feature-branch)
            target_branch: The target branch (e.g., main)

        Returns:
            The git diff output as a string
        """
        logger.info(f"Getting diff: {target_branch}...{source_branch}")
        try:
            result = subprocess.run(
                ["git", "diff", f"{target_branch}...{source_branch}"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            if not result.stdout.strip():
                return "No differences found between branches."
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error getting diff: {e.stderr}"

    def get_branches(self) -> str:
        """
        List all available git branches.

        Returns:
            List of branch names
        """
        try:
            result = subprocess.run(
                ["git", "branch", "-a", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error listing branches: {e.stderr}"

    def get_changed_files(self, source_branch: str, target_branch: str) -> str:
        """
        Get list of files changed between two branches.

        Args:
            source_branch: The source branch
            target_branch: The target branch

        Returns:
            List of changed file paths
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{target_branch}...{source_branch}"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            return result.stdout or "No files changed."
        except subprocess.CalledProcessError as e:
            return f"Error getting changed files: {e.stderr}"
