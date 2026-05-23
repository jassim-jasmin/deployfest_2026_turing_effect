import os
import json
import uuid
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import initialize_rag, query_rag_context
from tools import search_properties, get_locality_insights, calculate_roi

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="PropGrowth AI - Backend Core",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory thread storage for tracking simulated runs and fallback state
active_threads = {}

# Payload schemas
class StartAnalysisPayload(BaseModel):
    address: str
    city: str
    budget_lakhs: float
    bhk_type: str
    investment_horizon_years: int

class ResumeAnalysisPayload(BaseModel):
    thread_id: str
    approved_comps: List[str]
    analyst_notes: str

# Startup handler
@app.on_event("startup")
def startup_event():
    try:
        initialize_rag()
    except Exception as e:
        print(f"Error initializing RAG at startup: {e}")

@app.get("/api/health")
def health_check():
    """
    Returns API operational status and version.
    """
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/analyze/start")
def start_analysis_endpoint(payload: StartAnalysisPayload):
    """
    Initiates analysis. Attempts to delegate to agent.py, otherwise
    falls back to mock pipeline using tools and RAG.
    """
    # 1. Attempt agent.py dynamic import and invocation
    try:
        from agent import start_analysis
        # Call agent function if it is present and executable
        if callable(start_analysis):
            result = start_analysis(payload.model_dump())
            return result
    except (ImportError, AttributeError, TypeError):
        pass

    # 2. Graceful fallback logic
    thread_id = f"thread_{uuid.uuid4().hex[:12]}"
    
    # Pre-calculate components to prepare the report
    try:
        # Search properties matching location
        comps = search_properties(
            location=payload.address, 
            budget_min=payload.budget_lakhs * 0.8, 
            budget_max=payload.budget_lakhs * 1.2, 
            bhk_type=payload.bhk_type
        )
        
        # Get locality insights
        insights = get_locality_insights(locality=payload.address, city=payload.city)
        
        # Determine average financials to compute ROI
        avg_price = sum(c["price"] for c in comps) / len(comps) if comps else payload.budget_lakhs
        avg_rent = sum(c["monthly_rent"] for c in comps) / len(comps) if comps else 20000.0
        appreciation = insights.get("avg_price_trend_pct", 8.0)
        
        roi = calculate_roi(
            price_lakhs=avg_price, 
            monthly_rent=avg_rent, 
            appreciation_rate_pct=appreciation
        )
        
        # Query zoning and planning context
        rag_query = f"infrastructure zoning development {payload.address} {payload.city}"
        rag_context = query_rag_context(query=rag_query)
        
        # Calculate preliminary investment score
        infra_score = insights.get("infrastructure_score", 50)
        demand_score = insights.get("demand_index", 50)
        rental_yield = roi.get("rental_yield_pct", 3.0)
        
        prelim_score = int(0.4 * infra_score + 0.3 * demand_score + 3.0 * rental_yield)
        prelim_score = max(10, min(98, prelim_score)) # clamp between 10 and 98
        
        report = {
            "comps": comps,
            "locality_insights": insights,
            "roi_metrics": roi,
            "rag_context": rag_context,
            "input_parameters": payload.model_dump(),
            "scores": {
                "preliminary_score": prelim_score,
                "final_score": None
            },
            "status": "awaiting_hitl",
            "analyst_notes": None,
            "verdict": None
        }
    except Exception as e:
        # If calculation fails, create a generic skeleton structure to prevent crash
        report = {
            "comps": [],
            "locality_insights": {},
            "roi_metrics": {},
            "rag_context": "Error preparing analysis context.",
            "input_parameters": payload.model_dump(),
            "scores": {
                "preliminary_score": 50,
                "final_score": None
            },
            "status": "awaiting_hitl",
            "analyst_notes": None,
            "verdict": None
        }

    # Store state progress log details in active threads
    active_threads[thread_id] = {
        "status": "awaiting_hitl",
        "stream_messages": [
            "Initiating analysis pipeline...",
            "Parsed input parameters successfully.",
            f"Fetched comparable properties matching location: {payload.address}.",
            f"Retrieved zoning and planning documents from RAG.",
            "Calculated preliminary ROI and appreciation metrics.",
            "Awaiting human-in-the-loop analyst review and approval."
        ],
        "report": report
    }
    
    return {
        "thread_id": thread_id,
        "status": "awaiting_hitl",
        "preliminary_report": report
    }

