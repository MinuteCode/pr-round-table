#!/usr/bin/env python3
"""
Multi-Agent Code Review Tool

A CLI tool that reviews git diffs using multiple AI agents:
- Code Quality Reviewer: Focuses on readability and best practices
- Security & Performance Reviewer: Focuses on vulnerabilities and performance
- Judge: Synthesizes both reviews into a final verdict

Supports multiple review rounds: after the initial review, you can ask
follow-up questions or request deeper analysis on specific areas.

Usage:
    python main.py --source <branch> --target <branch> [options]

Example:
    python main.py --source feature/new-api --target main
    python main.py --source dev --target main --provider openrouter --model anthropic/claude-sonnet-4
"""

import argparse
import uuid
from team import create_review_team


def print_round_header(round_num: int, title: str):
    """Print a formatted round header."""
    print(f"\n{'=' * 60}")
    print(f"  ROUND {round_num} — {title}")
    print(f"{'=' * 60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Review code changes between git branches using AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect provider from available API keys
  python main.py --source feature-branch --target main

  # Use specific provider
  python main.py --source dev --target main --provider openrouter

  # Use specific provider and model
  python main.py --source dev --target main --provider openrouter --model anthropic/claude-sonnet-4

  # Specify repository path
  python main.py --source dev --target main --repo /path/to/repo

Supported providers:
  - anthropic  (requires ANTHROPIC_API_KEY)
  - openai     (requires OPENAI_API_KEY)
  - openrouter (requires OPENROUTER_API_KEY)

Default models:
  - anthropic:  claude-sonnet-4-20250514
  - openai:     gpt-4o
  - openrouter: anthropic/claude-sonnet-4
        """,
    )
    parser.add_argument(
        "--source",
        "-s",
        required=True,
        help="Source branch containing the changes",
    )
    parser.add_argument(
        "--target",
        "-t",
        required=True,
        help="Target branch to compare against (e.g., main)",
    )
    parser.add_argument(
        "--repo",
        "-r",
        default=".",
        help="Path to git repository (default: current directory)",
    )
    parser.add_argument(
        "--provider",
        "-p",
        choices=["anthropic", "openai", "openrouter"],
        default=None,
        help="LLM provider (auto-detects from API keys if not specified)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default=None,
        help="Model ID to use (uses provider default if not specified)",
    )

    args = parser.parse_args()

    provider_info = (
        f" using {args.provider}" if args.provider else " (auto-detecting provider)"
    )
    print(f"Starting code review: {args.source} -> {args.target}{provider_info}")

    team = create_review_team(
        repo_path=args.repo,
        provider=args.provider,
        model_id=args.model,
    )

    session_id = str(uuid.uuid4())

    prompt = f"""
    Please review the code changes from branch '{args.source}'
    compared to branch '{args.target}'.

    The codebase is in swift, it's an iOS/tvOS app, the architecture is VIP, with an ongoing migration to MVVM.

    Steps:
    0. Use find_file to look for AGENTS.md or CLAUDE.md, and if found, use read_file to read them for project context
    1. First, use get_changed_files to see what files were modified
    2. Then use get_diff to get the full diff
    3. Delegate the review to both reviewers
    4. Summarize both reviews into their respective sections
    5. Synthesize their feedback into a final verdict. Use concrete filepaths from the codebase and blocks of code from the codebase, without exceeding 20 lines

    For critical issues, you MUST provide specific line references and suggested fixes and MUST provide a specific code block from the call site.
    For high to medium isssues, provide the line of code that's responsible and an adequate fix idea

    Write your finding in a nicely formatted, to the point and super clear markdown document called [branch_name]_code_review.md, with the following sections:
    # Code Quality reviewer output
    [The code quality reviewer's feedback goes here]
    # Security & Performance reviewer output
    [The security & performance reviewer's feedback goes here]

    # Must Fix
    [A concise list of critical issues that MUST be fixed before merging, with specific line references and suggested fixes. Include code blocks from the call site for each issue, without exceeding 40 lines.]

    # Should Fix
    [A concise list of high to medium severity issues that SHOULD be fixed before merging, with specific line references and suggested fixes. Include code blocks from the call site for each issue, without exceeding 20 lines.]

    # Refactoring opportunities
    [A concise list of code quality improvements that could be made, with specific line references and suggested refactorings. Include code blocks from the call site for each opportunity, without exceeding 20 lines.]
    """

    # Round 1: Initial code review
    print_round_header(1, "Initial Code Review")

    team.print_response(
        prompt,
        stream=True,
        show_message=False,
        session_id=session_id,
    )

    # Interactive follow-up rounds
    round_num = 2
    while True:
        print(f"\n{'-' * 60}")
        print("  Enter follow-up feedback for another review round,")
        print("  or 'q' to end the session.")
        print(f"{'-' * 60}")

        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ("q", "quit", "exit", "done", ""):
            break

        print_round_header(round_num, "Follow-up Review")

        team.print_response(
            user_input,
            stream=True,
            show_message=False,
            session_id=session_id,
        )

        round_num += 1

    print("\nReview session complete.")


if __name__ == "__main__":
    main()
