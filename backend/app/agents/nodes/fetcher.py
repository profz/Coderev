from app.agents.state import AgentState
from app.services.github import GitHubClient

async def fetch_pr_data(state: AgentState) -> dict:
    client = GitHubClient(token=state["installation_token"])
    
    pr = await client.get_pr(state["repo_full_name"], state["pr_number"])
    diff = await client.get_pr_diff(state["repo_full_name"], state["pr_number"])

    return {
        "pr_title": pr["title"],
        "pr_author": pr["user"]["login"],
        "diff": diff,
        "changed_files": [f["filename"] for f in pr.get("files", [])],
        "findings": [],   # initialize for parallel merge
    }
