from langgraph.graph import StateGraph, START, END
from graphs.state import mystate
from graphs.nodes.eoi_feilds_extractor import extract_fields
from graphs.nodes.jd_extractor import jd_extractor
from graphs.nodes.form_creater import create_form

builder = StateGraph(mystate)

builder.add_node("jd_text_links_extractor", jd_extractor)
builder.add_node("eoi_feild_extractor", extract_fields)
builder.add_node("form_feilds_extractor", create_form)

builder.add_edge(START, "jd_text_links_extractor")
builder.add_edge("jd_text_links_extractor", "eoi_feild_extractor")
builder.add_edge("jd_text_links_extractor", "form_feilds_extractor")
builder.add_edge("eoi_feild_extractor", END)
builder.add_edge("form_feilds_extractor", END)

_graph = None


def init_graph(store):
    global _graph

    _graph = builder.compile(store=store)


def get_graph():
    if _graph is None:
        raise RuntimeError(
            "Graph has not been initialized. Call init_graph() first."
        )

    return _graph
