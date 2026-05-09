"""
frontend/INTEGRATION_GUIDE.md
──────────────────────────────
Guide for integrating the Streamlit frontend with the FastAPI backend.
"""

# Frontend & Backend Integration Guide

## Quick Start

### Step 1: Install Backend Dependencies
From the project root:
```bash
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies
```bash
cd frontend
pip install -r requirements.txt
cd ..
```

### Step 3: Start the Backend API
```bash
python main.py --seed
# Or if data is already seeded:
python main.py
```

The backend will start on `http://localhost:8000`

### Step 4: Start the Frontend UI
In a new terminal:
```bash
cd frontend
python run.py
```

The UI will be available at `http://localhost:8501`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         STREAMLIT UI                            │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Chat    │  │Diagnostic  │  │Transform │  │Orchestration│  │
│  │Interface │  │ Response   │  │ Alert    │  │  Animation  │  │
│  └──────────┘  └────────────┘  └──────────┘  └──────────────┘  │
│                                                                   │
│                    HTTP Client (requests)                        │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ REST API Calls
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Orchestrator (run_orchestrator)             │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ Group A Agents (Parallel):                              │   │
│  │  • PerformanceAnalysisAgent                             │   │
│  │  • FundFlowAgent                                        │   │
│  │  • MarketIntelligenceAgent                              │   │
│  │  • CompetitorIntelligenceAgent                          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ Group B Agents (Sequential):                            │   │
│  │  • RecommendationAgent (waits for Group A)              │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ Conflict Resolution & Confidence Scoring                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               Data Layer                                 │   │
│  │  • SQLite Database (fund data, performance)             │   │
│  │  • ChromaDB Vector Store (semantic search)              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## API Endpoints

### 1. Health Check
```
GET /health
```
Response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "db": "ok",
  "vector_store": "ok"
}
```

### 2. Diagnose
```
POST /diagnose
Content-Type: application/json

{
  "query": "Why did our Global Equity Fund slow down?",
  "fund_id": "GEF001",
  "period": "2026-Q1",
  "user_id": "advisor_name",
  "mode": "standard"
}
```

Response:
```json
{
  "trace_id": "uuid-string",
  "fund_id": "GEF001",
  "period": "2026-Q1",
  "generated_at": "2026-05-08T10:30:00Z",
  "latency_ms": 2300,
  "overall_confidence": {
    "level": "HIGH",
    "score": 0.85
  },
  "root_cause": {
    "primary_issue": "...",
    "impact": "...",
    "contributing_factors": [...],
    "severity": "HIGH",
    "macro_headwinds": [...],
    "risk_events": [...]
  },
  "peer_comparison": {
    "rankings": [...],
    "our_ranking": "25th percentile",
    "strategy_gap": {...}
  },
  "recommendations": [
    {
      "title": "...",
      "description": "...",
      "impact": "...",
      "rationale": "...",
      "sources": [...],
      "approval_status": "GREEN|AMBER|RED"
    }
  ],
  "conflicts_detected": false,
  "conflicts_summary": [],
  "disclaimer": "..."
}
```

### 3. Audit Record
```
GET /audit/{trace_id}
```

Returns audit information including agent calls, timing, and confidence factors.

### 4. Full Audit Trail
```
GET /audit/{trace_id}/detail
```

Returns complete Show Your Work audit trail with all intermediate steps.

### 5. Approve Recommendation
```
POST /audit/{trace_id}/approve
Content-Type: application/json

