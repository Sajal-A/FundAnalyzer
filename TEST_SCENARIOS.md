"""
TEST_SCENARIOS.md
─────────────────
5 Comprehensive Test Scenarios for Fund Performance Diagnostic AI

Each scenario includes:
- Query/Question
- Expected Output
- Visual Breakdown
- Validation Checklist
"""

---

# 🧪 Test Scenario #1: Performance Decline Analysis

## 📝 User Query
```
"Why did our Global Equity Fund slow down this quarter?"
```

## 📊 Expected Output

### 1. Orchestration Animation
```
┌─────────────────────────────────────────────────────────┐
│ 🎬 Agent Orchestration                                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Performance Agent    ████████████░░░░ 75%  ✅          │
│  Flow Agent          ██████████████░░ 85%   ✅          │
│  Market Agent        ████████████████ 95%   ⏳          │
│  Competitor Agent    ██████████░░░░░░ 60%   ⏳          │
│                                                          │
│  Recommendation     ░░░░░░░░░░░░░░░░ 0%    ⏸️ Waiting  │
│                                                          │
│  ✓ All agents completed execution!                      │
│  Total Time: ~2.3s | Parallel: 4 agents | Sequential: 1 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2. Overview Tab

**Key Metrics:**
- Overall Confidence: HIGH (0.87)
- Latency: 2,347 ms
- Fund ID: GEF001
- Period: 2026-Q1

**Root Cause Analysis:**
```
┌─────────────────────────────────────────────────────┐
│ 🎯 Root Cause: Tech Sector Rotation                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Primary Issue:                                       │
│ "Technology sector underperformance due to rising   │
│  interest rate expectations and valuation repricing"│
│                                                      │
│ Impact: -185 basis points                           │
│ Severity: 🔴 HIGH                                   │
│                                                      │
│ Contributing Factors:                               │
│ • Fed rate hike speculation (+50bps)                │
│ • Tech earnings guidance misses                      │
│ • AI bubble concerns resurface                       │
│ • Portfolio concentration in mega-cap tech          │
│                                                      │
│ Macro Headwinds:                                     │
│ • Inverted yield curve persisting                    │
│ • CPI readings sticky at 3.8%                       │
│ • China growth concerns mounting                     │
│                                                      │
│ Risk Events:                                         │
│ • Fed policy pivot signal on May 1st                │
│ • Tech earnings disappointment (NVDA, MSFT)         │
│ • VIX spike to 18.5 mid-quarter                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 3. Performance Tab

**Monthly Returns Table:**
```
┌──────────────────────────────────────┐
│ Month      │ Fund %  │ Benchmark %   │
├──────────────────────────────────────┤
│ 2026-01    │  2.1%   │   1.8%        │
│ 2026-02    │ -0.8%   │   0.2%        │
│ 2026-03    │  0.5%   │   0.9%        │
├──────────────────────────────────────┤
│ Q1 Total   │  1.8%   │   2.9%        │
│ Diff       │ -1.1%   │  (Lagging)    │
└──────────────────────────────────────┘
```

**Sector Attribution Chart:**
```
Sector Contribution to Q1 Returns:

Tech           [████░░░░░░░] -0.85% ⬇️
Healthcare     [██████░░░░░]  0.35% ➡️
Financials     [████████░░░] -0.12% ⬇️
Energy         [██░░░░░░░░░] -0.28% ⬇️
Consumer       [███████░░░░]  0.20% ➡️
Industrials    [█████░░░░░░]  0.15% ➡️
Materials      [███░░░░░░░░]  0.08% ➡️
Utilities      [██░░░░░░░░░]  0.02% ➡️
```

**Regional Distribution:**
```
Region              Allocation
North America        55%  (Higher tech exposure)
Europe               30%  (More diversified)
Asia Pacific         15%  (Emerging exposure)
```

### 4. Peers Tab

