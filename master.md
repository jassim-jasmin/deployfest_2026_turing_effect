# PropGrowth AI — Hackathon Master Prompt
### Team of 4 | 5-Hour Sprint | Stack: FastAPI + LangGraph + ChromaDB + Gemini + Phoenix + React/Vite

---

> **HOW TO USE THIS DOCUMENT**
> Split your team as shown in the **Team Split** section. Each person pastes their own section into a fresh Claude/Gemini chat and says: *"Build this exactly as described. Output complete, working code — no placeholders, no TODOs."* Person 4 handles integration after others finish.

---

## ⚡ TEAM SPLIT & TIME BUDGET

| Person | Role | Time |
|--------|------|------|
| **P1** | Backend Core (FastAPI + tools.py + rag.py + data) | 2.5 hrs |
| **P2** | Agent Brain (agent.py with LangGraph + HITL) | 2.5 hrs |
| **P3** | Frontend (React + Vite + all components) | 2.5 hrs |
| **P4** | Telemetry + Integration + Demo polish | 2.5 hrs |

P4 starts integrating after ~90 minutes when P1 and P2 have working skeletons.

---

---

# PERSON 1 PROMPT — Backend Core

Paste this entire block into Claude:

---

```
Build the backend core of "PropGrowth AI" — an AI property investment analyzer.

## Project Structure to Create
```
propgrowth/backend/
├── main.py
├── tools.py
├── rag.py
├── data/
│   └── master_plans.txt
└── requirements.txt
```

## requirements.txt
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
python-dotenv==1.0.1
chromadb==0.5.0
sentence-transformers==3.0.0
google-generativeai==0.7.2
langgraph==0.2.0
langchain-google-genai==1.0.7
langchain-core==0.2.10
arize-phoenix[evals]==4.5.0
opentelemetry-sdk==1.24.0
opentelemetry-exporter-otlp==1.24.0
openinference-instrumentation-langchain==0.1.19
pydantic==2.7.4
httpx==0.27.0
sse-starlette==2.1.0
```

## FILE: tools.py

Create a tools.py with these 4 functions. Each is a plain Python function (not LangChain tool — just clean functions called directly by the agent):

### 1. search_properties(location, budget_min, budget_max, bhk_type)
Returns a list of 4 mock comparable properties (Comps) for Indian cities.
Each comp has: id, title, location, price (INR lakhs), bhk, area_sqft, price_per_sqft, monthly_rent, listing_age_days, distance_km, nearby_metro (bool), source.
Include realistic Indian city data. Vary the comps slightly based on location param — if location contains "Pune" return Pune Comps; if "Bangalore" return Bangalore comps; else return generic metros. Each comp must look like real real estate data.

### 2. calculate_roi(price_lakhs, monthly_rent, appreciation_rate_pct)
Returns a dict:
- rental_yield_pct: (monthly_rent * 12) / (price_lakhs * 100000) * 100
- break_even_years: float (price / annual_rent, rounded to 1 decimal)
- projected_10yr_value_lakhs: price_lakhs * (1 + appreciation_rate_pct/100)^10
- total_10yr_return_pct: percentage gain over 10 years
- monthly_cashflow: monthly_rent minus assumed EMI (assume 70% loan at 8.5% for 20 years)

### 3. get_locality_insights(locality, city)
Returns a dict with:
- infrastructure_score: int 1-100 (seed with city+locality hash for consistency)
- demand_index: int 1-100
- population_growth_pct: float (3yr CAGR)
- avg_price_trend_pct: float (YoY)
- top_employers_nearby: list of 3 company names
- connectivity_rating: str ("Excellent"/"Good"/"Average"/"Poor")
- flood_risk: str ("Low"/"Medium"/"High")
- social_infrastructure: dict {schools: int, hospitals: int, malls: int}

Use a deterministic seeding approach (hash of locality+city mod ranges) so same input always returns same output. Include some hardcoded realistic overrides for "Hinjewadi, Pune", "Whitefield, Bangalore", "Bandra, Mumbai", "Sector 62, Noida".

