import os
import sys
import unittest
import uuid
from fastapi.testclient import TestClient

# Ensure the backend directory is in the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tools import search_properties, calculate_roi, get_locality_insights
from rag import initialize_rag, query_rag_context
from main import app


class TestTools(unittest.TestCase):
    def test_search_properties_known_city(self):
        # Test searching in Pune
        results = search_properties(location="Hinjewadi", budget_min=50.0, budget_max=100.0, bhk_type="2BHK")
        self.assertEqual(len(results), 4)
        for r in results:
            self.assertIn("id", r)
            self.assertIn("title", r)
            self.assertIn("location", r)
            self.assertIn("price", r)
            self.assertIn("bhk", r)
            self.assertIn("monthly_rent", r)

    def test_search_properties_unknown(self):
        # Test searching in an unknown location (should fall back to standard entries)
        results = search_properties(location="RandomPlaceName123", budget_min=50.0, budget_max=100.0, bhk_type="2BHK")
        self.assertEqual(len(results), 4)

    def test_calculate_roi(self):
        # Test ROI mathematical execution and blending
        roi = calculate_roi(price_lakhs=100.0, monthly_rent=25000.0, appreciation_rate_pct=8.0)
        self.assertIn("rental_yield_pct", roi)
        self.assertIn("break_even_years", roi)
        self.assertIn("projected_10yr_value_lakhs", roi)
        self.assertIn("total_10yr_return_pct", roi)
        self.assertIn("monthly_cashflow", roi)
        self.assertGreater(roi["rental_yield_pct"], 0)

    def test_get_locality_insights_known(self):
        # Test overridden/known locality
        insights = get_locality_insights(locality="Hinjewadi", city="Pune")
        self.assertIn("infrastructure_score", insights)
        self.assertIn("demand_index", insights)
        self.assertIn("avg_price_trend_pct", insights)
        self.assertIn("top_employers_nearby", insights)
        self.assertEqual(len(insights["top_employers_nearby"]), 3)

    def test_get_locality_insights_unknown(self):
        # Test unknown locality falling back to deterministic seed logic
        insights = get_locality_insights(locality="Nandoshi Village", city="Pune")
        self.assertIn("infrastructure_score", insights)
        self.assertIn("demand_index", insights)
        self.assertIn("avg_price_trend_pct", insights)
        self.assertIn("top_employers_nearby", insights)
        self.assertEqual(len(insights["top_employers_nearby"]), 3)


class TestRAG(unittest.TestCase):
    def test_rag_flow(self):
        # Initialize RAG and run query to ensure ChromaDB grounding context resolves
        initialize_rag()
        context = query_rag_context("infrastructure zoning development Pune")
        self.assertIsNotNone(context)
        self.assertTrue(isinstance(context, str))
        self.assertTrue("GROUNDING CONTEXT" in context or "No specific zoning" in context)


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "version": "1.0.0"})

    def test_telemetry(self):
        response = self.client.get("/api/telemetry")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue("mock_traces" in data or "traces" in data)

    def test_analysis_workflow_fallback(self):
        # 1. Start Analysis
        payload = {
            "address": "Hinjewadi Phase 2",
            "city": "Pune",
            "budget_lakhs": 85.0,
            "bhk_type": "2BHK",
            "investment_horizon_years": 5
        }
        response = self.client.post("/api/analyze/start", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("thread_id", data)
        self.assertEqual(data["status"], "awaiting_hitl")
        
        thread_id = data["thread_id"]
        report = data["preliminary_report"]
        self.assertIn("comps", report)
        self.assertIn("locality_insights", report)
        self.assertIn("roi_metrics", report)
        self.assertIn("rag_context", report)
        
        # 2. Get status polling (verify we are awaiting HITL)
        status_response = self.client.get(f"/api/analyze/status/{thread_id}")
        self.assertEqual(status_response.status_code, 200)
        status_data = status_response.json()
        self.assertEqual(status_data["status"], "awaiting_hitl")
        self.assertIn("stream_messages", status_data)
        
        # 3. Resume/Complete Analysis
        comps_ids = [c["id"] for c in report["comps"]]
        resume_payload = {
            "thread_id": thread_id,
            "approved_comps": comps_ids[:2],  # Approve first two comps
            "analyst_notes": "Strong buy opportunity due to proximity to Hinjewadi IT parks."
        }
        resume_response = self.client.post("/api/analyze/resume", json=resume_payload)
        self.assertEqual(resume_response.status_code, 200)
        final_report = resume_response.json()
        self.assertEqual(final_report["status"], "complete")
        self.assertIn("verdict", final_report)
        self.assertIn("scores", final_report)
        self.assertIsNotNone(final_report["scores"]["final_score"])
        
        # 4. Verify status is complete after resuming
        status_response = self.client.get(f"/api/analyze/status/{thread_id}")
        self.assertEqual(status_response.status_code, 200)
        status_data = status_response.json()
        self.assertEqual(status_data["status"], "complete")


if __name__ == "__main__":
    unittest.main()
