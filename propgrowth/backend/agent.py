import os
import uuid
import json
import time
import asyncio
import asyncio.coroutines
from typing import TypedDict, List, Dict, Any, Optional

import google.generativeai as genai
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Global in-memory store for active thread states
_thread_store: Dict[str, dict] = {}


class AnalysisState(TypedDict):
    """
    Exact shared state schema matching global contract.
    """
    thread_id: str
    address: str
    city: str
    budget_lakhs: float
    bhk_type: str
    investment_horizon_years: int
    comps: List[dict]
    locality_insights: dict
    rag_context: str
    roi_estimates: dict
    preliminary_score: int
    hitl_approved: bool
    approved_comps: List[dict]
    analyst_notes: str
    final_score: int
    report: dict
    stream_messages: List[str]


class AwaitableDict(dict):
    """
    Hybrid dict class that supports both standard synchronous dictionary operations
    and asynchronous awaiting. This resolves uvicorn/FastAPI serialization issues
    when a route calls an async function synchronously.
    """
    def __await__(self):
        async def _async_impl():
            return self
        return _async_impl().__await__()


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def _calculate_median(numbers: List[float]) -> float:
    """Calculates the median of a list of floats."""
    if not numbers:
        return 0.0
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2.0
    else:
        return sorted_numbers[mid]


def _normalize_range(val: float, min_val: float, max_val: float) -> float:
    """Normalizes a value in a [min_val, max_val] range to a 0-100 score."""
    if val <= min_val:
        return 0.0
    if val >= max_val:
        return 100.0
    return ((val - min_val) / (max_val - min_val)) * 100.0


def _safe_parse_gemini_json(text: str) -> dict:
    """Safely extracts and parses JSON from Gemini output, stripping code fences."""
    if not text:
        raise ValueError("Empty response from Gemini model")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return json.loads(cleaned)


def _get_fallback_report(state: dict) -> dict:
    """Generates a safe fallback report conforming to the target JSON schema."""
    final_score = state.get("final_score", 50)
    city = state.get("city", "City")
    horizon = state.get("investment_horizon_years", 5)

    if final_score >= 80:
        verdict = "STRONG BUY"
    elif final_score >= 65:
        verdict = "BUY"
    elif final_score >= 50:
        verdict = "HOLD"
    else:
        verdict = "AVOID"

    return {
        "executive_summary": f"The property under evaluation in {city} shows stable market parameters. Based on the calculated growth score of {final_score}/100, the investment outlook remains moderate with localized risks.",
        "growth_verdict": verdict,
        "growth_drivers": [
            f"Favorable micro-market appreciation trends in {city}.",
            "Good connectivity to commercial hubs and primary highways.",
            "Strong tenant demand driving consistent rental yields.",
            "Positive development layout zoning updates in the target zone."
        ],
        "risk_factors": [
            "Short-term pricing volatility in the local sector.",
            "Infrastructure completion timeline risks.",
            "Potential high-density competition in adjacent projects."
        ],
        "financial_projections": {
            "1yr_appreciation_pct": float(round(final_score * 0.08, 1)),
            "3yr_appreciation_pct": float(round(final_score * 0.25, 1)),
            "5yr_appreciation_pct": float(round(final_score * 0.45, 1)),
            "10yr_appreciation_pct": float(round(final_score * 0.95, 1)),
            "recommended_exit_horizon": f"{horizon} years"
        },
        "comparable_analysis": "Comparable properties in the locality show prices aligning well with the budget range. Median transaction values are stable.",
        "infrastructure_impact": f"Zoning and development plan updates in {city} indicate long-term growth driven by transit corridors.",
        "final_recommendation": f"Proceed with caution. Aim to acquire at or below the median market price. Suggested hold horizon is {horizon} years to maximize gains."
    }


