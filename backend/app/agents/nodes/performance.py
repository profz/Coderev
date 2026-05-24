from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.agents.prompts.performance import PERFORMANCE_SYSTEM_PROMPT
from app.config import settings
from app.api.config import get_config
import json

def get_llm():
    cfg = get_config()
    return ChatGroq(model=cfg.model, api_key=settings.GROQ_API_KEY, temperature=0.1)

async def analyze_performance(state: AgentState) -> dict:
    llm = get_llm()
    response = await llm.ainvoke([
        SystemMessage(content=PERFORMANCE_SYSTEM_PROMPT),
        HumanMessage(content=f"PR Title: {state['pr_title']}\n\nDiff:\n{state['diff']}")
    ])
    try:
        findings = json.loads(response.content)
    except json.JSONDecodeError:
        findings = []
    for f in findings:
        f["category"] = "performance"
    return {"findings": findings}