### 4. rag_search(query: str) -> str
Import and call query_rag_context from rag.py. Return the string result.

## FILE: rag.py

Create a ChromaDB-backed RAG module:

```python
# rag.py — ChromaDB vector store for zoning & infrastructure grounding
```

- Use `chromadb.PersistentClient(path="./chroma_db")`
- Collection name: `"zoning_infrastructure"`
- Embeddings: Use `chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")`
- On startup, check if collection has documents. If empty, seed from `data/master_plans.txt`
- Parse master_plans.txt by splitting on double newlines (each paragraph = one document)
- Add documents with metadata: {source: "master_plans", chunk_id: int}

Function `query_rag_context(query: str, n_results: int = 3) -> str`:
- Query the collection
- Return a formatted string: "GROUNDING CONTEXT:\n" + joined results with "---" separators
- If no results, return "No specific zoning or infrastructure data found for this query."

Function `initialize_rag()`:
- Called at FastAPI startup
- Loads and seeds data if needed
- Prints confirmation

## FILE: data/master_plans.txt

Write a comprehensive seed file with 20+ paragraphs covering these Indian cities — Pune, Bangalore, Mumbai, Hyderabad, Noida, Chennai. Each paragraph should be a self-contained fact about one of:
- Metro line expansions (with timelines like 2025-2028)
- New IT parks or SEZ approvals
- Zoning rezoning announcements
- Highway or ring road projects
- Smart city initiatives
- Affordable housing zones
- Commercial corridors

Make these sound like real urban planning documents. Include specific locality names, distances, dates, and project names. At least 3-4 entries per city. Examples of format:
"Pune Metro Line 3 (PCMC to Swargate) Phase 2 extension approved for Hinjewadi IT Park connectivity. New stations at Wakad, Baner, and Aundh Depot planned. Expected completion Q4 2027. Properties within 800m of proposed stations have historically appreciated 18-22% post-announcement in similar corridors."

## FILE: main.py

Create FastAPI app:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio, json, uuid
from typing import AsyncGenerator
```

**Endpoints:**

### POST /api/analyze/start
Request body: `{ "address": str, "city": str, "budget_lakhs": float, "bhk_type": str, "investment_horizon_years": int }`

- Import and call `start_analysis(request_data)` from agent.py
- Returns: `{ "thread_id": str, "status": "awaiting_hitl", "preliminary_score": int, "comps": [...], "locality_insights": {...}, "rag_context": str, "roi_estimates": {...} }`

### POST /api/analyze/resume
Request body: `{ "thread_id": str, "approved_comps": [...], "analyst_notes": str }`

- Import and call `resume_analysis(thread_id, approved_comps, analyst_notes)` from agent.py
- Returns: `{ "thread_id": str, "status": "complete", "final_score": int, "report": {...}, "telemetry": {...} }`

### GET /api/analyze/stream/{thread_id}
SSE endpoint. Import `get_stream_events(thread_id)` from agent.py which returns an async generator of step strings.
Stream format: `data: {"step": "...", "message": "...", "timestamp": "..."}\n\n`

### GET /api/telemetry
Returns mock telemetry summary: `{ "total_traces": int, "avg_latency_ms": int, "tool_calls": {...}, "rag_retrievals": int }`

### GET /api/health
Returns `{"status": "ok", "version": "1.0.0"}`

Enable CORS for `http://localhost:5173` and `http://localhost:3000`.
Call `initialize_rag()` in FastAPI startup event.

Output complete, working Python files — no placeholders, no TODOs, no "add your logic here" comments. Every function must be fully implemented.
```

---

---

# PERSON 2 PROMPT — Agent Brain (LangGraph + HITL)

Paste this entire block into Claude:

---

```
Build agent.py for "PropGrowth AI" — the LangGraph state machine that powers the AI investment analyst.

## CRITICAL: This file is agent.py inside propgrowth/backend/

## Dependencies available (already in requirements.txt):
- langgraph==0.2.0
- langchain-google-genai==1.0.7
- langchain-core==0.2.10
- google-generativeai==0.7.2

