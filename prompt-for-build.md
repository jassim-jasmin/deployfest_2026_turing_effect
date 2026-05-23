# 📋 ARCHITECTURAL BLUEPRINT (Share with the entire team)

Before running to your workstations, copy-paste these strict global contracts. **Do not deviate from these variable names, types, or file paths.**

### Global Directory Layout

```text
propgrowth/
├── backend/
│   ├── main.py          # Person 1
│   ├── tools.py         # Person 1
│   ├── rag.py           # Person 1
│   ├── agent.py         # Person 2
│   ├── telemetry.py     # Person 4
│   ├── requirements.txt # Shared
│   └── data/
│       └── master_plans.txt # Person 1
└── frontend/            # Person 3
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── index.css
        └── components/

```

### Shared State Schema (`AnalysisState`)

This exact data contract maps directly between the LangGraph state backend, the FastAPI JSON payloads, and the React frontend state hooks:

* `thread_id`: `str` (UUIDv4 string)
* `address`: `str`
* `city`: `str`
* `budget_lakhs`: `float`
* `bhk_type`: `str`
* `investment_horizon_years`: `int`
* `comps`: `List[dict]` (Array of property dictionaries)
* `locality_insights`: `dict`
* `rag_context`: `str`
* `roi_estimates`: `dict`
* `preliminary_score`: `int` (1-100)
* `hitl_approved`: `bool`
* `approved_comps`: `List[dict]`
* `analyst_notes`: `str`
* `final_score`: `int` (1-100)
* `report`: `dict` (The structured Gemini output)
* `stream_messages`: `List[str]` (Array of system step strings)

---

# 👤 PERSON 1 PROMPT: Backend Core & Data Engine

**Role:** Data & API Infrastructure

**Core Task:** Build `tools.py`, `rag.py`, `main.py`, and seed data files.

```text
You are Person 1 on a 4-man hackathon team building "PropGrowth AI". Build the backend engine, data models, and API surface layer. 
Output complete, production-ready, clean Python code. No placeholders, no TODOs, no "insert logic here". 

Ensure that you allow telemetry hooks (Person 4) to overlay your execution block seamlessly by wrapping metrics tracking beautifully.

## 1. Setup requirements.txt
Create propgrowth/backend/requirements.txt:

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

```

## 2. FILE: tools.py
Implement these 3 core functions. Add an execution timer mechanism inside each function that checks if a telemetry hook exists before executing, preparing for Person 4's integration:

1. `search_properties(location: str, budget_min: float, budget_max: float, bhk_type: str) -> list`: 
Returns exactly 4 realistic mock comparable dictionaries for Indian cities. Fields: [id, title, location, price, bhk, area_sqft, price_per_sqft, monthly_rent, listing_age_days, distance_km, nearby_metro, source]. Seed dynamically: if location has "Pune", return Pune metrics; if "Bangalore", return Bangalore metrics; else standard metro fallback.
2. `calculate_roi(price_lakhs: float, monthly_rent: float, appreciation_rate_pct: float) -> dict`: 
Returns exact math: 
- `rental_yield_pct`: (monthly_rent * 12) / (price_lakhs * 100000) * 100
- `break_even_years`: round(price_lakhs / (monthly_rent * 12 / 100000), 1)
- `projected_10yr_value_lakhs`: price_lakhs * ((1 + appreciation_rate_pct/100)**10)
- `total_10yr_return_pct`: ((projected_10yr_value_lakhs - price_lakhs) / price_lakhs) * 100
- `monthly_cashflow`: monthly_rent - (price_lakhs * 100000 * 0.7 * 0.008) # Assumed EMI logic
3. `get_locality_insights(locality: str, city: str) -> dict`: 
Deterministic output using standard hashing (`hash(locality + city)`). Fields: [infrastructure_score (1-100), demand_index (1-100), population_growth_pct, avg_price_trend_pct, top_employers_nearby (list of 3), connectivity_rating, flood_risk, social_infrastructure (dict of schools/hospitals/malls)]. Hardcode explicit overrides for "Hinjewadi, Pune", "Whitefield, Bangalore", "Bandra, Mumbai", "Sector 62, Noida".

## 3. FILE: rag.py
Implement a vectorized ChromaDB localized module:
- Persistent client mapping to: `chromadb.PersistentClient(path="./chroma_db")`
- Target Collection: `zoning_infrastructure`
- Embeddings Engine: `SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")`
- Write an execution flow checking if collection is empty on load. If true, seed from `data/master_plans.txt` by splitting items on double newlines (`\n\n`). Store with standard tracking schema: `{source: "master_plans", chunk_id: int}`.
- Implement `query_rag_context(query: str, n_results: int = 3) -> str`: Return results structured as: `"GROUNDING CONTEXT:\n" + "\n---\n".join(results)`. Fallback string: `"No specific zoning or infrastructure data found for this query."`
- Implement `initialize_rag()` to safely interface lifecycle setup at system initiation.