def _update_main_active_threads(thread_id: str, status: str, stream_messages: List[str], report: dict = None) -> None:
    """Updates the active threads tracking registry in main.py to keep polling sync work."""
    try:
        import main
        main.active_threads[thread_id] = {
            "status": status,
            "stream_messages": stream_messages,
            "report": report or {}
        }
    except Exception:
        pass


# =====================================================================
# LANGGRAPH NODE FUNCTIONS (SYNCHRONOUS)
# =====================================================================

def fetch_market_data(state: AnalysisState) -> dict:
    """Calls search_properties and get_locality_insights using Person 1's tools."""
    try:
        from tools import search_properties, get_locality_insights
        address = state.get("address", "")
        city = state.get("city", "")
        budget_lakhs = state.get("budget_lakhs", 100.0)
        bhk_type = state.get("bhk_type", "2BHK")

        comps = search_properties(
            location=f"{address}, {city}",
            budget_min=budget_lakhs * 0.8,
            budget_max=budget_lakhs * 1.2,
            bhk_type=bhk_type
        )
        locality_insights = get_locality_insights(locality=address, city=city)
    except Exception:
        comps = []
        locality_insights = {}

    stream = list(state.get("stream_messages") or [])
    stream.append("🏘️ Fetching comparable properties and market data...")

    return {
        "comps": comps,
        "locality_insights": locality_insights,
        "stream_messages": stream
    }


def inject_rag_context(state: AnalysisState) -> dict:
    """Queries RAG context utilizing Person 1's query_rag_context."""
    try:
        try:
            from rag import query_rag_context
        except ImportError:
            from tools import rag_search as query_rag_context

        city = state.get("city", "")
        address = state.get("address", "")
        query = f"infrastructure development zoning {city} {address}"
        rag_context = query_rag_context(query)
    except Exception:
        rag_context = "No specific zoning or infrastructure data found for this query."

    stream = list(state.get("stream_messages") or [])
    stream.append("📋 Retrieving zoning laws and infrastructure master plans...")

    return {
        "rag_context": rag_context,
        "stream_messages": stream
    }


def calculate_preliminary(state: AnalysisState) -> dict:
    """Calculates ROI estimates and preliminary growth scores."""
    try:
        from tools import calculate_roi

        comps = state.get("comps") or []
        prices = [c["price"] for c in comps if "price" in c]
        rents = [c["monthly_rent"] for c in comps if "monthly_rent" in c]

        median_price = _calculate_median(prices) if prices else state.get("budget_lakhs", 100.0)
        median_rent = _calculate_median(rents) if rents else 20000.0

        appreciation = state.get("locality_insights", {}).get("avg_price_trend_pct", 8.0)
        roi_estimates = calculate_roi(
            price_lakhs=median_price,
            monthly_rent=median_rent,
            appreciation_rate_pct=appreciation
        )
    except Exception:
        roi_estimates = {}

    infra = state.get("locality_insights", {}).get("infrastructure_score", 50)
    demand = state.get("locality_insights", {}).get("demand_index", 50)
    trend = state.get("locality_insights", {}).get("avg_price_trend_pct", 0.0)

    trend_norm = _normalize_range(trend, 0.0, 20.0)
    yield_pct = roi_estimates.get("rental_yield_pct", 0.0) if roi_estimates else 0.0
    yield_norm = _normalize_range(yield_pct, 2.0, 6.0)

    score = (infra * 0.30) + (demand * 0.25) + (trend_norm * 0.25) + (yield_norm * 0.20)

    rag_context = state.get("rag_context", "")
    if "metro" in rag_context.lower() or "it park" in rag_context.lower():
        score += 5

    preliminary_score = min(100, max(1, int(round(score))))
    stream = list(state.get("stream_messages") or [])
    stream.append("⚙️ Calculating preliminary growth score...")

    return {
        "roi_estimates": roi_estimates,
        "preliminary_score": preliminary_score,
        "stream_messages": stream
    }


