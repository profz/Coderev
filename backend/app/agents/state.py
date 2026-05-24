from typing import TypedDict, Annotated, Optional
import operator

class Finding(TypedDict):
    category: str       # bug | security | performance | smell
    severity: str       # critical | high | medium | low
    file_path: str
    line_number: Optional[int]
    message: str
    suggestion: str

class AgentState(TypedDict):
    # --- Input ---
    repo_full_name: str
    pr_number: int
    installation_token: str

    # --- Fetched by fetcher node ---
    pr_title: str
    pr_author: str
    diff: str                   # raw unified diff
    changed_files: list[str]

    # --- Parallel agent findings ---
    # Annotated with operator.add so each agent's list is merged
    findings: Annotated[list[Finding], operator.add]

    # --- Aggregator output ---
    summary: str
    review_id: str

    # --- Error propagation ---
    error: Optional[str]
