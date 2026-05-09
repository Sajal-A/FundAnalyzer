# Fund Performance Diagnostic AI - Frontend

Interactive Streamlit UI for the Fund Performance Diagnostic AI system.

## Features

### 💬 Chat Interface
- Natural language query input
- Suggested prompts for quick analysis
- Full conversation history with timestamps
- Export conversation and analysis

### 🎬 Orchestration Animation
- Real-time visualization of parallel agent execution
- Group A agents (Performance, Flow, Market, Competitor) shown running in parallel
- Recommendation agent shown waiting for Group A results
- Execution timeline and performance metrics

### 📈 Diagnostic Response Tabs

#### Overview Tab
- Key metrics (Confidence, Latency, Fund ID, Period)
- Root cause analysis with severity levels
- Macro headwinds and risk events
- Primary issues and contributing factors

#### Performance Tab
- Monthly returns table and comparison to benchmark
- Sector attribution bar chart
- Regional distribution (North America, Europe, Asia Pacific)
- Channel breakdown (Direct, Mutual, ETF)

#### Peers Tab
- Category ranking table with percentiles
- Our fund position highlighted
- Performance gap vs peers
- Strategy gap analysis and differences

#### Recommendations Tab
- 4 recommended actions with expandable details
- Action descriptions, impact, and rationale
- Supporting agents and source citations
- GREEN/AMBER/RED approval status with working approve button

### 🔍 Transparency Layer
- Confidence badges with scoring
- Checkpoint tier indicators
- Latency metrics
- Trace ID reference

**Show Your Work - Audit Trail Tabs:**
1. **Agent Calls** - Full tool list per agent, parallel vs sequential execution flags
2. **Confidence Factors** - 5-factor weighted score breakdown with individual bars
3. **Conflicts** - Inter-agent disagreement, resolution logic, winning agent
4. **Sources** - Data tier hierarchy (SQLite → ChromaDB → Market APIs)

### 💬 Follow-up Questions
- Quick-reply buttons with common follow-ups
- Free-text follow-up input
- Context carried forward in conversation
- Each follow-up gets its own confidence score and trace ID

## Setup

### Prerequisites
- Python 3.9+
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
cd frontend
pip install -r requirements.txt
```

2. Create a `.env` file:
```env
API_BASE_URL=http://localhost:8000
API_TIMEOUT=60
```

### Running the UI

```bash
streamlit run app.py
```

The UI will be available at `http://localhost:8501`

## Project Structure

```
frontend/
├── app.py                              # Main Streamlit application
├── requirements.txt                    # Frontend dependencies
├── config.py                          # Configuration settings
├── .streamlit/
│   └── config.toml                    # Streamlit configuration
├── components/
│   ├── __init__.py
│   ├── chat_interface.py              # Chat UI component
│   ├── diagnostic_response.py         # Multi-tab diagnostic response
│   ├── transparency_layer.py          # Audit trail and transparency
│   └── orchestration_animation.py    # Agent execution visualization
├── utils/
│   ├── __init__.py
│   ├── api_client.py                 # Backend API client
│   └── state_manager.py              # Session state management
├── styles/
│   ├── __init__.py
│   └── theme.py                      # Custom CSS and styling
└── README.md                          # This file
```

## API Integration

The frontend communicates with the backend via REST API:

### Endpoints Used
- `GET /health` - API health check
- `POST /diagnose` - Submit diagnostic query
- `GET /audit/{trace_id}` - Retrieve audit record
- `GET /audit/{trace_id}/detail` - Full audit trail
- `POST /audit/{trace_id}/approve` - Approve recommendation

### Request Format
```json
{
  "query": "Why did our Global Equity Fund slow down?",
  "fund_id": "GEF001",
  "period": "2026-Q1",
  "user_id": "advisor_name",
  "mode": "standard"
}
```

### Response Format
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
  "root_cause": { ... },
  "peer_comparison": { ... },
  "recommendations": [ ... ],
  "conflicts_detected": false,
  "conflicts_summary": [ ... ],
  "disclaimer": "..."
}
```

## Components Details

### Chat Interface
- Displays conversation history
- Suggested prompts for quick analysis
- Query input with clear functionality
- Export options for conversation and analysis

### Diagnostic Response
- 4-tab layout for different analysis dimensions
- Overview: Key metrics and root causes
- Performance: Returns, sectors, channels
- Peers: Rankings and comparisons
- Recommendations: Actions with approval workflow

### Transparency Layer
- Agent execution pills showing latency and confidence
- Audit trail with four detailed tabs
- Confidence factor breakdown with visualization
- Conflict resolution documentation
- Data source hierarchy

### Orchestration Animation
- Visual representation of parallel execution
- Agent status indicators (Running, Waiting, Completed)
- Progress bars for each agent
- Execution summary with timing

## Customization

### Styling
Edit `styles/theme.py` to customize:
- Color palette
- Font sizes and weights
- Button and card styles
- Component layouts

### Configuration
Edit `config.py` to change:
- API endpoints
- Default fund/period
- Suggested prompts
- Follow-up suggestions
- Confidence thresholds

### Components
Each component in `components/` can be independently modified:
- `chat_interface.py` - Chat UI behavior
- `diagnostic_response.py` - Tab layouts and content
- `transparency_layer.py` - Audit trail display
- `orchestration_animation.py` - Animation speed and visuals

## Troubleshooting

### API Connection Error
- Ensure backend is running on `http://localhost:8000`
- Check `API_BASE_URL` in `.env`
- Use "Health Check" button to verify connectivity

### Missing Audit Data
- Confirm response includes `show_your_work` for detailed mode
- Check that trace ID is properly captured
- Verify API endpoint `/audit/{trace_id}` is accessible

### Animation Not Showing
- Check browser console for JavaScript errors
- Ensure Streamlit version ≥ 1.35.0
- Verify HTML rendering is enabled

## Performance Notes

- API calls timeout after 60 seconds (configurable)
- Conversation history stored in session state
- Cache enabled for API responses
- Animation runs smoothly with 0.02s frame delay

## Future Enhancements

- [ ] Real-time WebSocket updates for agent execution
- [ ] Advanced filtering on peer comparison
- [ ] Custom report generation and export
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Mobile-responsive design
- [ ] Scenario analysis and what-if modeling
- [ ] Integration with external data sources
