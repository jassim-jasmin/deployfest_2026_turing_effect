import sys
import os
import asyncio

# Add backend directory to sys.path to enable local imports during test run
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "propgrowth", "backend")
sys.path.insert(0, backend_dir)

from rag import initialize_rag
from agent import start_analysis, resume_analysis

# Mock active_threads inside main.py since the agent updates main.active_threads
import main
main.active_threads = {}

async def test_pipeline():
    print("--- 1. Initializing RAG ---")
    initialize_rag()
    print("RAG Initialized successfully.\n")

    print("--- 2. Starting Analysis (Sync check) ---")
    request_data = {
        "address": "Hinjewadi Phase 2",
        "city": "Pune",
        "budget_lakhs": 80.0,
        "bhk_type": "2BHK",
        "investment_horizon_years": 5
    }

    # Call start_analysis synchronously as main.py does
    start_res = start_analysis(request_data)
    print("Start Result Type:", type(start_res))
    print("Is instance of dict:", isinstance(start_res, dict))
    print("Keys returned:", list(start_res.keys()))
    print("Thread ID:", start_res.get("thread_id"))
    print("Preliminary Score:", start_res.get("preliminary_score"))
    print("Comparable count fetched:", len(start_res.get("comps", [])))
    print("Stream Messages:")
    for msg in start_res.get("stream_messages", []):
        print(f"  - {msg}")
    print()

    thread_id = start_res.get("thread_id")
    comps = start_res.get("comps", [])
    approved_ids = [c["id"] for c in comps[:2]]  # Approve first 2 comps

    print("--- 3. Resuming Analysis (Async check) ---")
    # Call resume_analysis asynchronously
    resume_res = await resume_analysis(
        thread_id=thread_id,
        approved_comps=approved_ids,
        analyst_notes="Market indicators look bullish for this micro-market, solid IT growth."
    )

    print("Resume Result Type:", type(resume_res))
    print("Final Score:", resume_res.get("final_score"))
    print("Final Approved comps count:", len(resume_res.get("approved_comps", [])))
    print("Final Report Keys:", list(resume_res.get("report", {}).keys()) if resume_res.get("report") else "None")
    print("Final Report Growth Verdict:", resume_res.get("report", {}).get("growth_verdict"))
    print("Final Stream Messages:")
    for msg in resume_res.get("stream_messages", []):
        print(f"  - {msg}")
    
    print("\n--- 4. Polling Status Registry Check ---")
    print("main.active_threads keys:", list(main.active_threads.keys()))
    if thread_id in main.active_threads:
        print("Thread status in main:", main.active_threads[thread_id]["status"])
        print("Thread final report verdict in main:", main.active_threads[thread_id]["report"].get("report", {}).get("growth_verdict"))

if __name__ == "__main__":
    asyncio.run(test_pipeline())