**Category Ranking:**
```
┌────────────────────────────────────────────────────────┐
│ Rank │ Fund Name          │ YTD Return │ Percentile  │
├────────────────────────────────────────────────────────┤
│  1   │ StellarGrowth      │   4.2%     │   95th      │
│  2   │ EliteEquity        │   3.8%     │   88th      │
│  3   │ PrecisionFund      │   2.5%     │   72nd      │
│  4   │ ⭐ GEF001           │   1.8%     │   25th      │
│  5   │ StandardIndex      │   1.2%     │   18th      │
│  6   │ ValueMaster        │   0.8%     │   10th      │
└────────────────────────────────────────────────────────┘

GEF001 Category Ranking: 25th percentile
Performance Gap: Underperforming by 2.4% vs category average
```

### 5. Recommendations Tab

**Action 1: Reduce Tech Exposure**
```
┌──────────────────────────────────────────────────────┐
│ 💡 Action 1: Reduce Technology Sector Exposure      │
├──────────────────────────────────────────────────────┤
│ Status: 🟢 GREEN (Approved)                         │
│                                                      │
│ Description:                                         │
│ Shift 8-10% from mega-cap tech to financial sector  │
│ benefiting from higher rates                        │
│                                                      │
│ Expected Impact: +75 to +120 basis points           │
│                                                      │
│ Rationale:                                           │
│ "Current portfolio has 28% in Technology, vs 22%    │
│  category average. Given rising rate environment    │
│  and valuation concerns, reducing concentration     │
│  aligns with peer performance patterns. Financial   │
│  sector benefits from rate increases (net borrowers)│
│  making it attractive tactical swap."               │
│                                                      │
│ Supporting Agents:                                   │
│ • Performance Agent (historical tech underperformance)│
│ • Market Intelligence (rate forecast analysis)      │
│ • Competitor Intelligence (peer positioning)        │
│                                                      │
│ Sources:                                             │
│ • Market Intelligence: Fed Fund Futures (98% conf)  │
│ • Competitor Analysis: Sector allocations (95% conf)│
│ • Historical Returns: Tech regression analysis      │
└──────────────────────────────────────────────────────┘
```

**Action 2: Increase Duration in Bonds**
```
Status: 🟠 AMBER (Review Recommended)

Description:
Add 5% to high-grade corporate bonds (5-7 year duration)

Expected Impact: +30 to +50 basis points

Rationale: "Bond yields attractive at current levels"
```

**Action 3: Add Emerging Market Exposure**
```
Status: 🔴 RED (Not Recommended)

Expected Impact: Uncertain/Risky

Reason: "China slowdown concerns, EM currency volatility"
```

**Action 4: Rebalance to Equal Weight**
```
Status: 🟢 GREEN (Approved)

Expected Impact: +45 basis points
```

### 6. Transparency Layer

**Confidence Badges:**
```
┌──────────────────────────────────────────┐
│ Overall Confidence: 🟢 HIGH (0.87)      │
│ Checkpoint: 📍 STANDARD                  │
│ Latency: ⏱️  2,347 ms                    │
│ Trace ID: 8f5a2b9c-4d1e...              │
└──────────────────────────────────────────┘
```

**Agent Execution Pills:**
```
Performance Agent    | 847ms | 0.91 confidence
Flow Agent          | 623ms | 0.88 confidence
Market Agent        | 1,204ms | 0.85 confidence
Competitor Agent    | 782ms | 0.82 confidence
Recommendation Agent | 456ms | 0.89 confidence
```

**Audit Trail - Agent Calls Tab:**
```
Agent: PerformanceAnalysisAgent
├─ Tool: get_historical_returns()
│  ├─ Fund: GEF001
│  ├─ Period: 2026-01 to 2026-03
│  └─ Result: Monthly returns [2.1%, -0.8%, 0.5%]
│
├─ Tool: sector_attribution()
│  ├─ Method: Brinson-Fachler
│  └─ Result: Tech -0.85%, Healthcare +0.35%
│
└─ Tool: compute_benchmark_tracking_error()
   ├─ Tracking Error: 1.1%
   └─ Information Ratio: 0.15

Status: COMPLETED | Latency: 847ms | Confidence: 0.91
```