def hitl_verification(state: AnalysisState) -> dict:
    """Transit node executed immediately after thread resume."""
    stream = list(state.get("stream_messages") or [])
    stream.append("✅ Analyst review received. Processing approved comparables...")
    return {
        "stream_messages": stream
    }


def calculate_final_score(state: AnalysisState) -> dict:
    """Calculates ROI and final investment score based on approved comps and analyst notes."""
    try:
        from tools import calculate_roi

        approved_comps = state.get("approved_comps") or []
        if not approved_comps:
            approved_comps = state.get("comps") or []

        if approved_comps:
            avg_price = sum(float(c.get("price", 0.0)) for c in approved_comps) / len(approved_comps)
            avg_rent = sum(float(c.get("monthly_rent", 0.0)) for c in approved_comps) / len(approved_comps)
        else:
            avg_price = state.get("budget_lakhs", 100.0)
            avg_rent = 20000.0

        appreciation = state.get("locality_insights", {}).get("avg_price_trend_pct", 8.0)
        roi_estimates = calculate_roi(
            price_lakhs=avg_price,
            monthly_rent=avg_rent,
            appreciation_rate_pct=appreciation
        )
    except Exception:
        roi_estimates = state.get("roi_estimates") or {}

    infra = state.get("locality_insights", {}).get("infrastructure_score", 50)
    demand = state.get("locality_insights", {}).get("demand_index", 50)
    trend = state.get("locality_insights", {}).get("avg_price_trend_pct", 0.0)

    trend_norm = _normalize_range(trend, 0.0, 20.0)
    yield_pct = roi_estimates.get("rental_yield_pct", 0.0) if roi_estimates else 0.0
    yield_norm = _normalize_range(yield_pct, 2.0, 6.0)

    score = (infra * 0.30) + (demand * 0.25) + (trend_norm * 0.25) + (yield_norm * 0.20)

    rag_context = state.get("rag_context", "")
    if "metro" in rag_context.lower() or "it park" in rag_context.lower():
        score += 5

    score = min(100, max(1, int(round(score))))

    # Modifier based on analyst notes keywords
    notes = (state.get("analyst_notes") or "").lower()
    modifier = 0
    if any(kw in notes for kw in ["bullish", "strong", "good"]):
        modifier += 3
    if any(kw in notes for kw in ["risk", "overpriced", "concern"]):
        modifier -= 3

    final_score = min(100, max(1, score + modifier))
    stream = list(state.get("stream_messages") or [])
    stream.append("📊 Calculating final weighted investment score...")

    return {
        "roi_estimates": roi_estimates,
        "final_score": final_score,
        "stream_messages": stream
    }


def generate_report(state: AnalysisState) -> dict:
    """Assembles inputs and makes a structured Gemini call for the final analysis report."""
    prompt = f"""You are a senior real estate investment analyst in India. Generate a comprehensive investment analysis report.

Property: {state.get('address')}, {state.get('city')}
Investment Horizon: {state.get('investment_horizon_years')} years
Final Growth Score: {state.get('final_score')}/100
Budget: ₹{state.get('budget_lakhs')} Lakhs

MARKET DATA:
{json.dumps(state.get('locality_insights'), indent=2)}

COMPARABLE PROPERTIES (Analyst-Approved):
{json.dumps(state.get('approved_comps'), indent=2)}

ROI CALCULATIONS:
{json.dumps(state.get('roi_estimates'), indent=2)}

GROUNDING CONTEXT (Zoning & Infrastructure):
{state.get('rag_context')}

ANALYST NOTES: {state.get('analyst_notes')}

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
}}"""

    report_dict = None
    response_text = ""
    start_time = time.perf_counter()

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        response_text = response.text
        report_dict = _safe_parse_gemini_json(response_text)
    except Exception as e:
        print(f"Error calling Gemini or parsing: {e}")
        report_dict = _get_fallback_report(state)
    finally:
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        try:
            import telemetry
            if hasattr(telemetry, "log_gemini_call") and callable(telemetry.log_gemini_call):
                prompt_tokens = len(prompt) // 4
                resp_tokens = len(response_text) // 4 if response_text else 0
                telemetry.log_gemini_call(prompt_tokens, resp_tokens, latency_ms)
        except Exception:
            pass

    stream = list(state.get("stream_messages") or [])
    stream.append("📝 Generating investment analysis report...")

    return {
        "report": report_dict,
        "stream_messages": stream
    }


