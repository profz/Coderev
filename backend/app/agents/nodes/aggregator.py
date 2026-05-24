from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.services.github import GitHubClient
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)

llm = ChatGroq(model=settings.GROQ_MODEL, api_key=settings.GROQ_API_KEY, temperature=0.2)

AGGREGATOR_PROMPT = """
You are a senior engineer writing a pull request review summary.
Given a JSON list of findings (bugs, security, performance, code smells),
write a concise review comment in markdown.

Format it exactly like this:

## 🤖 AI Code Review Summary

**Verdict:** [🚨 Critical Issues Found / ⚠️ Needs Attention / ✅ Looks Good]

### By Severity
| Severity | Count |
|----------|-------|
| 🔴 Critical | N |
| 🟠 High | N |
| 🟡 Medium | N |
| 🟢 Low | N |

### Key Issues
- [category] **file.py:line** — short description

### Recommendation
One paragraph summary of what needs to be fixed before merging.

---
*Reviewed by AI Code Review Agent — bugs, security, performance, code smells*

Return ONLY the markdown. No JSON. No preamble.
"""

async def aggregate_and_post(state: AgentState) -> dict:
    findings = state.get("findings", [])
    logger.info(f"Aggregating {len(findings)} findings")

    # Generate summary
    summary_response = await llm.ainvoke([
        SystemMessage(content=AGGREGATOR_PROMPT),
        HumanMessage(content=json.dumps(findings, indent=2))
    ])
    summary = summary_response.content

    # Post top-level review comment
    client = GitHubClient(token=state["installation_token"])
    try:
        await client.post_review_comment(
            repo=state["repo_full_name"],
            pr_number=state["pr_number"],
            body=summary,
        )
        logger.info("Posted summary review comment")
    except Exception as e:
        logger.error(f"Failed to post summary: {e}")

    # Post line comments for critical/high only
    for f in findings:
        if f.get("severity") in ("critical", "high") and f.get("line_number"):
            try:
                await client.post_line_comment(
                    repo=state["repo_full_name"],
                    pr_number=state["pr_number"],
                    path=f["file_path"],
                    line=f["line_number"],
                    body=f"**[{f['category'].upper()} – {f['severity']}]** {f['message']}\n\n💡 {f['suggestion']}"
                )
            except Exception as e:
                logger.warning(f"Skipped line comment: {e}")

    return {"summary": summary}
