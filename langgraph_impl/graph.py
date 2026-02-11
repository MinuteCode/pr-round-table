"""
LangGraph graph definition for the code review tool.

Builds a ReAct-style graph where the Judge agent reasons in a loop,
calling tools (git, file, and reviewer sub-agents) until it has
synthesized a final review.

Graph topology:
    START → judge → {tools, END}
    tools → judge
"""

from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from langgraph_impl.config import get_model
from langgraph_impl.tools import create_tools
from langgraph_impl.prompts import JUDGE_SYSTEM_PROMPT


def build_graph(
    repo_path: str = ".", provider: str = None, model_id: str = None
):
    """
    Build and compile the code review graph.

    Args:
        repo_path: Path to the git repository
        provider: LLM provider to use
        model_id: Specific model ID to use

    Returns:
        A compiled StateGraph with InMemorySaver checkpointer
    """
    tools = create_tools(
        repo_path=repo_path, provider=provider, model_id=model_id
    )
    model = get_model(provider=provider, model_id=model_id)
    model_with_tools = model.bind_tools(tools)

    tools_by_name = {t.name: t for t in tools}

    def judge_node(state: MessagesState):
        """The Judge agent: reasons about the review and decides next actions."""
        messages = [SystemMessage(content=JUDGE_SYSTEM_PROMPT)] + list(
            state["messages"]
        )
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    def tool_node(state: MessagesState):
        """Execute tool calls from the Judge's last message."""
        outputs = []
        last_message = state["messages"][-1]
        for tool_call in last_message.tool_calls:
            try:
                tool_func = tools_by_name[tool_call["name"]]
                result = tool_func.invoke(tool_call["args"])
            except Exception as e:
                result = f"Error executing tool '{tool_call['name']}': {e}"
            outputs.append(
                ToolMessage(
                    content=str(result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

    def should_continue(state: MessagesState) -> str:
        """Route to tools if the Judge made tool calls, otherwise end."""
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(MessagesState)
    workflow.add_node("judge", judge_node)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("judge")
    workflow.add_conditional_edges(
        "judge", should_continue, {"tools": "tools", END: END}
    )
    workflow.add_edge("tools", "judge")

    checkpointer = InMemorySaver()
    return workflow.compile(checkpointer=checkpointer)
