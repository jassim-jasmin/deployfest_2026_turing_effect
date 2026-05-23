Build a full-stack AI Property Investment Advisor called "PropMind" end to end.

## Project Overview
A task-executing AI agent for Indian real estate that reasons, plans, calls tools, 
uses RAG for grounding, and has full observability — built for a GDG Cloud hackathon.

## Tech Stack
- Backend: Python + FastAPI
- LLM: Claude claude-sonnet-4-20250514 via Anthropic SDK
- RAG: ChromaDB + sentence-transformers (all-MiniLM-L6-v2)
- Observability: Langfuse (free tier)
- Frontend: React + Vite
- Agent Loop: Custom ReAct (Reason → Act → Observe)

## Step 1: Project Structure
Create this folder structure:
propmind/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── agent.py             # ReAct agent loop
│   ├── tools.py             # Tool definitions
│   ├── rag.py               # ChromaDB RAG pipeline
│   ├── telemetry.py         # Langfuse integration
│   ├── data/                # Sample real estate docs
│   │   └── bengaluru_market.txt
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── PropertyCard.jsx
│   │   │   ├── TelemetryPanel.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   └── AgentThinking.jsx
│   └── package.json
└── .env.example

## Step 2: Backend - Tools (tools.py)
Create these agent tools with proper schemas:
1. search_properties(location, budget_min, budget_max, bhk_type) 
   → returns mock property listings for Indian cities
2. calculate_roi(price, monthly_rent, appreciation_rate)
   → returns rental_yield, break_even_years, 10yr_returns
3. get_locality_insights(locality, city)
   → returns infrastructure score, demand index, price trend
4. rag_search(query)
   → queries ChromaDB for relevant market knowledge

## Step 3: Backend - RAG Pipeline (rag.py)
- Create ChromaDB collection called "realestate_knowledge"
- Ingest sample data about:
  * Bengaluru localities (Whitefield, Sarjapur, HSR, Koramangala, Electronic City)
  * Price ranges per area (2024-2025 realistic values)
  * Rental yield benchmarks
  * Infrastructure projects (Metro Phase 3, Peripheral Ring Road)
- Embed using sentence-transformers all-MiniLM-L6-v2
- Expose query_knowledge(text, n_results=3) function

## Step 4: Backend - ReAct Agent Loop (agent.py)
Implement a proper ReAct loop:
1. REASON: Claude analyzes the user query and decides which tools to call
2. ACT: Execute the chosen tool
3. OBSERVE: Feed tool result back to Claude
4. Repeat until Claude has enough info to give final answer
5. RESPOND: Return structured JSON with properties, metrics, telemetry

Use Claude tool_use API (not just text prompting).
System prompt should make Claude an expert Indian real estate advisor.
Track all tool calls, latency, RAG docs retrieved for telemetry.

## Step 5: Backend - Telemetry (telemetry.py)
Integrate Langfuse:
- Create a trace per user query
- Log each tool call as a span with input/output
- Log RAG retrievals with similarity scores  
- Log final LLM response
- Calculate and store: total_latency, tools_called, rag_docs_used, confidence_score
- Expose /api/telemetry endpoint returning last 10 traces

## Step 6: Backend - FastAPI App (main.py)
Endpoints:
- POST /api/analyze → runs agent, returns properties + telemetry
- GET /api/telemetry → returns recent traces from Langfuse
- GET /api/health → health check
- Enable CORS for localhost:5173

## Step 7: Frontend (React + Vite)
Dark luxury theme (#030308 background, indigo/purple accents).
Components:
- SearchBar: text input with suggested queries
- AgentThinking: animated tool call badges showing ReAct steps live (SSE stream)
- PropertyCard: score ring, price, rental yield, appreciation, pros/cons
- TelemetryPanel: tools called, RAG docs, latency, confidence score
- MarketInsight: key insight card
- RecommendationCard: top pick with reasoning

Use SSE (Server-Sent Events) to stream agent thinking steps in real time.

## Step 8: Sample Data (data/bengaluru_market.txt)
Generate realistic content covering:
- 10 Bengaluru localities with price per sqft (2024 values)
- Rental yields per area
- Upcoming infrastructure impact
- Investment risk ratings
- Comparison with Hyderabad and Pune markets

## Step 9: Environment Setup (.env.example)
ANTHROPIC_API_KEY=your_key
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_key
LANGFUSE_HOST=https://cloud.langfuse.com

## Step 10: README.md
Include:
- Architecture diagram (ASCII)
- Setup instructions
- How the ReAct loop works
- How RAG prevents hallucinations
- How to view Langfuse dashboard
- Demo script for judges

## Key Requirements
- Agent must use Claude's native tool_use API (not string parsing)
- RAG must actually retrieve from ChromaDB (not fake it)
- Telemetry must show real tool call sequences
- Frontend must stream agent thinking in real time via SSE
- All prices must be realistic Indian market values (₹ not $)
- Must run fully on free tiers (no paid APIs except Anthropic)

Start with Step 1 and implement everything completely. 
Ask me before skipping any step.
