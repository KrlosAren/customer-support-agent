from typing import Callable, List, Dict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition

from app.agents.base.agent import Assistant
from app.utils.nodes_helpers import create_tool_node_with_fallback

from app.utils.logger import get_logger

logger = get_logger(__name__)


def supervisor_graph(
    builder,
    assistant: Assistant,
    tools: List[Callable],
    extra_nodes: Dict[str, Callable] = {},
) -> StateGraph:
    """Create the state graph for the supervisor agent."""
    logger.info("Creating supervisor graph")
    builder.add_node("fetch_user_info", extra_nodes.get("user_info", None))
    builder.add_edge(START, "fetch_user_info")
    builder.add_node("assistant", assistant)
    builder.add_node("tools", create_tool_node_with_fallback(tools))
    # Define edges: these determine how the control flow moves
    builder.add_edge("fetch_user_info", "assistant")

    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    # The checkpointer lets the graph persist its state
    # this is a complete memory for the entire graph.
    memory = MemorySaver()
    return builder.compile(checkpointer=memory, interrupt_before=["tools"])