## Agent State Schema (TypedDict)

```python
class AnalysisState(TypedDict):
    # Inputs
    thread_id: str
    address: str
    city: str
    budget_lakhs: float
    bhk_type: str
    investment_horizon_years: int
    
    # Intermediate data
    comps: List[dict]
    locality_insights: dict
    rag_context: str
    roi_estimates: dict
    
    # HITL
    preliminary_score: int
    hitl_approved: bool
    approved_comps: List[dict]
    analyst_notes: str
    
    # Output
    final_score: int
    report: dict
    
    # Streaming
    current_step: str
    stream_messages: List[str]
```

## LangGraph Graph Structure

Build a StateGraph with these nodes in order:
1. `fetch_market_data` — calls tools.search_properties and tools.get_locality_insights
2. `inject_rag_context` — calls tools.rag_search with a query built from address+city
3. `calculate_preliminary` — calls tools.calculate_roi, computes preliminary_score (int 1-100)
4. `hitl_verification` — this is the INTERRUPT node (agent pauses here)
5. `calculate_final_score` — uses approved_comps to compute weighted final_score
6. `generate_report` — calls Gemini to produce the full investment report

**Graph edges:**
```
fetch_market_data -> inject_rag_context -> calculate_preliminary -> hitl_verification -> calculate_final_score -> generate_report
```

**Interrupt:** Use `interrupt_before=["hitl_verification"]` with `MemorySaver` checkpointer.

## Node Implementations

### Node 1: fetch_market_data
```python
def fetch_market_data(state: AnalysisState) -> AnalysisState:
    # Extract locality from address (use last word before city or whole address)
    # Call tools.search_properties(location=f"{state['address']}, {state['city']}", 
    #                               budget_min=state['budget_lakhs']*0.8,
    #                               budget_max=state['budget_lakhs']*1.2,
    #                               bhk_type=state['bhk_type'])
    # Call tools.get_locality_insights(locality=state['address'], city=state['city'])
    # Update state with comps and locality_insights
    # Append to stream_messages: "🏘️ Fetching comparable properties and market data..."
```

### Node 2: inject_rag_context
```python
def inject_rag_context(state: AnalysisState) -> AnalysisState:
    # Build query: f"infrastructure development zoning {state['city']} {state['address']}"
    # Call tools.rag_search(query)
    # Update rag_context in state
    # Append "📋 Retrieving zoning laws and infrastructure master plans..."
```

### Node 3: calculate_preliminary
```python
def calculate_preliminary(state: AnalysisState) -> AnalysisState:
    # Pick the median-priced comp, call tools.calculate_roi
    # Calculate preliminary_score (int 1-100) using this weighted formula:
    #   - infrastructure_score weight: 30%
    #   - demand_index weight: 25%  
    #   - avg_price_trend_pct normalized (0-20% trend → 0-100 score) weight: 25%
    #   - roi rental_yield_pct normalized (2-6% → 0-100) weight: 20%
    #   - Bonus: +5 if rag_context contains "metro" or "IT park"
    #   - Cap at 100
    # Store preliminary_score, roi_estimates in state
    # Append "⚙️ Calculating preliminary growth score..."
```

### Node 4: hitl_verification
```python
def hitl_verification(state: AnalysisState) -> AnalysisState:
    # This node only runs AFTER the interrupt is resumed with user data
    # At this point state already has approved_comps and analyst_notes from resume call
    # Just append "✅ Analyst review received. Processing approved comparables..."
    # Return state unchanged (data was injected by resume mechanism)
```

### Node 5: calculate_final_score
```python
def calculate_final_score(state: AnalysisState) -> AnalysisState:
    # Use approved_comps (may be subset of original comps)
    # Recalculate ROI using average of approved comp prices
    # Apply same scoring formula as preliminary but:
    #   - If analyst_notes contains positive keywords (good/strong/bullish/approve), add 3 pts
    #   - If analyst_notes contains negative keywords (risk/concern/overpriced), subtract 3 pts
    # Store as final_score
    # Append "📊 Calculating final weighted investment score..."
```