**Audit Trail - Confidence Factors Tab:**
```
Factor                  Weight    Score
Data Completeness       25%       0.95
Model Accuracy          20%       0.82
External Validation     20%       0.88
Recency of Data         20%       0.85
Agent Agreement Level   15%       0.92
─────────────────────────────────
WEIGHTED SCORE:                   0.87 (HIGH)
```

**Audit Trail - Conflicts Tab:**
```
✅ No conflicts detected - all agents agreed!

(If there were conflicts, they'd show:)
Conflict #1: Tech Sector Outlook
├─ Topic: Should tech exposure be reduced?
├─ Agent A (Performance): YES - historically underperforming
├─ Agent B (Market): MAYBE - depends on rate cuts
├─ Resolution: Performance Agent wins (higher confidence)
└─ Final: YES, recommend reduction
```

**Audit Trail - Sources Tab:**
```
Tier 1 - Primary (Highest Priority):
├─ SQLite Database
│  ├─ Historical fund returns
│  ├─ Fund holdings
│  ├─ Monthly performance data
│  └─ Sector allocations

Tier 2 - Secondary:
├─ ChromaDB Vector Store
│  ├─ Peer fund positioning
│  ├─ Historical market analysis
│  └─ Sector trend insights

Tier 3 - Tertiary:
├─ Market Intelligence APIs
│  ├─ Real-time Fed Fund Futures
│  ├─ VIX levels and trends
│  └─ Peer category benchmarks
```

### 7. Follow-up Suggestions

```
[Button] "Why did tech drag on performance?"
[Button] "What about EMEA region exposure?"
[Button] "Which action should we prioritize?"
[Button] "How does this compare to 2026-Q2?"
[Button] "Show detailed confidence breakdown"
```

---

## ✅ Validation Checklist

- [x] Animation shows all 4 Group A agents running in parallel
- [x] Recommendation agent waits (shows 0% progress)
- [x] Overview tab displays root cause with severity
- [x] Performance tab shows monthly returns vs benchmark
- [x] Sector chart shows Tech with highest negative impact
- [x] Peers tab shows GEF001 ranked 25th percentile
- [x] Recommendations tab shows 4 actions with approval status
- [x] Confidence badges display (HIGH = green)
- [x] Audit trail expands properly
- [x] Follow-up buttons are interactive

---

# 🧪 Test Scenario #2: Peer Comparison Analysis

## 📝 User Query
```
"How does our fund compare to competitors in our category?"
```

## 📊 Expected Output

### 1. Orchestration Animation (2.1s total)

### 2. Overview Tab

**Key Metrics:**
- Overall Confidence: HIGH (0.84)
- Latency: 2,103 ms
- Fund ID: GEF001
- Period: 2026-Q1

**Root Cause Summary:**
```
Primary Issue: Underperformance vs Peers (3-year rolling)
├─ YTD Return Gap: -2.4% below category average
├─ 3-Year CAGR Gap: -1.8% below category average
└─ Main Driver: Sector allocation differences
```

### 3. Peers Tab (Main Focus)