## 4. FILE: data/master_plans.txt
Write a text file with 20+ realistic urban planning paragraphs across Pune, Bangalore, Mumbai, Hyderabad, Noida, and Chennai. Explicitly mention infrastructure milestones, tech corridors, metro extensions, dates (2025–2029), and appreciation metrics. Ensure paragraphs are cleanly separated by a single blank line.

## 5. FILE: main.py
Set up FastAPI app instance. Setup CORS routing allowing all methods and explicitly whitelist `http://localhost:5173`.
Implement these 4 rigid structural REST routes:

1. `POST /api/analyze/start`: Payload: `{address, city, budget_lakhs, bhk_type, investment_horizon_years}`. 
Execution: Imports `start_analysis` from `agent.py`. Resolves immediately to allow UI synchronization. Returns state parameters.
2. `POST /api/analyze/resume`: Payload: `{thread_id, approved_comps, analyst_notes}`. 
Execution: Imports `resume_analysis` from `agent.py`. Blocks until execution trace ends, returning final JSON dictionary report payloads.
3. `GET /api/analyze/status/{thread_id}`: Poll endpoint (Person 3 optimization fallback). Fetches active in-memory record for running graph compilation and sends back current states: `{stream_messages: [...], status: "running" | "awaiting_hitl" | "complete"}`.
4. `GET /api/telemetry`: Imports `get_telemetry_summary` from `telemetry.py`. If telemetry is un-imported or absent, gracefully fall back to a mock dictionary matching the telemetry blueprint spec.
5. `GET /api/health`: Returns `{"status": "ok", "version": "1.0.0"}`.

At startup (`@app.on_event("startup")`), run `initialize_rag()`. Make sure hooks are available for telemetry startup processes.

```

---

# 👤 PERSON 2 PROMPT: Agent Brain & LangGraph Logic

**Role:** AI Workflow & Orchestrator

**Core Task:** Build `agent.py` using LangGraph and handle the Human-in-the-Loop (HITL) interrupt.

```text
You are Person 2 on a 4-man hackathon team building "PropGrowth AI". Build the agent.py state orchestration machine.
Output complete, production-ready, clean Python code. No placeholders, no TODOs, no "insert logic here".

## 1. State Definition
Define the exact global state schema tracking parameters inside a standard `TypedDict` structure named `AnalysisState`:
[thread_id, address, city, budget_lakhs, bhk_type, investment_horizon_years, comps, locality_insights, rag_context, roi_estimates, preliminary_score, hitl_approved, approved_comps, analyst_notes, final_score, report, stream_messages]

## 2. Memory Store Lifecycle Infrastructure
Initialize two thread stores in global memory:
- `_thread_store: Dict[str, dict]` (Holds full serialized states mapping to unique thread tokens)
- Implement `MemorySaver()` as checkpointer target interface for LangGraph execution state preservation.

## 3. LangGraph Workflow Node Pipeline
Compile a 6-node state-graph machine with an abstract interrupt checkpoint explicitly intercepting transition directly before hitl processing:
`fetch_market_data` -> `inject_rag_context` -> `calculate_preliminary` -> [INTERRUPT BOUNDARY] -> `hitl_verification` -> `calculate_final_score` -> `generate_report`

Implement each step as a synchronous execution node modifying state:
1. `fetch_market_data`: Strip address for tokens. Call Person 1's tools: `search_properties` and `get_locality_insights`. Appends system status log string to `stream_messages`: "🏘️ Fetching comparable properties and market data..."
2. `inject_rag_context`: Construct an explicit string query: `f"infrastructure development zoning {state['city']} {state['address']}"`. Invoke Person 1's `rag.py -> query_rag_context(query)`. Appends system status log string to `stream_messages`: "📋 Retrieving zoning laws and infrastructure master plans..."
3. `calculate_preliminary`: Isolate price indices, run `tools.calculate_roi` on median values, and score properties via mathematical components: (30% infrastructure + 25% demand + 25% normalized pricing trend + 20% normalized yield metrics). Add a +5 bonus if "metro" or "IT park" pops inside the rag text payload (cap score at 100). Appends system status log string to `stream_messages`: "⚙️ Calculating preliminary growth score..."
4. `hitl_verification`: A placeholder transit node executed immediately upon thread waking. Appends system status log string to `stream_messages`: "✅ Analyst review received. Processing approved comparables..."
5. `calculate_final_score`: Extract user-filtered `approved_comps`. Rerun exact mathematical operations on mean valuation of selected nodes. Add +3 points for positive analyst keywords ('bullish', 'strong', 'good') or drop -3 for negative keywords ('risk', 'overpriced', 'concern'). Store calculation output inside `final_score`. Appends system status log string to `stream_messages`: "📊 Calculating final weighted investment score..."
6. `generate_report`: Assemble a structural call using `google.generativeai` utilizing the unified free-tier layout model target `"gemini-1.5-flash"`. Instruct model via prompt parameters to enforce a pure, un-fenced, raw clean JSON dictionary string output. Catch format issues cleanly, and append text string to `stream_messages`: "📝 Generating investment analysis report..."