### Node 6: generate_report
```python
def generate_report(state: AnalysisState) -> AnalysisState:
    # Use google.generativeai to call Gemini 2.5 Flash
    # Model: "gemini-2.5-flash" (or "gemini-1.5-flash" as fallback)
    # Build a detailed prompt (see below)
    # Parse response into structured report dict
    # Append "📝 Generating investment analysis report..."
```

**Gemini Prompt for generate_report:**
```
You are a senior real estate investment analyst in India. Generate a comprehensive investment analysis report.

Property: {address}, {city}
Investment Horizon: {investment_horizon_years} years
Final Growth Score: {final_score}/100
Budget: ₹{budget_lakhs} Lakhs

MARKET DATA:
{locality_insights as formatted JSON}

COMPARABLE PROPERTIES (Analyst-Approved):
{approved_comps as formatted list}

ROI CALCULATIONS:
{roi_estimates as formatted JSON}

GROUNDING CONTEXT (Zoning & Infrastructure):
{rag_context}

ANALYST NOTES: {analyst_notes}

Generate a JSON response with exactly this structure (no markdown, pure JSON):
{{
  "executive_summary": "2-3 sentence summary",
  "growth_verdict": "STRONG BUY | BUY | HOLD | AVOID",
  "growth_drivers": ["driver1", "driver2", "driver3", "driver4"],
  "risk_factors": ["risk1", "risk2", "risk3"],
  "financial_projections": {{
    "1yr_appreciation_pct": float,
    "3yr_appreciation_pct": float,
    "5yr_appreciation_pct": float,
    "10yr_appreciation_pct": float,
    "recommended_exit_horizon": "X years"
  }},
  "comparable_analysis": "2 sentence comp analysis",
  "infrastructure_impact": "2 sentence analysis of zoning/metro impact from grounding data",
  "final_recommendation": "3-4 sentence actionable recommendation"
}}
```

## HITL State Management (In-Memory Store)

```python
# Global in-memory store for HITL thread state
_thread_store: Dict[str, AnalysisState] = {}
_stream_queues: Dict[str, asyncio.Queue] = {}
```

## Public Functions (called by main.py)

### start_analysis(request_data: dict) -> dict
```python
async def start_analysis(request_data: dict) -> dict:
    # 1. Generate thread_id = str(uuid.uuid4())
    # 2. Create initial AnalysisState from request_data
    # 3. Initialize MemorySaver checkpointer
    # 4. Build graph with interrupt_before=["hitl_verification"]
    # 5. Invoke graph with config={"configurable": {"thread_id": thread_id}}
    # 6. Graph runs nodes 1-3, pauses before hitl_verification
    # 7. Store the graph instance and config in _thread_store[thread_id]
    # 8. Return preliminary results dict
```

### resume_analysis(thread_id: str, approved_comps: list, analyst_notes: str) -> dict
```python
async def resume_analysis(thread_id: str, approved_comps: list, analyst_notes: str) -> dict:
    # 1. Retrieve stored graph and config from _thread_store
    # 2. Update state with approved_comps and analyst_notes using graph.update_state()
    # 3. Resume graph execution with graph.invoke(None, config=config)
    # 4. Return final report dict
```

### get_stream_events(thread_id: str) -> AsyncGenerator
```python
async def get_stream_events(thread_id: str):
    # Yield stream_messages from state as they're added
    # Use polling on _thread_store[thread_id] state
    # Yield JSON: {"step": node_name, "message": message, "timestamp": iso_string}
    # End stream when status is "complete"
```

## IMPORTANT IMPLEMENTATION NOTES:
- Load GEMINI_API_KEY from environment: `os.environ.get("GEMINI_API_KEY")`
- Configure genai: `genai.configure(api_key=GEMINI_API_KEY)`
- For Gemini call use: `model = genai.GenerativeModel("gemini-1.5-flash")` (more reliable free tier)
- Parse Gemini JSON response safely: strip any ```json fences, then json.loads()
- All node functions must be synchronous (LangGraph sync nodes)
- The async wrappers (start_analysis, resume_analysis) wrap the sync graph calls

Output a complete, fully working agent.py — no placeholders, no TODOs. Every function must be fully implemented with real logic.
```