**Detailed Peer Rankings:**
```
┌────────────────────────────────────────────────────────────┐
│ Rank │ Fund Name          │ 1Y Return │ 3Y CAGR │ AUM    │
├────────────────────────────────────────────────────────────┤
│  1   │ StellarGrowth      │  8.2%     │  5.4%   │ $8.5B  │
│  2   │ EliteEquity        │  7.8%     │  5.1%   │ $6.2B  │
│  3   │ PrecisionFund      │  6.5%     │  4.2%   │ $4.1B  │
│  4   │ DynamicAllocation  │  5.1%     │  3.8%   │ $3.9B  │
│  5   │ ⭐ GEF001           │  4.8%     │  3.2%   │ $3.2B  │ ← US
│  6   │ CoreIndexed        │  4.2%     │  2.9%   │ $2.8B  │
│  7   │ ValueMaster        │  3.1%     │  2.1%   │ $2.1B  │
└────────────────────────────────────────────────────────────┘

Category Average (1Y): 5.2% | 3Y CAGR: 3.5%
GEF001 Performance Gap: -0.4% YTD | -0.3% 3Y CAGR

Percentile Ranking: 37th (Below median)
Status: ⚠️ Underperforming
```

**Strategy Gap Analysis:**
```
┌─────────────────────────────────────────────────────────┐
│ Sector Allocation Comparison                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Sector     │ GEF001 │ Category Avg │ Top Performer   │
├─────────────────────────────────────────────────────────┤
│ Tech       │  28%   │   22%        │   18%           │
│ Healthcare │  14%   │   15%        │   22%           │
│ Financials │  16%   │   18%        │   15%           │
│ Industrials│  12%   │   14%        │   16%           │
│ Energy     │   8%   │   10%        │   12%           │
│ Consumer   │  15%   │   13%        │   11%           │
│ Materials  │   4%   │    5%        │    3%           │
│ Utilities  │   3%   │    3%        │    3%           │
│                                                         │
│ Key Difference:                                        │
│ GEF001 is OVERWEIGHT in Tech (+6%) and Consumer (+2%)│
│ but UNDERWEIGHT in Healthcare (-8%) and Industrials  │
│                                                         │
│ Impact: Tech sector drag was amplified in Q1          │
└─────────────────────────────────────────────────────────┘
```

**Peer Strategy Comparison:**
```
Why Top Performers Outperformed:
├─ StellarGrowth (1st)
│  └─ Higher Healthcare exposure (22% vs our 14%)
│     Healthcare returned +2.1% in Q1
│
├─ EliteEquity (2nd)
│  └─ Lower Tech exposure (18% vs our 28%)
│     Avoided -0.85% tech drag
│
└─ PrecisionFund (3rd)
   └─ Balanced positioning + tactical rebalancing
      Adjusted allocations monthly vs quarterly
```

### 4. Recommendations Tab

**Action 1: Align Sector Allocations**
```
Status: 🟢 GREEN (Approved)

Description:
Rebalance to category-average allocations over 6 weeks
- Reduce Tech from 28% to 22% (-6%)
- Increase Healthcare from 14% to 22% (+8%)
- Adjust Industrials from 12% to 14% (+2%)

Expected Impact: +65 to +95 basis points

Rationale:
"Category average allocation has produced consistent
outperformance. Our overweight in underperforming
Tech and underweight in Healthcare are key drags."
```

**Action 2: Improve Portfolio Rebalancing Frequency**
```
Status: 🟠 AMBER (Review Recommended)

Description:
Change rebalancing from quarterly to monthly

Expected Impact: +20 to +40 basis points

Note: Requires operational changes
```

### 5. Audit Trail - Agent Calls

```
CompetitorIntelligenceAgent: COMPLETED
├─ Tool: fetch_peer_fund_data()
│  ├─ Category: Large Cap Equity
│  ├─ Funds: 47 competitors analyzed
│  ├─ Data: Holdings, returns, AUM, managers
│  └─ Latency: 234ms
│
├─ Tool: sector_positioning_analysis()
│  ├─ Comparison: GEF001 vs category average
│  ├─ Result: Tech overweight (+6%), Healthcare underweight (-8%)
│  └─ Confidence: 0.94
│
└─ Tool: performance_factor_analysis()
   ├─ Method: Brinson-Fachler
   ├─ Allocation Effect: -0.82%
   └─ Latency: 189ms

Status: COMPLETED | Latency: 782ms | Confidence: 0.88
```

---

