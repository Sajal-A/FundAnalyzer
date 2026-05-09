# Quick Start Guide - Fund Performance Diagnostic AI

## 🚀 Quick Start

### Option 1: Windows (All-in-One)
Simply run:
```batch
start.bat
```

This opens two command windows:
- One for the Backend API (http://localhost:8000)
- One for the Frontend UI (http://localhost:8501)

### Option 2: Windows (Individual)
**Start Backend:**
```batch
start_backend.bat
```

**Start Frontend (in another terminal):**
```batch
start_frontend.bat
```

### Option 3: Manual (Any OS)

**Terminal 1 - Backend:**
```bash
cd FUND_ANALYSIS_AGENT
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd FUND_ANALYSIS_AGENT/frontend
pip install -r requirements.txt
python run.py
```

### Option 4: Linux/Mac (using start.sh)
```bash
chmod +x start.sh
bash start.sh
```

## 📊 Access the Application

| Component | URL |
|-----------|-----|
| Frontend UI | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Redoc | http://localhost:8000/redoc |

## 🎯 First Query

After both services are running:

1. Open http://localhost:8501 in your browser
2. Click one of the suggested prompts or enter your own query
3. Watch the agent orchestration animation
4. Review the diagnostic response with multiple tabs
5. Check the audit trail for transparency

## 📁 Project Structure

```
FUND_ANALYSIS_AGENT/
├── main.py                    # Backend entry point
├── start.bat                  # Windows all-in-one startup
├── start_backend.bat          # Windows backend only
├── start_frontend.bat         # Windows frontend only
├── start.sh                   # Linux/Mac startup script
├── requirements.txt           # Backend dependencies
│
├── frontend/                  # Streamlit UI
│   ├── app.py                # Main Streamlit application
│   ├── run.py                # UI startup script
│   ├── requirements.txt       # Frontend dependencies
│   ├── config.py             # UI configuration
│   ├── INTEGRATION_GUIDE.md   # Integration documentation
│   ├── README.md             # Frontend README
│   ├── .env.example          # Environment variables template
│   │
│   ├── components/           # Streamlit components
│   │   ├── chat_interface.py
│   │   ├── diagnostic_response.py
│   │   ├── transparency_layer.py
│   │   ├── orchestration_animation.py
│   │   └── __init__.py
│   │
│   ├── utils/                # Utility modules
│   │   ├── api_client.py
│   │   ├── state_manager.py
│   │   └── __init__.py
│   │
│   ├── styles/               # UI styling
│   │   ├── theme.py
│   │   └── __init__.py
│   │
│   └── .streamlit/           # Streamlit configuration
│       └── config.toml
│
├── agents/                   # Backend agents
│   ├── orchestrator.py
│   ├── performance_agent.py
│   ├── flow_agent.py
│   ├── market_agent.py
│   ├── competitor_agent.py
│   └── recommendation_agent.py
│
├── api/                      # FastAPI backend
│   ├── main.py
│   └── models.py
│
├── core/                     # Core functionality
│   ├── config.py
│   ├── database.py
│   ├── vector_store.py
│   ├── audit.py
│   ├── confidence.py
│   ├── output_formatter.py
│   ├── exceptions.py
│   └── __init__.py
│
├── data/                     # Data layer
│   ├── mock/
│   ├── schema/
│   └── README.md
│
├── tests/                    # Test suite
├── logs/                     # Application logs
└── README.md                 # Main README
```

## ✨ Frontend Features

### 💬 Chat Interface
- Natural language queries
- Suggested prompts
- Full conversation history
- Export functionality

### 🎬 Agent Orchestration
- Real-time animation of parallel execution
- Group A agents: Performance, Flow, Market, Competitor
- Group B agent: Recommendation (sequential)
- Progress bars and status indicators

### 📈 Diagnostic Response (4 Tabs)
1. **Overview**: Key metrics, root cause, headwinds, risk events
2. **Performance**: Returns, sectors, regions, channels
3. **Peers**: Rankings, gap analysis
4. **Recommendations**: Actions with approval workflow

### 🔍 Transparency Layer
- Confidence scores and badges
- Agent execution pills with latency
- Expandable audit trail with 4 tabs:
  - Agent Calls
  - Confidence Factors
  - Conflicts & Resolution
  - Data Sources

### 💡 Follow-up Questions
- Quick-reply suggestion buttons
- Free-text input
- Context-aware responses
- Per-query confidence scores

## 🔧 Configuration

### Backend Configuration
Edit the root `.env` file:
```env
DATABASE_URL=sqlite:///data/fund_analysis.db
VECTOR_STORE_PATH=./vector_store
LOG_LEVEL=INFO
OPENAI_API_KEY=your_key_here
```

### Frontend Configuration
Edit `frontend/.env`:
```env
API_BASE_URL=http://localhost:8000
API_TIMEOUT=60
LOG_LEVEL=INFO
```

## 🐛 Troubleshooting

**Q: "Failed to connect to API"**
- Ensure backend is running on http://localhost:8000
- Check firewall settings
- Verify API_BASE_URL in frontend/.env

**Q: "Module not found errors"**
- Install dependencies: `pip install -r requirements.txt`
- For frontend: `pip install -r frontend/requirements.txt`
- Activate the correct virtual environment

**Q: "Database errors"**
- Seed mock data: `python main.py --seed`
- Check database path in core/config.py

**Q: "Streamlit not found"**
- Install frontend dependencies: `pip install streamlit`
- Use correct Python interpreter/environment

## 📚 Documentation

- [Main README](README.md) - Project overview
- [Frontend README](frontend/README.md) - UI documentation
- [Integration Guide](frontend/INTEGRATION_GUIDE.md) - Backend-frontend integration
- [API Docs](http://localhost:8000/docs) - FastAPI interactive docs

## 🎓 Example Queries

Try these queries to test the system:

1. **Performance Analysis**
   - "Why did our Global Equity Fund slow down this quarter?"
   - "What were the main drivers of outperformance?"

2. **Peer Comparison**
   - "How do we compare to peer funds?"
   - "Which category are we underperforming in?"

3. **Sector Analysis**
   - "Give me a sector-by-sector breakdown"
   - "Which sectors drove returns?"

4. **Risk Analysis**
   - "What are the main risk factors?"
   - "Identify macro headwinds affecting the fund"

5. **Recommendations**
   - "What actions should we take?"
   - "Which recommendation should we prioritize?"

## 📞 Support

For issues or questions:
1. Check the [Integration Guide](frontend/INTEGRATION_GUIDE.md)
2. Review backend logs: `logs/app.log`
3. Check Streamlit output in terminal
4. Test API endpoints: http://localhost:8000/docs

## 🚀 Next Steps

After getting the system running:

1. **Customize Branding**: Edit colors in `frontend/styles/theme.py`
2. **Add More Prompts**: Update `frontend/config.py`
3. **Connect Real Data**: Replace mock data in `data/mock/`
4. **Deploy**: Consider Docker/Kubernetes for production
5. **Monitor**: Set up logging and analytics

---

**Happy analyzing! 📊✨**
