# ◈ coderev `ai`

> Automated pull request analysis powered by LLM agents. Detects bugs, security vulnerabilities, performance bottlenecks, and code smells — posted directly as GitHub review comments.

---

## What it does

Every time a PR is opened or updated, coderev spins up a multi-agent pipeline that analyzes the diff in parallel across four dimensions and posts findings back to GitHub as line-level comments — within seconds.

```
PR opened on GitHub
    ↓ webhook
FastAPI validates + queues
    ↓ Redis
Worker → LangGraph
    ↓ parallel execution
    ├── 🐛 Bug Detector
    ├── 🔒 Security Scanner
    ├── ⚡ Performance Analyzer
    └── 🧹 Code Smell Detector
    ↓ aggregator
GitHub PR comments + line annotations
    ↓
Dashboard — findings grouped by severity and category
```

---

## Stack

| Layer | Technology |
|---|---|
| Agent framework | LangGraph (parallel fan-out) |
| LLM inference | Groq / LLaMA 3.3 70B |
| Backend | FastAPI + Python 3.14 |
| Queue | Redis + RQ |
| Database | PostgreSQL + SQLAlchemy async |
| Frontend | Nuxt 3 (Vue 3) |
| GitHub integration | Webhooks + REST API |

---

## Architecture

```
backend/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── config.py                # Settings via pydantic-settings
│   ├── database.py              # Async SQLAlchemy engine
│   ├── api/
│   │   ├── webhook.py           # GitHub webhook receiver + HMAC verification
│   │   ├── reviews.py           # Review CRUD endpoints
│   │   ├── config.py            # Runtime config (repo, model)
│   │   └── health.py
│   ├── agents/
│   │   ├── state.py             # AgentState TypedDict
│   │   ├── graph.py             # LangGraph graph definition
│   │   ├── nodes/
│   │   │   ├── fetcher.py       # Fetch PR diff from GitHub API
│   │   │   ├── bug.py           # Bug detection agent
│   │   │   ├── security.py      # Security vulnerability agent
│   │   │   ├── performance.py   # Performance analysis agent
│   │   │   ├── smell.py         # Code smell agent
│   │   │   └── aggregator.py    # Merge findings + post to GitHub
│   │   └── prompts/             # System prompts per agent
│   ├── services/
│   │   ├── github.py            # GitHub API client
│   │   └── reviewer.py          # Orchestrates agent pipeline
│   └── worker/
│       └── worker.py            # RQ worker entrypoint
frontend/
└── app/
    ├── pages/
    │   ├── index.vue            # Dashboard
    │   └── reviews/[id].vue     # Review detail
    └── composables/
        └── useReviews.ts
```

---

## Agent Graph

```
START
  └─► fetch_pr_data
           ├─► detect_bugs ──────────┐
           ├─► scan_security ────────┤  (parallel via LangGraph fan-out)
           ├─► analyze_performance ──┤
           └─► detect_smells ────────┘
                                     └─► aggregator ──► END
                                          │
                                          ├── POST summary comment
                                          ├── POST line comments (critical/high)
                                          └── SAVE to PostgreSQL
```

Parallel execution uses `Annotated[list[Finding], operator.add]` in `AgentState` — findings from all 4 agents are automatically merged without race conditions.

---

## Setup

### Prerequisites

```bash
sudo pacman -S python python-pip nodejs npm redis postgresql
```

### Backend

```bash
cd backend
uv venv .venv && source .venv/bin/activate

uv pip install fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg \
  alembic pydantic-settings httpx redis rq langgraph \
  langchain-groq langchain-core python-dotenv psycopg2-binary
```

### Frontend

```bash
cd frontend
npm install
npm install marked
```

### Environment

```bash
# backend/.env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your_secret_here
GROQ_API_KEY=gsk_xxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/codereview
PUBLIC_URL=https://your-tunnel-url.serveousercontent.com
```

### Database

```bash
cd backend
alembic upgrade head
```

---

## Running

```bash
# Terminal 1 — tunnel
ssh -R yourname:80:localhost:8000 serveo.net

# Terminal 2 — API
cd backend && source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3 — worker
cd backend && source .venv/bin/activate
python -m app.worker.worker

# Terminal 4 — frontend
cd frontend && npm run dev
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/webhooks/github` | GitHub webhook receiver |
| `GET` | `/api/reviews/` | List all reviews |
| `GET` | `/api/reviews/{id}` | Get review with findings |
| `GET` | `/api/config/` | Get current config |
| `PUT` | `/api/config/` | Update repo + model |
| `GET` | `/api/config/models` | List available models |
| `GET` | `/api/config/status` | Runtime status check |
| `GET` | `/health` | Health check |

---

## Findings Schema

Each agent returns findings in this format:

```json
{
  "category": "bug | security | performance | smell",
  "severity": "critical | high | medium | low",
  "file_path": "path/to/file.py",
  "line_number": 42,
  "message": "What the issue is",
  "suggestion": "How to fix it"
}
```

---

## What each agent catches

**🐛 Bug Detector**
Null dereferences, off-by-one errors, unhandled exceptions, resource leaks, race conditions, incorrect logic

**🔒 Security Scanner**
SQL injection, XSS, hardcoded secrets, insecure deserialization, path traversal, missing auth checks, sensitive data in logs, weak cryptography

**⚡ Performance Analyzer**
N+1 queries, O(n²) algorithms, blocking calls in async contexts, missing pagination, unnecessary loops, missing caching

**🧹 Code Smell Detector**
Functions over 40 lines, deep nesting, magic numbers, duplicate code, misleading names, dead code

---

## Supported Models

| Model | Speed | Quality |
|---|---|---|
| `llama-3.3-70b-versatile` | Fast | ⭐⭐⭐⭐⭐ |
| `llama-3.1-8b-instant` | Very fast | ⭐⭐⭐ |
| `mixtral-8x7b-32768` | Fast | ⭐⭐⭐⭐ |
| `gemma2-9b-it` | Fast | ⭐⭐⭐ |

Model is switchable at runtime via the dashboard settings panel — no restart required.

---

## Dashboard

- Live polling every 5 seconds
- Stats: total reviews, completed, critical findings, issues found
- Per-review: severity strip, markdown summary, findings grouped by category
- Settings: target repo configuration, model selection

---

## License

MIT