## ✅ Validation Checklist

- [x] Peer rankings show clear ordering by performance
- [x] GEF001 highlighted in correct position (5th)
- [x] Sector allocation comparison visible
- [x] Strategy gap explanation clear
- [x] Top performer reasons explained
- [x] Recommendations address specific gaps
- [x] Confidence high (0.88+)
- [x] Follow-ups suggest related analysis

---

# 🧪 Test Scenario #3: Risk Analysis

## 📝 User Query
```
"What are the main risk factors affecting this fund?"
```

## 📊 Expected Output

### Overview Tab

**Risk Event Identification:**
```
Current Risk Events:
┌──────────────────────────────────────────┐
│ 🔴 HIGH Priority                        │
├──────────────────────────────────────────┤
│ • Fed policy shift (Probability: 85%)    │
│ • Tech sector correction (Probability: 90%) │
│ • Valuation repricing (Probability: 75%) │
│                                          │
│ 🟠 MEDIUM Priority                      │
├──────────────────────────────────────────┤
│ • China economic slowdown (Prob: 55%)    │
│ • China policy risk (Prob: 60%)          │
│ • Geopolitical tension (Prob: 40%)       │
└──────────────────────────────────────────┘
```

**Macro Headwinds:**
```
Current Macro Conditions:
├─ Inverted Yield Curve: YES (-35bps)
│  Impact on Fund: Negative for growth stocks
│
├─ Inflation Levels: CPI 3.8% (Sticky)
│  Impact: Rate pressure continues
│
├─ Growth Outlook: Moderating
│  Impact: Valuations under pressure
│
├─ Credit Spreads: Widening (+15bps)
│  Impact: Risk-off environment
│
└─ Earnings Revisions: Negative (-8% down)
   Impact: Tech earnings especially weak
```

**Fund-Specific Risk Factors:**
```
┌──────────────────────────────────────────────┐
│ Risk Factor            │ Level    │ Trend    │
├──────────────────────────────────────────────┤
│ Concentration Risk     │ HIGH     │ ⬆️ Rising  │
│ (Tech at 28%)          │          │          │
│                                   │          │
│ Duration Risk          │ MEDIUM   │ ➡️ Stable  │
│ (Interest rate exposure)          │          │
│                                   │          │
│ Liquidity Risk         │ LOW      │ ⬇️ Falling │
│ (Largest holdings very liquid)    │          │
│                                   │          │
│ FX Risk                │ MEDIUM   │ ⬆️ Rising  │
│ (15% in non-USD assets)           │          │
│                                   │          │
│ Geopolitical Risk      │ MEDIUM   │ ⬆️ Rising  │
│ (Emerging market exposure)        │          │
└──────────────────────────────────────────────┘
```

**Recommendations Tab:**

```
Action 1: Implement Concentration Risk Hedging
Status: 🟢 GREEN

Description:
Add sector-specific put options on Tech holdings
Cost: 0.5% annually
Expected Protection: -75% downside in crash scenario

Action 2: Diversify Away from Tech Concentration
Status: 🟢 GREEN

Description:
Reduce Tech to 22% (category average)
Add to Healthcare and Industrials
Impact: -0.6% current performance, +1.2% risk-adjusted returns
```

---

## ✅ Validation Checklist

- [x] Risk events clearly categorized by priority
- [x] Macro headwinds displayed with current values
- [x] Fund-specific risks identified
- [x] Risk levels color-coded (High/Medium/Low)
- [x] Trends shown (Rising/Stable/Falling)
- [x] Recommendations address top risks
- [x] Hedge strategies explained
- [x] Confidence badge present

---

# 🧪 Test Scenario #4: Sector Breakdown Analysis

## 📝 User Query
```
"Give me a detailed sector-by-sector breakdown for this quarter"
```

## 📊 Expected Output

### Overview Tab

