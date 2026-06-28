from langgraph.graph import StateGraph, START, END
from graphs.state import mystate
from graphs.nodes.eoi_feilds_extractor import extract_fields
from graphs.nodes.jd_extractor import jd_extractor

builder = StateGraph(mystate)

builder.add_node("jd_text_links_extractor",jd_extractor)
builder.add_node("eoi_feild_extractor",extract_fields)

builder.add_edge(START, "jd_text_links_extractor")
builder.add_edge("jd_text_links_extractor","eoi_feild_extractor")
builder.add_edge("eoi_feild_extractor",END)
graph = builder.compile()
