# Fund Performance Diagnostic AI System
### Multi-Agent POC — Local Environment

A multi-agent AI system that autonomously investigates fund performance by orchestrating
specialized agents across data domains. Built with **Strands Agents** + **OpenAI GPT-4o**,
running fully locally with **SQLite** and **ChromaDB**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | Strands Agents |
| LLM Provider | OpenAI GPT-4o |
| Structured DB | SQLite (local) |
| Vector Store | ChromaDB (local, in-process) |
| API Layer | FastAPI |
| Language | Python 3.11+ |

---

## Project Structure

```
fund-diagnostic-ai/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py                         # Entry point — runs the FastAPI app
│
├── data/
│   ├── schema/
│   │   └── init_db.py              # Creates all SQLite tables
│   └── mock/
│       ├── seed_fund_performance.py
│       ├── seed_sector_attribution.py
│       ├── seed_geographic_attribution.py
│       ├── seed_aum_flows.py
│       ├── seed_competitor.py
│       ├── seed_market_intelligence.py
│       └── seed_unstructured.py    # Seeds ChromaDB vector store
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py             # Master orchestrator agent
│   ├── performance_agent.py        # Fund returns & attribution analysis
│   ├── flow_agent.py               # AUM, net flows, regional/channel
│   ├── market_agent.py             # Macro indicators, sector trends, RAG
│   ├── competitor_agent.py         # Peer benchmarking & rankings
│   └── recommendation_agent.py    # Synthesizes findings → actions
│
├── tools/
│   ├── __init__.py
│   ├── db_tools.py                 # All SQLite query tools (Strands @tool)
│   ├── vector_tools.py             # ChromaDB search tools (Strands @tool)
│   └── market_tools.py             # Mock market data tools (Strands @tool)
│
├── core/
│   ├── __init__.py
│   ├── config.py                   # All config, env vars, constants
│   ├── database.py                 # SQLite connection & session management
│   ├── vector_store.py             # ChromaDB client initialization
│   ├── audit.py                    # Audit trail logging (SQLite)
│   ├── confidence.py               # Confidence scoring engine
│   ├── output_formatter.py         # Formats final executive response
│   └── exceptions.py               # Custom exceptions
│
├── api/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app & route definitions
│   ├── models.py                   # Pydantic request/response models
│   └── dependencies.py             # FastAPI dependency injection
│
├── tests/
│   ├── __init__.py
│   ├── test_db_tools.py
│   ├── test_performance_agent.py
│   ├── test_flow_agent.py
│   ├── test_market_agent.py
│   ├── test_competitor_agent.py
│   ├── test_recommendation_agent.py
│   └── test_orchestrator.py
│
├── logs/                           # Runtime logs (gitignored)
├── vector_store/                   # ChromaDB persistent storage (gitignored)
└── docs/                           # Reference documents
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment
```bash
cp .env.example .env
# Add your OpenAI API key to .env
```

### 3. Initialize database & seed mock data
```bash
python data/schema/init_db.py
python data/mock/seed_fund_performance.py
python data/mock/seed_sector_attribution.py
python data/mock/seed_geographic_attribution.py
python data/mock/seed_aum_flows.py
python data/mock/seed_competitor.py
python data/mock/seed_market_intelligence.py
python data/mock/seed_unstructured.py
```

### 4. Run the API
```bash
uvicorn api.main:app --reload --port 8000
```

### 5. Query the system
```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{"query": "Why did our Global Equity Fund slow down this quarter?", "fund_id": "GEF001", "period": "2026-Q1"}'
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/diagnose` | Main diagnostic query |
| GET | `/audit/{trace_id}` | Retrieve full audit trail for a trace |
| GET | `/audit/{trace_id}/detail` | Show Your Work — full reasoning chain |
| GET | `/health` | Health check |

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENAI_MODEL` | Model to use (default: gpt-4o) | No |
| `DB_PATH` | SQLite database file path | No |
| `CHROMA_PATH` | ChromaDB persistence directory | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |
| `CONFIDENCE_THRESHOLD` | Minimum confidence to auto-clear (default: 0.75) | No |

---

## Development Notes

- All mock data is self-consistent — signals across all tables tell a coherent story
- ChromaDB runs in-process (no server needed)
- SQLite file is created automatically on first run
- Audit logs are stored in the same SQLite database under the `audit_log` table
- To reset everything: delete `fund_diagnostic.db` and the `vector_store/` directory
