# Multi-Agent Code Review Tool

A CLI tool that automates code reviews using multiple AI agents. It analyzes git diffs between branches through specialized reviewers — one focused on **code quality** and another on **security & performance** — orchestrated by a **Judge agent** that synthesizes their findings into a structured, prioritized verdict.

Built with two interchangeable implementations: [Agno](https://github.com/agno-agi/agno) (default) and [LangGraph](https://github.com/langchain-ai/langgraph).

## How It Works

```
                         ┌──────────────┐
                         │    Judge     │
                         │ (Team Lead)  │
                         └──────┬───────┘
                     delegates to both reviewers
                       ┌────────┴────────┐
                       │                 │
              ┌────────▼──────┐  ┌───────▼─────────┐
              │ Code Quality  │  │   Security &     │
              │  Reviewer     │  │  Performance     │
              │               │  │   Reviewer       │
              └────────┬──────┘  └───────┬─────────┘
                       │                 │
                       └────────┬────────┘
                         findings merge
                       ┌────────▼────────┐
                       │  Final Verdict  │
                       │  (Markdown)     │
                       └─────────────────┘
```

1. The **Judge** fetches the git diff and changed file list using git tools
2. It delegates the diff to both specialized reviewers **simultaneously**
3. Each reviewer analyzes the diff through its own lens and returns findings rated by severity
4. The Judge consolidates, deduplicates, and prioritizes all findings into a final structured review
5. After the initial review, you can ask **follow-up questions** for additional rounds of analysis

## Project Structure

```
code_review_tool/
├── main.py                  # CLI entry point (Agno implementation)
├── team.py                  # Team orchestration — wires up Judge + reviewers + tools
├── config.py                # Model config — provider auto-detection, default models
├── requirements.txt         # Python dependencies
├── agents/
│   └── reviewers.py         # Specialized agent definitions (quality + security)
├── tools/
│   ├── git_tools.py         # GitTools toolkit — diff, branches, changed files
│   └── file_tools.py        # FileTools toolkit — read_file, find_file
└── langgraph_impl/          # Alternative LangGraph-based implementation
    ├── main.py              # CLI entry point (LangGraph)
    ├── graph.py             # ReAct-style state graph definition
    ├── config.py            # Model config (LangChain wrappers)
    ├── prompts.py           # System prompts for the Judge
    └── tools.py             # Tool definitions (git, file, reviewer sub-agents)
```

## Setup

### Prerequisites

- Python 3.10+
- Git
- An API key for at least one supported LLM provider

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd code_review_tool

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For the LangGraph implementation, also install:
pip install langgraph langchain-core langchain-anthropic langchain-openai
```

### API Keys

Set one (or more) of the following environment variables:

| Provider   | Environment Variable   | Default Model                   |
|------------|------------------------|---------------------------------|
| Anthropic  | `ANTHROPIC_API_KEY`    | `claude-sonnet-4-20250514`      |
| OpenAI     | `OPENAI_API_KEY`       | `gpt-4o`                        |
| OpenRouter | `OPENROUTER_API_KEY`   | `anthropic/claude-sonnet-4`     |

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

If no `--provider` flag is given, the tool auto-detects based on which API key is set (priority: Anthropic > OpenAI > OpenRouter).

## Usage

### Agno Implementation (default)

```bash
# Auto-detect provider from available API keys
python main.py --source feature-branch --target main

# Use a specific provider
python main.py --source dev --target main --provider openrouter

# Use a specific provider and model
python main.py --source dev --target main --provider openrouter --model anthropic/claude-sonnet-4

# Point to a different repository
python main.py --source dev --target main --repo /path/to/repo
```

### LangGraph Implementation

```bash
python -m langgraph_impl.main --source feature-branch --target main
```

Both implementations accept the same CLI arguments:

| Argument            | Required | Description                                      |
|---------------------|----------|--------------------------------------------------|
| `--source`, `-s`    | Yes      | Source branch containing the changes              |
| `--target`, `-t`    | Yes      | Target branch to compare against (e.g., `main`)  |
| `--repo`, `-r`      | No       | Path to the git repository (default: `.`)         |
| `--provider`, `-p`  | No       | LLM provider: `anthropic`, `openai`, `openrouter` |
| `--model`, `-m`     | No       | Model ID override (uses provider default)         |

### Interactive Follow-ups

After the initial review, the tool enters an interactive loop where you can ask follow-up questions:

```
────────────────────────────────────────────────────
  Enter follow-up feedback for another review round,
  or 'q' to end the session.
────────────────────────────────────────────────────

> Can you look more closely at the error handling in NetworkManager.swift?
```

Type `q`, `quit`, `exit`, `done`, or press Enter on an empty line to end the session.

## Output Format

The review is output as a structured markdown document with the following sections:

- **Code Quality Reviewer Output** — readability, naming, DRY, complexity, design patterns, error handling
- **Security & Performance Reviewer Output** — vulnerabilities, OWASP Top 10, auth, data exposure, memory, concurrency
- **Must Fix** — critical issues with specific line references, code blocks, and suggested fixes
- **Should Fix** — high/medium severity issues with line references and fix ideas
- **Refactoring Opportunities** — code quality improvements with suggested refactorings

The Judge also provides an **Executive Summary** and a **Final Verdict**: `APPROVE`, `REQUEST CHANGES`, or `NEEDS DISCUSSION`.

## Architecture Details

### Agno Implementation

Uses the [Agno](https://github.com/agno-agi/agno) multi-agent framework. The `Team` class handles orchestration — the Judge is the team leader with `delegate_to_all_members=True`, meaning both reviewers run in parallel. Session context is preserved in an `InMemoryDb` for follow-up rounds.

### LangGraph Implementation

Uses a [ReAct-style](https://arxiv.org/abs/2210.03629) state graph where the Judge loops between reasoning and tool execution. The reviewer sub-agents are exposed as tools (`quality_review`, `security_review`) that the Judge can invoke. The graph uses `InMemorySaver` for checkpointing between rounds and streams output token-by-token.

```
START → judge → should_continue? → tools → judge → ... → END
```

### Tools Available to Agents

| Tool               | Description                                      |
|--------------------|--------------------------------------------------|
| `get_diff`         | Unified diff between two branches                |
| `get_changed_files`| List of files modified between branches          |
| `get_branches`     | All available git branches                       |
| `read_file`        | Read file contents (path-validated, 50KB limit)  |
| `find_file`        | Search repository for files by name              |

## License

This project is unlicensed. Feel free to use it as you see fit.