---

---

# PERSON 3 PROMPT — Frontend (React + Vite)

Paste this entire block into Claude:

---

```
Build the complete frontend for "PropGrowth AI" — a luxury AI real estate investment analyzer.

## Setup
- React 18 + Vite
- No external UI libraries (pure CSS)
- No TypeScript — plain JSX
- API base URL: http://localhost:8000

## package.json
```json
{
  "name": "propgrowth-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.3.0"
  }
}
```

## vite.config.js
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } }
})
```

## Design System

**Theme: Dark luxury investment terminal**
- Background: Deep charcoal #0a0a0f with subtle grid texture (CSS background-image grid)
- Glass cards: rgba(255,255,255,0.04) backdrop-filter blur(20px) border 1px solid rgba(255,255,255,0.08)
- Primary accent: Electric gold #f0b429
- Secondary accent: Emerald #10b981 (positive), Crimson #ef4444 (negative/risk)
- Text primary: #f8fafc, Text secondary: #94a3b8
- Font: Import "DM Mono" for numbers/scores, "Syne" for headings, system-sans for body
- Border radius: 16px for cards, 8px for inputs
- Shadows: 0 0 40px rgba(240,180,41,0.08) for gold glow on hover

## App.jsx — Main Application

Three app states: `"input"`, `"analyzing"`, `"hitl"`, `"complete"`

```jsx
// State management:
const [appState, setAppState] = useState("input")
const [threadId, setThreadId] = useState(null)
const [preliminaryData, setPreliminaryData] = useState(null)
const [streamMessages, setStreamMessages] = useState([])
const [finalReport, setFinalReport] = useState(null)
```

**Flow:**
1. Input state → show PropertyInput component
2. On form submit → POST /api/analyze/start → set threadId, start SSE stream → set appState "analyzing"
3. SSE stream fills streamMessages → show AgentThinking component
4. When start API returns → set preliminaryData → set appState "hitl"
5. HITL state → show HitlVerification component with comps
6. On HITL submit → POST /api/analyze/resume → set finalReport → set appState "complete"
7. Complete state → show InvestmentReport component

## Component: PropertyInput.jsx

Full-screen centered form with glassmorphism card.

Fields:
- Property Address (text input, placeholder "e.g. Hinjewadi Phase 2, Wakad")
- City (select dropdown: Pune, Bangalore, Mumbai, Hyderabad, Noida, Chennai)
- Budget (₹ Lakhs) (number input, range 20-500)
- BHK Type (radio buttons styled as pill toggles: 1BHK, 2BHK, 3BHK, 4BHK+)
- Investment Horizon (slider: 3, 5, 7, 10 years with visual tick marks)

Big "Analyze Property →" button with gold gradient background.

Header: Large "PropGrowth AI" title with a subtle shimmer animation. Tagline: "AI-Powered Property Intelligence"

## Component: AgentThinking.jsx

Shows during "analyzing" state. Displays in a terminal-style panel:
- Each streamMessage appears as a new line with a typewriter animation
- Each message has a colored icon prefix (🏘️ yellow, 📋 blue, ⚙️ purple, ✅ green, 📊 orange, 📝 gold)
- Animated pulsing dot "Agent is thinking..." at the bottom
- Shows a "PRELIMINARY SCORE" badge when preliminaryData arrives (animate in)

## Component: HitlVerification.jsx

Props: `{ data: preliminaryData, onSubmit: (approvedComps, notes) => void }`

Layout: Two-column grid
- Left: Score ring (import GrowthScoreRing) showing preliminary_score + locality insights summary
- Right: Comps review panel

**Comps Panel:**
- Each comp shown as a card with: property name, price, area, price/sqft
- Toggle switch (styled checkbox) to include/exclude comp
- "Analyst Notes" textarea
- "Submit Review & Generate Report →" button

Header text: "Human Analyst Verification Required" with a ⚡ badge saying "HITL Active"