## 4. LLM Schema Format Requirement
Enforce this exact structural parsing schema configuration mapping string results into Gemini execution steps:
{
  "executive_summary": "2-3 sentences",
  "growth_verdict": "STRONG BUY | BUY | HOLD | AVOID",
  "growth_drivers": ["str", "str", "str", "str"],
  "risk_factors": ["str", "str", "str"],
  "financial_projections": {
    "1yr_appreciation_pct": float, "3yr_appreciation_pct": float, "5yr_appreciation_pct": float, "10yr_appreciation_pct": float, "recommended_exit_horizon": "X years"
  },
  "comparable_analysis": "str",
  "infrastructure_impact": "str",
  "final_recommendation": "str"
}
Add a safe fallback dictionary block to rescue executions if API rate limits or timeout breaks occur.

## 5. State Integration Execution APIs
Expose these exact async interface structures called directly by Person 1's `main.py`:
- `async def start_analysis(request_data: dict) -> dict`: Compiles the graph configuration mapping passing user inputs, invokes thread processing execution tracking path up to the interrupt marker checkpoint, caches runtime state variables locally in `_thread_store`, and returns the partial calculated metrics mapping.
- `async def resume_analysis(thread_id: str, approved_comps: list, analyst_notes: str) -> dict`: Extracts structural graph pointers via `_thread_store`, modifies current target state variables with user adjustments using `graph.update_state()`, signals thread wake execution using `graph.invoke(None, config)`, and returns final output calculations array.

```

---

# 👤 PERSON 3 PROMPT: Frontend Luxury UI (React + Vite)

**Role:** Client Application & Visual Design

**Core Task:** Build a dark luxury investment terminal using pure CSS, vanilla JSX, and the polling optimization fallback.

```text
You are Person 3 on a 4-man hackathon team building "PropGrowth AI". Build the frontend workspace application.
Output complete, production-ready, beautifully styled clean React components within single-file/modular clean layouts. No external component design toolkits allowed—write pure, raw custom CSS or inline structures.

## 1. Technical Parameters
- Stack: React 18 + Vite compilation engine (Port 5173)
- Coding: Clean JavaScript vanilla configuration layout (No TypeScript).
- Target Base API Endpoint: `http://localhost:8000`

## 2. Styling Guide: Dark Luxury Terminals
- Deep background base colors: Charcoal #0a0a0f layered with a custom geometric design grid.
- Surface structure treatment: Glassmorphism container blocks (`rgba(255,255,255,0.04)` backdrop blur overlay bordered via 1px border frames utilizing `rgba(255,255,255,0.08)`).
- Typography layout: Modern geometric typography accents. Headings: "Syne", Numerical metrics metrics: "DM Mono", body copy lines: system sans-serif.
- Color accent system: Primary Gold (`#f0b429`), Emerald highlights (`#10b981`), Crimson risk colors (`#ef4444`).

## 3. Application State Logic Engine
Manage unified structural interface navigation tracking exactly across 4 designated state loops: `"input"`, `"analyzing"`, `"hitl"`, `"complete"`. 

Implement polling optimization loops interfacing endpoint paths safely: when start functions complete processing sequences, begin firing sequential XML HTTP/fetch operations to `/api/analyze/status/{thread_id}` every 1.5 seconds to track compilation tracking updates inside local state targets.

## 4. Component Architectural Blueprint
Deliver completely functional React component files matching these interface designs:

