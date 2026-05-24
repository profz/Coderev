from langgraph.graph import StateGraph, END, START
from app.agents.state import AgentState
from app.agents.nodes.fetcher import fetch_pr_data
from app.agents.nodes.bug import detect_bugs
from app.agents.nodes.security import scan_security
from app.agents.nodes.performance import analyze_performance
from app.agents.nodes.smell import detect_smells
from app.agents.nodes.aggregator import aggregate_and_post

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("fetch_pr_data",       fetch_pr_data)
    graph.add_node("detect_bugs",         detect_bugs)
    graph.add_node("scan_security",       scan_security)
    graph.add_node("analyze_performance", analyze_performance)
    graph.add_node("detect_smells",       detect_smells)
    graph.add_node("aggregator",          aggregate_and_post)

    # Entry
    graph.add_edge(START, "fetch_pr_data")

    # Fan-out: fetch → all 4 agents IN PARALLEL
    graph.add_edge("fetch_pr_data", "detect_bugs")
    graph.add_edge("fetch_pr_data", "scan_security")
    graph.add_edge("fetch_pr_data", "analyze_performance")
    graph.add_edge("fetch_pr_data", "detect_smells")

    # Fan-in: all 4 agents → aggregator
    graph.add_edge("detect_bugs",         "aggregator")
    graph.add_edge("scan_security",       "aggregator")
    graph.add_edge("analyze_performance", "aggregator")
    graph.add_edge("detect_smells",       "aggregator")

    # Exit
    graph.add_edge("aggregator", END)

    return graph.compile()

review_graph = build_graph()