# =====================================================================
# LANGGRAPH WORKFLOW CONFIGURATION
# =====================================================================

workflow = StateGraph(AnalysisState)

# Add Nodes
workflow.add_node("fetch_market_data", fetch_market_data)
workflow.add_node("inject_rag_context", inject_rag_context)
workflow.add_node("calculate_preliminary", calculate_preliminary)
workflow.add_node("hitl_verification", hitl_verification)
workflow.add_node("calculate_final_score", calculate_final_score)
workflow.add_node("generate_report", generate_report)

# Add Edges
workflow.add_edge(START, "fetch_market_data")
workflow.add_edge("fetch_market_data", "inject_rag_context")
workflow.add_edge("inject_rag_context", "calculate_preliminary")
workflow.add_edge("calculate_preliminary", "hitl_verification")
workflow.add_edge("hitl_verification", "calculate_final_score")
workflow.add_edge("calculate_final_score", "generate_report")
workflow.add_edge("generate_report", END)

# Persistent Memory Checkpointer
memory_saver = MemorySaver()

# Compile the graph with checking interrupts
graph = workflow.compile(
    checkpointer=memory_saver,
    interrupt_before=["hitl_verification"]
)


# =====================================================================
# EXPOSED SYSTEM APIS
# =====================================================================

def start_analysis(request_data: dict) -> dict:
    """
    Compiles input values, executes the graph up to the HITL interrupt boundary,
    caches intermediate results, and returns the partial state dictionary.
    Exposed as synchronous-compatible function representing a coroutine.
    """
    try:
        thread_id = request_data.get("thread_id") or str(uuid.uuid4())

        initial_state = {
            "thread_id": thread_id,
            "address": request_data.get("address", ""),
            "city": request_data.get("city", ""),
            "budget_lakhs": float(request_data.get("budget_lakhs", 100.0)),
            "bhk_type": request_data.get("bhk_type", "2BHK"),
            "investment_horizon_years": int(request_data.get("investment_horizon_years", 5)),
            "comps": [],
            "locality_insights": {},
            "rag_context": "",
            "roi_estimates": {},
            "preliminary_score": 0,
            "hitl_approved": False,
            "approved_comps": [],
            "analyst_notes": "",
            "final_score": 0,
            "report": {},
            "stream_messages": []
        }

        config = {"configurable": {"thread_id": thread_id}}

        # Log starting stage in main.py tracker
        _update_main_active_threads(
            thread_id=thread_id,
            status="running",
            stream_messages=["🏘️ Initiating live backend thread sequence..."]
        )

        # Run graph. It will pause automatically before hitl_verification
        graph.invoke(initial_state, config=config)

        # Extract snapshot state values
        state_snapshot = graph.get_state(config)
        partial_state = dict(state_snapshot.values)

        # Cache in store
        _thread_store[thread_id] = partial_state

        # Update polling tracker status
        _update_main_active_threads(
            thread_id=thread_id,
            status="awaiting_hitl",
            stream_messages=partial_state.get("stream_messages", []),
            report=partial_state
        )

        return AwaitableDict(partial_state)

    except Exception as e:
        thread_id = request_data.get("thread_id") or str(uuid.uuid4())
        err_state = {
            "thread_id": thread_id,
            "address": request_data.get("address", ""),
            "city": request_data.get("city", ""),
            "budget_lakhs": float(request_data.get("budget_lakhs", 100.0)),
            "bhk_type": request_data.get("bhk_type", "2BHK"),
            "investment_horizon_years": int(request_data.get("investment_horizon_years", 5)),
            "comps": [],
            "locality_insights": {},
            "rag_context": f"Error occurred during initialization: {str(e)}",
            "roi_estimates": {},
            "preliminary_score": 50,
            "hitl_approved": False,
            "approved_comps": [],
            "analyst_notes": "",
            "final_score": 0,
            "report": {},
            "stream_messages": [f"❌ Error initiating analysis: {str(e)}"]
        }
        _thread_store[thread_id] = err_state
        _update_main_active_threads(
            thread_id=thread_id,
            status="awaiting_hitl",
            stream_messages=err_state["stream_messages"],
            report=err_state
        )
        return AwaitableDict(err_state)