{
  "approved_by": "user_id"
}
```

## Frontend Components

### Chat Interface (`components/chat_interface.py`)
- Displays conversation history
- Suggested prompts for quick queries
- Query input area
- Export functionality

### Diagnostic Response (`components/diagnostic_response.py`)
- **Overview Tab**: Key metrics, root cause, headwinds
- **Performance Tab**: Returns, sectors, regions
- **Peers Tab**: Rankings, gap analysis
- **Recommendations Tab**: Actions with approval workflow

### Transparency Layer (`components/transparency_layer.py`)
- Confidence badges and scores
- Agent execution pills with latency
- Audit trail tabs:
  - Agent Calls: Full execution trace
  - Confidence Factors: 5-factor breakdown
  - Conflicts: Resolution documentation
  - Sources: Data hierarchy

### Orchestration Animation (`components/orchestration_animation.py`)
- Visual representation of parallel execution
- Agent status indicators
- Progress bars
- Execution timeline

## State Management

Session state is managed via `utils/state_manager.py` and Streamlit's built-in `st.session_state`:

```python
st.session_state.messages       # Conversation history
st.session_state.current_response  # Latest diagnostic response
st.session_state.trace_id       # Current trace ID
st.session_state.fund_id        # Selected fund
st.session_state.period         # Selected period
st.session_state.user_id        # Current user
```

## Configuration

### Backend Configuration
See `core/config.py` for backend settings:
- Database paths
- Vector store configuration
- Log levels
- API settings

### Frontend Configuration
See `frontend/config.py` for UI settings:
- API endpoints
- Default values
- Suggested prompts
- Color palettes
- Animation settings

Edit `.env` files to override defaults:
- Backend: `.env` in project root
- Frontend: `frontend/.env`

## Data Flow

### Query Processing
1. User types query in UI
2. UI sends POST to `/diagnose`
3. Backend orchestrator receives request
4. Group A agents run in parallel
5. Recommendation agent runs sequentially
6. Conflict resolution and confidence scoring
7. Response formatted and returned
8. UI renders multi-tab diagnostic response

### Audit Trail
1. Each agent execution logged with:
   - Agent name and timestamp
   - Tool calls and parameters
   - Latency and confidence
   - Output payload

2. Inter-agent conflicts detected and logged
3. Confidence score computed with 5 factors
4. Full trace persisted to database
5. UI fetches audit via `/audit/{trace_id}`

## Troubleshooting

### "Failed to connect to API"
- Ensure backend is running: `python main.py`
- Check `API_BASE_URL` in `frontend/.env`
- Verify CORS is enabled in backend

### "Module not found: streamlit"
- Install frontend dependencies: `pip install -r frontend/requirements.txt`
- Ensure virtual environment is activated

### "Agent execution shows no data"
- Verify backend has data seeded: `python main.py --seed`
- Check database path in `core/config.py`
- Review backend logs for errors

### "Animations not rendering"
- Ensure Streamlit version ≥ 1.35.0
- Check browser console for JavaScript errors
- Clear Streamlit cache: `streamlit cache clear`

### "Latency too high"
- Check backend performance (watch agent logs)
- Verify database queries are optimized
- Check network latency with health endpoint

## Development Tips

### Local Development Workflow
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend
streamlit run app.py --logger.level=debug
```

### Adding New Endpoints
1. Add route to `api/main.py`
2. Create corresponding API client method in `frontend/utils/api_client.py`
3. Create UI component for displaying response
4. Update UI to call the endpoint

### Customizing UI
- Colors and styling: `frontend/styles/theme.py`
- Suggested prompts: `frontend/config.py`
- Component layouts: `frontend/components/*.py`
- Page configuration: `frontend/.streamlit/config.toml`

### Debugging
- Backend: Check `logs/app.log`
- Frontend: Use `st.write()` for debugging
- API: Test endpoints with curl or Postman
- Database: Query SQLite directly with `sqlite3 database.db`

## Performance Optimization

### Frontend
- Response caching with Streamlit cache
- Lazy loading of heavy components
- Optimized dataframe rendering

### Backend
- Parallel agent execution
- Vector store caching
- Database query optimization
- Connection pooling

### Network
- Keep-alive connections
- Compressed responses
- Efficient JSON serialization

## Security Considerations

- All API calls include CORS headers
- User ID tracked for audit trail
- Sensitive data not logged in UI
- Backend validates all inputs
- Database uses read-only queries where possible

## Next Steps

1. **Customize Branding**: Update colors and logos in `frontend/styles/theme.py`
2. **Add Analytics**: Integrate Mixpanel or similar for usage tracking
3. **Enhance Reports**: Add PDF export functionality
4. **Mobile Support**: Implement responsive design
5. **Real-time Updates**: Add WebSocket support for live agent updates
6. **Advanced Filtering**: Add peer comparison filters and custom ranges
