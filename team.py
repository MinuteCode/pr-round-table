"""
Code Review Team orchestration.

The team consists of:
- Judge (Team Leader): Coordinates the review and synthesizes findings
- Code Quality Reviewer: Focuses on readability and best practices
- Security & Performance Reviewer: Focuses on vulnerabilities and performance
"""

from agno.team import Team
from agno.db.in_memory import InMemoryDb
from config import get_model
from agents.reviewers import create_quality_reviewer, create_security_reviewer
from tools.git_tools import GitTools
from tools.file_tools import FileTools


def create_review_team(
    repo_path: str = ".", provider: str = None, model_id: str = None
):
    """
    Create the code review team with Judge as leader.

    Args:
        repo_path: Path to the git repository
        provider: LLM provider to use
        model_id: Specific model ID to use

    Returns:
        Team configured for code review
    """
    reviewer_1 = create_quality_reviewer(provider=provider, model_id=model_id)
    reviewer_2 = create_security_reviewer(provider=provider, model_id=model_id)

    return Team(
        name="Code Review Team",
        model=get_model(provider=provider, model_id=model_id),
        db=InMemoryDb(),
        members=[reviewer_1, reviewer_2],
        tools=[GitTools(repo_path=repo_path), FileTools(repo_path=repo_path)],
        instructions=[
            "You are the Judge agent leading a code review team. The codebase is in swift, the architecture is VIP, with an ongoing migration to MVVM.",
            "Point out the opportunities for refactoring, bad practices and propose very concise ideas for refactoring.",
            "Your role is to:",
            "1. Use the git tools to fetch the diff between branches",
            "2. Delegate the review to BOTH team members simultaneously",
            "3. Collect their findings and synthesize a final verdict",
            "",
            "When producing the final review, you must:",
            "- Consolidate findings from both reviewers",
            "- Resolve any conflicting recommendations",
            "- Prioritize issues by severity (Critical > High > Medium > Low)",
            "- Remove duplicate issues",
            "- Provide a detailed summary of the changes needed",
            "- Give references to specific files and lines of code, giving surrounding context without exceeding 20 lines",
            "",
            "Output format (markdown):",
            "## Executive Summary",
            "[Detailed overview of the most critical changes, their filepath and the block of code (not exceeding 20 lines) that is triggering the issue]",
            "",
            "## Critical Issues",
            "[Issues that must be fixed before merge]",
            "",
            "## High Priority",
            "[Important issues to address]",
            "",
            "## Medium Priority",
            "[Improvements to consider]",
            "",
            "## Final Verdict",
            "[APPROVE / REQUEST CHANGES / NEEDS DISCUSSION]",
        ],
        delegate_to_all_members=True,
        show_members_responses=True,
        add_history_to_context=True,
        markdown=True,
    )
