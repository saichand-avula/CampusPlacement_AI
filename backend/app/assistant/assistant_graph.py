from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from assistant.assistant_state import AssistantState



from assistant.assistant_nodes.assistant import (
    assistant_node,
    tools,
)

from assistant.assistant_nodes.short_term_memory import (
    short_term_memory,
)

from assistant.assistant_nodes.long_term_memory import (
    long_term_memory,
)


_graph = None


def init_graph(store):

    global _graph

    builder = StateGraph(AssistantState)

    builder.add_node(
        "assistant",
        assistant_node,
    )

    builder.add_node(
        "tools",
        ToolNode(tools),
    )

    builder.add_node(
        "short_term_memory",
        short_term_memory,
    )

    builder.add_node(
        "long_term_memory",
        long_term_memory,
    )

    builder.add_edge(
        START,
        "assistant",
    )

    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )

    builder.add_edge(
        "tools",
        "assistant",
    )

    builder.add_edge(
        "assistant",
        "short_term_memory",
    )

    builder.add_edge(
        "assistant",
        "long_term_memory",
    )

    builder.add_edge(
        "short_term_memory",
        END,
    )

    builder.add_edge(
        "long_term_memory",
        END,
    )

    _graph = builder.compile(
        store=store,
    )


def get_graph():

    if _graph is None:
        raise RuntimeError(
            "Assistant graph has not been initialized."
        )

    return _graph