## Component: GrowthScoreRing.jsx

Props: `{ score: number, size?: number }`

Pure SVG animated radial gauge:
- Outer ring: dark track
- Inner arc: animated stroke-dashoffset from 0 to score% fill
- Arc color: 0-40 crimson, 41-65 amber, 66-80 gold, 81-100 emerald
- Center: large DM Mono score number with "/" 100 below
- Below ring: label "Growth Score"
- On mount, animate arc fill over 1.5 seconds using SVG stroke-dashoffset CSS animation

## Component: InvestmentReport.jsx

Props: `{ report: finalReport }`

Full dashboard with sections:

**Header row:**
- Property address + city
- GrowthScoreRing (final score, size 120)
- Verdict badge: STRONG BUY (emerald) / BUY (gold) / HOLD (amber) / AVOID (crimson)

**Grid of 4 cards:**
1. Executive Summary (full width, styled as featured card)
2. Growth Drivers (list with ✦ bullet points, emerald text)
3. Risk Factors (list with ▲ bullet points, amber text)  
4. Infrastructure Impact (from RAG grounding, styled with a small "RAG Grounded" badge)

**Financial Projections table:**
Styled table showing 1yr/3yr/5yr/10yr appreciation as bars + percentages.

**Final Recommendation** — bottom card with bold text, gold left border.

## Component: TelemetryMetrics.jsx

Small panel shown in InvestmentReport at the bottom:
- "Powered by LangGraph + ChromaDB RAG + Gemini 2.5 Flash"
- Shows: tool calls made, RAG chunks retrieved, Gemini tokens (mock ok)
- Collapsed by default, expand on click

## index.css

Global styles only:
- Import Google Fonts: DM Mono, Syne
- CSS reset
- CSS variables for the design system
- Background grid texture using CSS background-image
- Smooth scrollbar styling
- Selection color override to gold

Output ALL files with complete, working JSX code. No placeholders. Every component fully styled with inline styles or CSS classes. The UI must look premium and production-ready.
```

---

---

# PERSON 4 PROMPT — Telemetry + Integration + Demo Polish

Paste this entire block into Claude after P1 and P2 have working code:

---

```
Build telemetry.py and integration glue for "PropGrowth AI".

## FILE: telemetry.py

Use Arize Phoenix for local observability (runs in-process, no external account needed).

```python
# telemetry.py
import phoenix as px
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor
import time
from typing import Dict, Any

# Global store for custom telemetry data
_telemetry_store = {
    "traces": [],
    "tool_calls": {"search_properties": 0, "calculate_roi": 0, "get_locality_insights": 0, "rag_search": 0},
    "rag_retrievals": 0,
    "gemini_calls": 0,
    "total_latency_ms": 0
}
```

Functions to implement:

### initialize_telemetry()
- Launch Phoenix: `session = px.launch_app()`
- Set up OpenTelemetry TracerProvider
- Instrument LangChain: `LangChainInstrumentor().instrument()`
- Print: `f"🔭 Phoenix telemetry UI: {session.url}"`
- Return the session

### log_tool_call(tool_name: str, inputs: dict, outputs: dict, latency_ms: int)
- Increment _telemetry_store["tool_calls"][tool_name]
- Append to traces list

### log_rag_retrieval(query: str, num_results: int, top_result_preview: str)
- Increment rag_retrievals counter
- Log to traces

### log_gemini_call(prompt_tokens: int, response_tokens: int, latency_ms: int)
- Increment gemini_calls
- Track latency

### get_telemetry_summary() -> dict
- Returns full _telemetry_store with computed averages

## Integration Tasks

After P1 and P2 share their code, do these integration steps:

### 1. Wire telemetry into tools.py
Add `from telemetry import log_tool_call` to tools.py.
Wrap each tool function with timing:
```python
start = time.time()
result = <original logic>
log_tool_call("search_properties", inputs, result, int((time.time()-start)*1000))
return result
```

### 2. Wire telemetry into rag.py  
Add `from telemetry import log_rag_retrieval` to rag.py.
After each chroma query, call log_rag_retrieval.