**Sector Summary:**
```
Sector Performance Contribution:
┌──────────────────────────────────────────────────────┐
│ Sector        │ Return │ Weight │ Contribution      │
├──────────────────────────────────────────────────────┤
│ Tech          │ -3.1%  │ 28%    │ -0.87% (Primary) │
│ Healthcare    │ +2.1%  │ 14%    │ +0.29%           │
│ Financials    │ -0.8%  │ 16%    │ -0.13%           │
│ Industrials   │ +0.5%  │ 12%    │ +0.06%           │
│ Energy        │ -3.5%  │  8%    │ -0.28%           │
│ Consumer      │ +1.2%  │ 15%    │ +0.18%           │
│ Materials     │ -1.8%  │  4%    │ -0.07%           │
│ Utilities     │ +0.3%  │  3%    │ +0.01%           │
├──────────────────────────────────────────────────────┤
│ TOTAL         │        │100%    │ -0.81% DRAG      │
└──────────────────────────────────────────────────────┘
```

### Performance Tab

**Sector Attribution Chart:**
```
Contribution to Returns by Sector:

Tech           ▁▁▁▁▁▁▁▁▁▁▁▁▁▁ -0.87% (🔴 Biggest Drag)
Energy         ▁▁▁▁▁▁▁▁ -0.28%
Financials     ▁▁ -0.13%
Materials      ▁ -0.07%
────────────────────────── NEUTRAL ──────────────────
Utilities      ▃ +0.01%
Industrials    ▃▃▃ +0.06%
Consumer       ▃▃▃▃▃▃ +0.18%
Healthcare     ▃▃▃▃▃▃▃▃▃ +0.29% (🟢 Best Performer)
```

**Detailed Sector Analysis:**

```
📱 TECHNOLOGY SECTOR (-0.87% contribution)
├─ Allocation: 28% (vs 22% category avg)
├─ Q1 Return: -3.1% (vs +0.8% category avg)
├─ Key Holdings:
│  • NVDA (5.2% of fund) ↓ -8.2% - Earnings miss
│  • MSFT (4.8% of fund) ↓ -4.1% - Valuation repricing
│  • AAPL (3.9% of fund) ↓ -6.5% - Rate sensitivity
│  • TSLA (2.1% of fund) ↓ -12.4% - Growth concerns
│
└─ Analysis:
   Concentration in mega-cap tech and overweight
   positioning created significant drag. The sector
   faced headwinds from rate expectations and
   valuation concerns post-earnings season.

🏥 HEALTHCARE SECTOR (+0.29% contribution)
├─ Allocation: 14% (vs 15% category avg)
├─ Q1 Return: +2.1% (vs +1.8% category avg)
├─ Key Holdings:
│  • JNJ (3.1% of fund) ↑ +3.2% - Stable dividends
│  • UNH (2.8% of fund) ↑ +4.1% - Strong earnings
│  • ABBV (2.2% of fund) ↑ +1.8% - Pharma stable
│
└─ Analysis:
   Defensive characteristics and M&A activity
   supported healthcare gains. Underweight
   positioning meant we didn't capture full upside.

💰 FINANCIALS SECTOR (-0.13% contribution)
├─ Allocation: 16% (vs 18% category avg)
├─ Q1 Return: -0.8% (vs +1.2% category avg)
├─ Mixed performance on rate expectations
├─ Key Factors:
│  • Net Interest Margins: Pressured near-term
│  • Rate: Cut expectations later pushed down banks
│  • Valuation: Attractive but cycle uncertain
└─ Recommendation: Monitor for rotation opportunity
```

**Monthly Performance by Sector:**
```
Month  │ Tech  │ Healthcare │ Financials │ Energy │ Consumer
───────┼───────┼────────────┼────────────┼────────┼─────────
Jan    │ -0.9% │   +1.2%    │   -0.2%    │ -1.1%  │  +0.8%
Feb    │ -1.8% │   +0.5%    │   +0.1%    │ -1.2%  │  +0.3%
Mar    │ -0.4% │   +0.4%    │   -0.7%    │ -1.2%  │  +0.1%
───────┴───────┴────────────┴────────────┴────────┴─────────
Q1 Avg │ -1.0% │   +0.7%    │   -0.3%    │ -1.2%  │  +0.4%
```