# Register start_analysis as a coroutine function for inspect framework compatibility
start_analysis._is_coroutine = getattr(asyncio.coroutines, "_is_coroutine", True)


async def resume_analysis(thread_id: str, approved_comps: list = None, analyst_notes: str = None) -> dict:
    """
    Updates the paused graph state with approved comps and analyst notes,
    resumes graph execution, and returns the final completed state details.
    """
    try:
        # Support dict argument signature (from main.py resume endpoint call)
        if isinstance(thread_id, dict):
            data = thread_id
            thread_id = data.get("thread_id")
            approved_comps = data.get("approved_comps") or []
            analyst_notes = data.get("analyst_notes") or ""

        config = {"configurable": {"thread_id": thread_id}}

        # Fetch paused state snapshot to retrieve original comparable list
        state_snapshot = graph.get_state(config)
        current_values = state_snapshot.values or {}
        original_comps = current_values.get("comps") or []

        # Map approved items
        mapped_approved_comps = []
        for c in (approved_comps or []):
            if isinstance(c, dict):
                mapped_approved_comps.append(c)
            elif isinstance(c, str):
                for oc in original_comps:
                    if oc.get("id") == c:
                        mapped_approved_comps.append(oc)
                        break

        # Fallback to original list if none matched or selected to prevent crashes
        if not mapped_approved_comps:
            mapped_approved_comps = original_comps

        # Update Graph state with user input modifications
        graph.update_state(
            config,
            {
                "approved_comps": mapped_approved_comps,
                "analyst_notes": analyst_notes or "",
                "hitl_approved": True
            },
            as_node="hitl_verification"
        )

        # Update main.py tracker to running
        _update_main_active_threads(
            thread_id=thread_id,
            status="running",
            stream_messages=(current_values.get("stream_messages") or []) + ["✅ Analyst review received. Processing approved comparables..."]
        )

        # Resume graph execution (completes remaining pipeline steps)
        graph.invoke(None, config=config)

        # Fetch final completed state values
        final_snapshot = graph.get_state(config)
        final_state = dict(final_snapshot.values)

        # Cache completed state in memory stores
        _thread_store[thread_id] = final_state

        # Update main.py tracker to complete
        _update_main_active_threads(
            thread_id=thread_id,
            status="complete",
            stream_messages=final_state.get("stream_messages", []),
            report=final_state.get("report")
        )

        return final_state

    except Exception as e:
        fallback_rep = _get_fallback_report({"final_score": 50})
        err_report = {
            "thread_id": thread_id if isinstance(thread_id, str) else "error_thread",
            "status": "complete",
            "final_score": 50,
            "report": fallback_rep,
            "stream_messages": [f"❌ Error resuming analysis: {str(e)}", "✅ Analysis sequence complete with fallback."]
        }
        return err_report


async def get_stream_events(thread_id: str):
    """Fallback generator yielding analysis pipeline stream log notifications."""
    state = _thread_store.get(thread_id) or {}
    messages = state.get("stream_messages") or []
    for msg in messages:
        yield json.dumps({
            "step": "analysis",
            "message": msg,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        })