### 3. Wire telemetry into agent.py
Add `from telemetry import log_gemini_call` to agent.py.
Wrap Gemini call in generate_report with timing.

### 4. Update main.py /api/telemetry endpoint
```python
from telemetry import get_telemetry_summary
@app.get("/api/telemetry")
def get_telemetry():
    return get_telemetry_summary()
```

### 5. Add startup to main.py
```python
from telemetry import initialize_telemetry
@app.on_event("startup")
async def startup():
    initialize_rag()
    initialize_telemetry()
```

## .env.example file
```
GEMINI_API_KEY=your_free_google_ai_studio_key_here
PORT=8000
# Phoenix runs locally - no keys needed
# Optional Langfuse (not needed if using Phoenix)
# LANGFUSE_PUBLIC_KEY=
# LANGFUSE_SECRET_KEY=
```

## README.md — Quick Start for Demo

Write a clean README with:
1. Prerequisites (Python 3.11, Node 18)
2. Backend setup (3 commands: cd backend, pip install -r requirements.txt, uvicorn main:app --reload)
3. Frontend setup (3 commands: cd frontend, npm install, npm run dev)
4. Add GEMINI_API_KEY to .env
5. Open http://localhost:5173
6. Phoenix observability UI auto-opens at http://localhost:6006

## Demo Script (for judges — 5 minutes)

Write a short demo_script.md with:
- Opening hook (30 sec): "PropGrowth AI uses a 6-node LangGraph agent with Human-in-the-Loop verification to analyze Indian real estate investments..."
- Live demo flow (3 min): Enter Hinjewadi Pune → watch SSE stream → show HITL comp review → show final report with RAG-grounded infrastructure section
- Technical deep-dive (1 min): Point to Phoenix dashboard showing tool call trace, RAG retrievals, Gemini latency
- Close (30 sec): Mention LangGraph interrupt mechanism, ChromaDB grounding preventing hallucination, HITL as trust layer

Output complete working files — telemetry.py, .env.example, README.md, demo_script.md.
```

---

---

## ⚡ CRITICAL TIPS FOR ALL TEAM MEMBERS

### When the generated code has errors:
Paste the error back into Claude with: *"Fix this exact error. Output only the corrected file section, no explanation."*

### LangGraph interrupt pattern (P2 — if confused):
The key is: `graph.invoke()` returns when it hits `interrupt_before`. You store the graph + config in memory. When resume is called, you call `graph.update_state(config, {"approved_comps": ..., "analyst_notes": ...})` then `graph.invoke(None, config=config)` to continue.

### If Gemini rate-limits during demo:
Add a try/except around the Gemini call and return a hardcoded mock report as fallback. Never let a demo crash on rate limits.

### SSE simplification (P1, if SSE is complex):
Replace SSE with a simple polling endpoint `GET /api/analyze/status/{thread_id}` that returns `{messages: [...], status: "running"|"awaiting_hitl"|"complete"}`. Frontend polls every 1.5 seconds. Same UX, 10x simpler to implement.

### CORS issue (most common bug):
Ensure main.py has:
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
```

### Integration order:
1. P1 finishes tools.py + rag.py → share with P2
2. P2 imports tools in agent.py
3. P4 wires telemetry after both are working
4. P3 works independently, wires to API last

---

## 🏆 JUDGING CRITERIA COVERAGE

| Criterion | How PropGrowth AI Covers It |
|-----------|----------------------------|
| Task-executing AI agent that reasons & plans | LangGraph 6-node state machine with Gemini reasoning in generate_report |
| External API interfaces | tools.py: 4 mock APIs (properties, ROI, locality, RAG search) |
| Human oversight | LangGraph interrupt_before HITL node — analyst reviews comps before final report |
| RAG pipeline to prevent hallucinations | ChromaDB + SentenceTransformers grounding all infrastructure claims |
| Deep observability & telemetry | Phoenix auto-instrumentation + custom tool call + RAG retrieval logging |
| Free-tier tools | Gemini AI Studio free, Phoenix local, ChromaDB local, SentenceTransformers local |