### Recommendations Tab

```
Action 1: Reduce Tech Overweight
Status: 🟢 GREEN
Impact: +85 bps
Method: Trim NVDA and TSLA positions

Action 2: Increase Healthcare Exposure
Status: 🟢 GREEN
Impact: +35 bps
Method: Add UNH, ABBV on dips

Action 3: Sector Rotation Strategy
Status: 🟠 AMBER
Impact: +40 bps
Method: Shift from Defensive to Cyclical (if rates stabilize)
```

---

## ✅ Validation Checklist

- [x] All 8 sectors displayed with returns
- [x] Contribution calculations accurate
- [x] Bar chart shows positive/negative clearly
- [x] Detailed analysis for top 3 sectors
- [x] Individual holding breakdown shown
- [x] Monthly trends visible
- [x] Recommendations aligned with findings

---

# 🧪 Test Scenario #5: Flow Analysis

## 📝 User Query
```
"Analyze fund flows and their impact on performance this quarter"
```

## 📊 Expected Output

### Overview Tab

**Flow Summary:**
```
Fund Flow Analysis - Q1 2026
┌─────────────────────────────────────────┐
│ Opening AUM (Dec 2025):    $3.40B       │
│ Inflows:                   $180M (+5.3%)│
│ Outflows:                  $120M (-3.5%)│
│ Net Flow:                  +$60M (+1.8%)│
├─────────────────────────────────────────┤
│ Closing AUM (Mar 2026):    $3.46B       │
│ Performance Gain:          -$28M (-0.8%)│
│ Market Impact:             +$54M (+1.6%)│
└─────────────────────────────────────────┘

Flow Trend: ⬆️ Positive (but decelerating)
3-Month Avg: +$35M/month
```

### Performance Tab

**Flow Impact Analysis:**
```
┌──────────────────────────────────────────────────────┐
│ Flow Impact Breakdown                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Total Fund Return:           -0.81%                 │
│                                                      │
│ Impact from Inflows:         -0.12%                 │
│ (Cash drag from deploying inflows)                  │
│                                                      │
│ Impact from Outflows:        +0.08%                 │
│ (Positive from reducing cash drag)                  │
│                                                      │
│ Net Flow Impact:             -0.04%                 │
│                                                      │
│ Performance (excluding flow): -0.77%                │
│                                                      │
│ ➜ Flows had minimal but negative impact            │
│   due to deployment timing into weak market         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Flow Sources Analysis:**
```
Inflows by Channel:
┌────────────────────────────────────┐
│ Channel        │ Amount    │ %    │
├────────────────────────────────────┤
│ Direct         │  $92M     │ 51%  │
│ Mutual Fund    │  $65M     │ 36%  │
│ ETF            │  $23M     │ 13%  │
└────────────────────────────────────┘

Outflow Sources:
┌────────────────────────────────────┐
│ Reason         │ Amount    │ %    │
├────────────────────────────────────┤
│ Rebalancing    │  $72M     │ 60%  │
│ Performance    │  $35M     │ 29%  │
│ Redemptions    │  $13M     │ 11%  │
└────────────────────────────────────┘
```

**Regional/Channel Distribution:**
```
Flow Distribution by Region:
┌──────────────────────────────────┐
│ North America  │ +$120M (67%)   │
│ Europe         │  -$35M (-19%)  │
│ Asia Pacific   │  -$25M (-14%)  │
└──────────────────────────────────┘

