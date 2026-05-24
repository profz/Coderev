from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.agents.prompts.bug import BUG_SYSTEM_PROMPT
from app.config import settings
from app.api.config import get_config
import json

def get_llm():
    cfg = get_config()
    return ChatGroq(model=cfg.model, api_key=settings.GROQ_API_KEY, temperature=0.1)

async def detect_bugs(state: AgentState) -> dict:
    llm = get_llm()
    response = await llm.ainvoke([
        SystemMessage(content=BUG_SYSTEM_PROMPT),
        HumanMessage(content=f"PR Title: {state['pr_title']}\n\nDiff:\n{state['diff']}")
    ])
    try:
        findings = json.loads(response.content)
    except json.JSONDecodeError:
        findings = []
    for f in findings:
        f["category"] = "bug"
    return {"findings": findings}
