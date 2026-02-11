"""
Specialized code reviewer agents.

- Code Quality Reviewer: Focuses on readability, best practices, maintainability
- Security & Performance Reviewer: Focuses on vulnerabilities and performance issues
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.agent import Agent
from config import get_model


def create_quality_reviewer(provider: str = None, model_id: str = None):
    """
    Create a reviewer focused on code quality and maintainability.

    Args:
        provider: LLM provider to use
        model_id: Specific model ID to use

    Returns:
        Agent configured for code quality review
    """
    return Agent(
        name="Code Quality Reviewer",
        role="Review code for quality, readability, and best practices",
        model=get_model(provider=provider, model_id=model_id),
        instructions=[
            "You are an expert code reviewer focused on code quality.",
            'The codebase is in swift, the architecture is VIP, with an ongoing migration to MVVM.',
            "Analyze the diff and provide feedback on:",
            "- Code readability and clarity",
            "- Naming conventions (variables, functions, classes)",
            "- Code duplication (DRY principle violations)",
            "- Function/method complexity",
            "- Documentation and comments quality",
            "- Design patterns and architecture",
            "- Error handling practices",
            "",
            "Format your review as markdown with clear sections.",
            "Rate each issue as: Critical, High, Medium, or Low severity.",
            "Provide specific line references and suggested fixes.",
        ],
        markdown=True,
    )


def create_security_reviewer(provider: str = None, model_id: str = None):
    """
    Create a reviewer focused on security and performance.

    Args:
        provider: LLM provider to use
        model_id: Specific model ID to use

    Returns:
        Agent configured for security and performance review
    """
    return Agent(
        name="Security & Performance Reviewer",
        role="Review code for security vulnerabilities and performance issues",
        model=get_model(provider=provider, model_id=model_id),
        instructions=[
            "You are an expert security and performance reviewer.",
            'The codebase is in swift, the architecture is VIP, with an ongoing migration to MVVM.',
            "Analyze the diff and provide feedback on:",
            "- Security vulnerabilities (OWASP Top 10)",
            "- SQL injection, XSS, CSRF risks",
            "- Authentication/authorization issues",
            "- Sensitive data exposure",
            "- Input validation gaps",
            "- Performance bottlenecks",
            "- Memory management issues",
            "- Race conditions and concurrency problems",
            "- Resource leaks",
            "",
            "Format your review as markdown with clear sections.",
            "Rate each issue as: Critical, High, Medium, or Low severity.",
            "Provide specific line references and remediation steps.",
        ],
        markdown=True,
    )