Trend: Geographic concentration risk
```

### Peers Tab

**Flow Comparison:**
```
Flow Percentile vs Category:
┌──────────────────────────────────────────┐
│ Fund              │ Q1 Flows  │ Rank    │
├──────────────────────────────────────────┤
│ StellarGrowth     │ +$450M    │  1st    │
│ EliteEquity       │ +$280M    │  2nd    │
│ GEF001            │  +$60M    │ 22nd    │ ← US
│ CoreIndexed       │  -$80M    │ 38th    │
│ ValueMaster       │ -$150M    │ 45th    │
└──────────────────────────────────────────┘

Category Average: +$75M
GEF001 vs Average: -$15M (-20%)

Implication: Below-average flows + below-average
performance = outflow risk in Q2
```

### Recommendations Tab

```
Action 1: Marketing Initiative for Q2
Status: 🟠 AMBER

Description:
Increase marketing spend by 30% to attract institutional
clients given competitive flow environment

Cost: $200K
Expected Impact: +$300M flows over next 4 quarters

Rationale: "Positive flows are critical to offset
performance drag and reduce cash drag effect."

Action 2: Optimize Deployment Process
Status: 🟢 GREEN

Description:
Implement systematic inflow deployment strategy to
reduce cash drag during market downturns

Impact: +10-15 basis points annually
Implementation: 2 weeks

Action 3: Enhance Investor Communication
Status: 🟢 GREEN

Description:
Monthly update to investors on fund strategy and
outperformance drivers

Expected Impact: Reduce redemptions by 20%
```

---

## ✅ Validation Checklist

- [x] Opening/Closing AUM clearly displayed
- [x] Net flows calculated accurately
- [x] Flow impact on performance isolated
- [x] Sources of flows identified
- [x] Channel breakdown shown
- [x] Peer flow comparison provided
- [x] Risk assessment (outflow risk) included
- [x] Recommendations address flow trends

---

# 📋 Summary Comparison Table

| Scenario | Query | Main Focus | Key Insight |
|----------|-------|-----------|-------------|
| 1 | Performance Decline | What went wrong? | Tech overweight created drag |
| 2 | Peer Comparison | How do we rank? | Allocation gap vs competitors |
| 3 | Risk Analysis | What are the risks? | Tech concentration is main risk |
| 4 | Sector Breakdown | Detailed sector view | Understand each sector's impact |
| 5 | Flow Analysis | Fund flow impact | Below-average flows + weak performance = outflow risk |

---

# 🎯 Expected System Behavior for All Scenarios

## ✅ Consistent Elements

1. **Orchestration Animation**: Always shows
   - 4 parallel Group A agents (1-2 seconds)
   - Sequential Recommendation agent (0.5 seconds)
   - Total latency: 2.0-2.5 seconds

2. **Response Structure**: Always includes
   - 4 diagnostic tabs
   - Transparency layer with audit trail
   - Follow-up suggestions
   - Confidence badges

3. **Confidence Scoring**: 
   - HIGH (0.80+): Green
   - MEDIUM (0.60-0.79): Amber
   - LOW (<0.60): Red

4. **Recommendations**:
   - GREEN (Approved): Safe action
   - AMBER (Review): Conditional or uncertain
   - RED (Not Recommended): Avoid

---

# 🧪 How to Test These Scenarios

1. **Open the UI**: http://localhost:8501
2. **Type one of the queries** (or click suggested prompts)
3. **Watch the orchestration animation**
4. **Review each tab** in the diagnostic response
5. **Check the audit trail** for transparency
6. **Try follow-up questions**
7. **Verify approval buttons work**

**Expected Total Flow**: ~5-10 seconds from query to complete response

---

# ✨ Success Criteria

For each scenario, verify:
- ✅ Response received within 5 seconds
- ✅ Orchestration animation smooth and complete
- ✅ All 4 tabs populate with relevant data
- ✅ Confidence score displays correctly
- ✅ Recommendations have approval status
- ✅ Audit trail expands and shows details
- ✅ Follow-up buttons are interactive
- ✅ Data is consistent across tabs