1. `PropertyInput.jsx`: Clean centered glass design card input handling form configurations. Capture address string text inputs, dropdown options array for Indian Cities [Pune, Bangalore, Mumbai, Hyderabad, Noida, Chennai], input fields for Budget values up to ₹500 Lakhs, BHK toggles [1BHK, 2BHK, 3BHK, 4BHK+], and horizon execution sliders up to 10 years.
2. `AgentThinking.jsx`: High-performance terminal tracking display window. Print lines mapped directly from array state element configurations using typewriter animations. Prepend appropriate state visual emojis matching target categories: 🏘️, 📋, ⚙️, ✅, 📊, 📝.
3. `GrowthScoreRing.jsx`: Animate a high-grade SVG vector radial ring metric container reflecting numeric percentage configurations (0-100 score). Apply transitions and dynamic conditional color updates mapping directly across thresholds (0-40 crimson, 41-65 amber, 66-80 gold, 81-100 emerald).
4. `HitlVerification.jsx`: Split layout framework display window. Left pane presents active `GrowthScoreRing` rendering partial initialization analytics. Right pane loads interactive checkboxes mapping to target data entries from `comps` array payloads, custom feedback comment text areas, and submission triggers driving backend compilation processes.
5. `InvestmentReport.jsx`: Dashboard detailing financial growth matrices. Render structural dashboard widgets showing summary segments, structured driver elements lists, categorized operational threats, predictive investment charts mapping projections, and dedicated markdown panels for grounding references.
6. `TelemetryMetrics.jsx`: Hidden drop-down accordion drawer summarizing processing analytics metrics: tracking total execution times, active processing call traces, and systemic information structures.

```

---

# 👤 PERSON 4 PROMPT: Telemetry, System Integration & Demo Polish

**Role:** Observability, Instrumentation & QA Validation

**Core Task:** Build `telemetry.py`, inject timing decorators into other people's functions, and write the demo documentation.

```text
You are Person 4 on a 4-man hackathon team building "PropGrowth AI". You own system telemetry, code integration orchestration, package verification, and demo execution scripts. 
Output complete, fully working infrastructure scripts.

## 1. FILE: telemetry.py
Construct an active internal system tracking layer powered by Arize Phoenix. Configure localized, trace metrics parsing definitions mapping directly to this storage blueprint layout structure:
```python
import phoenix as px
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor
import time

_telemetry_store = {
    "traces": [],
    "tool_calls": {"search_properties": 0, "calculate_roi": 0, "get_locality_insights": 0, "rag_search": 0},
    "rag_retrievals": 0,
    "gemini_calls": 0,
    "total_latency_ms": 0
}

```

Implement these explicit metric monitoring handlers:

* `initialize_telemetry()`: Launch local server session instances via `px.launch_app()`, set internal system TracerProviders, instrument active OpenTelemetry LangChain handlers (`LangChainInstrumentor().instrument()`), and print dashboard access locations clearly.
* `log_tool_call(tool_name, inputs, outputs, latency_ms)`: Update systemic counters in `_telemetry_store` and append transactional records to trace lists.
* `log_rag_retrieval(query, num_results, top_result_preview)`: Increment operational counter tracking statistics inside repository parameters.
* `log_gemini_call(prompt_tokens, response_tokens, latency_ms)`: Record performance overhead stats tracking generative calls.
* `get_telemetry_summary() -> dict`: Formats structural telemetry statistics metrics mapping out execution totals directly back to endpoints.

## 2. Integration Integration Pipeline (The 90-Minute Assembly Script)

When Persons 1 and 2 deliver their modules, execute these exact surgical code insertions:

* **Injection 1 (tools.py)**: Wrap execution loops across all core tools with an extraction time logic layer tracking call data via `log_tool_call`.
* **Injection 2 (rag.py)**: Intercept internal query routines inside execution points to route logging events to `log_rag_retrieval`.
* **Injection 3 (agent.py)**: Encapsulate Gemini inference blocks with systemic execution logs routing timing data directly to `log_gemini_call`.
* **Injection 4 (main.py)**: Wire startup operations to loop initialization parameters through `initialize_telemetry()`, and hook `/api/telemetry` directly to output reports via `get_telemetry_summary()`.

## 3. FILE: .env.example

Create a unified project configuration template documenting operational needs:

```text
GEMINI_API_KEY=your_free_google_ai_studio_key_here
PORT=8000

```

## 4. FILE: README.md

Deliver clean terminal deployment documentation for hackathon evaluators outlining prerequisites, backend installation sequences, frontend development setup steps, environment routing maps, and access coordinates.

## 5. FILE: demo_script.md

Compose an impactful 5-minute technical script highlighting how LangGraph's state machine handles asynchronous execution steps, detailing the use of ChromaDB for localized data grounding, showing off the Human-in-the-Loop review screen, and ending with a walkthrough of the Phoenix observability tracing metrics dashboard.