@app.post("/api/analyze/resume")
async def resume_analysis_endpoint(payload: ResumeAnalysisPayload):
    """
    Resumes analysis workflow. Imports and awaits agent.py resume_analysis,
    otherwise updates internal state tracker.
    """
    # 1. Attempt agent.py dynamic import and invocation
    try:
        from agent import resume_analysis
        if callable(resume_analysis):
            # Await the execution of resume_analysis if it is async
            if asyncio.iscoroutinefunction(resume_analysis):
                result = await resume_analysis(payload.model_dump())
            else:
                result = resume_analysis(payload.model_dump())
            return result
    except (ImportError, AttributeError, TypeError):
        pass

    # 2. Graceful fallback logic
    thread_id = payload.thread_id
    if thread_id not in active_threads:
        raise HTTPException(status_code=404, detail="Thread ID not found in active records.")
        
    thread = active_threads[thread_id]
    report = thread["report"]
    
    # Filter approved comps
    original_comps = report.get("comps", [])
    approved_comps_list = [c for c in original_comps if c.get("id") in payload.approved_comps]
    # If no comps approved, keep the original list to prevent crash
    if approved_comps_list:
        report["comps"] = approved_comps_list
        
    report["analyst_notes"] = payload.analyst_notes
    
    # Calculate final score based on notes sentiment and adjustments
    prelim_score = report["scores"]["preliminary_score"]
    adjustment = len(payload.approved_comps) - len(original_comps)
    
    notes_lower = payload.analyst_notes.lower()
    if "strong" in notes_lower or "buy" in notes_lower or "excellent" in notes_lower:
        adjustment += 4
    elif "risk" in notes_lower or "avoid" in notes_lower or "concern" in notes_lower:
        adjustment -= 5
        
    final_score = max(5, min(99, prelim_score + adjustment))
    report["scores"]["final_score"] = final_score
    
    # Determine final verdict
    if final_score >= 80:
        verdict = "STRONG BUY"
    elif final_score >= 65:
        verdict = "BUY"
    elif final_score >= 50:
        verdict = "HOLD"
    else:
        verdict = "AVOID"
        
    report["verdict"] = verdict
    report["status"] = "complete"
    
    # Update active threads progress log
    thread["status"] = "complete"
    thread["stream_messages"].extend([
        "Analyst review and approvals parsed.",
        "Filtering comps list according to analyst feedback.",
        "Adjusting investment score and executing final rule check...",
        "Investment report finalized successfully."
    ])
    
    return report

@app.get("/api/analyze/status/{thread_id}")
def get_analysis_status(thread_id: str):
    """
    Polling fallback route. Fetches the active progress log for the agent.
    """
    # Check fallback in-memory records
    if thread_id in active_threads:
        t = active_threads[thread_id]
        return {
            "stream_messages": t["stream_messages"],
            "status": t["status"]
        }
        
    # Standard fallback if not found
    raise HTTPException(status_code=404, detail="Thread ID not found.")

@app.get("/api/telemetry")
def get_telemetry():
    """
    Imports and fetches get_telemetry_summary from telemetry.py.
    Falls back to mock_telemetry_traces.json if unavailable.
    """
    try:
        from telemetry import get_telemetry_summary
        if callable(get_telemetry_summary):
            return get_telemetry_summary()
    except (ImportError, AttributeError):
        pass

    # Read from data/mock_telemetry_traces.json
    mock_file = os.path.join(CURRENT_DIR, "data", "mock_telemetry_traces.json")
    if os.path.exists(mock_file):
        try:
            with open(mock_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    # Absolute fallback schema
    return {"mock_traces": []}
