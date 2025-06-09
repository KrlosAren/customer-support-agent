from typing import Callable, List
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition

from app.agents.base.agent import Assistant
from app.agents.supervisor.state import TraveleAgentState
from app.utils.nodes_helpers import create_tool_node_with_fallback


def supervisor_graph(assistant: Assistant, tools: List[Callable]) -> StateGraph:
    """Create the state graph for the supervisor agent."""
    builder = StateGraph(state_schema=TraveleAgentState)

    builder.add_node("assistant", assistant)
    builder.add_node("tools", create_tool_node_with_fallback(tools))

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)
