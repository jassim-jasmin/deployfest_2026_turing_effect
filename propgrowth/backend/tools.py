import os
import json
import time
import hashlib
import random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def _log_telemetry_if_exists(tool_name: str, inputs: dict, output_summary: str, start_time: float):
    """
    Checks if a telemetry hook exists and logs the tool call details.
    Catches all exceptions to ensure telemetry failures never block tool execution.
    """
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    try:
        import telemetry
        if hasattr(telemetry, "log_tool_call") and callable(telemetry.log_tool_call):
            telemetry.log_tool_call(
                tool=tool_name,
                inputs=inputs,
                output_summary=output_summary,
                latency_ms=latency_ms
            )
    except Exception:
        pass

def search_properties(location: str, budget_min: float, budget_max: float, bhk_type: str) -> list:
    """
    Searches properties matching the location keywords, and formats the output comps.
    Falls back gracefully to standard entries to return exactly 4 comps.
    """
    start_time = time.perf_counter()
    comps_file = os.path.join(CURRENT_DIR, "data", "synthetic_comps.json")
    
    # Load all comps
    try:
        with open(comps_file, "r") as f:
            data = json.load(f)
            comps_list = data.get("comps", [])
    except Exception:
        comps_list = []

    # Filter by location keyword (case-insensitive)
    loc_lower = location.lower().strip() if location else ""
    matched_comps = []
    
    if loc_lower:
        for c in comps_list:
            locality = c.get("locality", "").lower()
            city = c.get("city", "").lower()
            if loc_lower in locality or loc_lower in city or locality in loc_lower or city in loc_lower:
                matched_comps.append(c)

    # Score matches to prioritize matching BHK and budget
    def score_comp(c):
        score = 0
        if bhk_type and c.get("bhk_type") == bhk_type:
            score += 10
        price = c.get("price_lakhs", 0)
        if budget_min <= price <= budget_max:
            score += 5
        elif price > 0:
            # close to budget range
            dist = min(abs(price - budget_min), abs(price - budget_max))
            score += max(0, 5 - (dist / price) * 10)
        return score

    if matched_comps:
        matched_comps.sort(key=score_comp, reverse=True)

    # Helper to map comp keys to requested schema
    def map_comp(c):
        return {
            "id": c.get("id", "COMP_UNKNOWN"),
            "title": c.get("title", "Standard Property"),
            "location": f"{c.get('locality', 'Unknown Locality')}, {c.get('city', 'Unknown City')}",
            "price": float(c.get("price_lakhs", 0.0)),
            "bhk": c.get("bhk_type", "2BHK"),
            "area_sqft": int(c.get("area_sqft", 1000)),
            "price_per_sqft": float(c.get("price_per_sqft", 0.0)),
            "monthly_rent": float(c.get("monthly_rent", 0.0)),
            "listing_age_days": int(c.get("listing_age_days", 30)),
            "distance_km": float(c.get("distance_from_city_center_km", c.get("metro_distance_km", 0.0))),
            "nearby_metro": bool(c.get("nearby_metro", False)),
            "source": c.get("source", "PropGrowth")
        }

    results = []
    for c in matched_comps[:4]:
        results.append(map_comp(c))

    # Fallback to standard entries if we don't have exactly 4 comps
    if len(results) < 4:
        fallback_candidates = [c for c in comps_list if c not in matched_comps]
        # Sort fallback candidates by best match on bhk and budget
        fallback_candidates.sort(key=score_comp, reverse=True)
        for c in fallback_candidates:
            if len(results) >= 4:
                break
            results.append(map_comp(c))
            
    # If still less than 4, pad with dummy objects (extremely unlikely but safe)
    while len(results) < 4:
        results.append({
            "id": f"COMP_FALLBACK_{len(results)}",
            "title": "Standard Fallback Comp",
            "location": "Outskirts, City",
            "price": float(budget_min + budget_max) / 2.0 if budget_min and budget_max else 50.0,
            "bhk": bhk_type if bhk_type else "2BHK",
            "area_sqft": 1000,
            "price_per_sqft": 5000.0,
            "monthly_rent": 15000.0,
            "listing_age_days": 15,
            "distance_km": 5.0,
            "nearby_metro": False,
            "source": "PropGrowth"
        })

    # Prepare inputs dictionary for logging
    inputs = {
        "location": location,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "bhk_type": bhk_type
    }
    avg_price = sum(r["price"] for r in results) / len(results) if results else 0.0
    output_summary = f"{len(results)} comps returned, avg price {avg_price:.1f}L"
    
    _log_telemetry_if_exists("search_properties", inputs, output_summary, start_time)
    
    return results

def calculate_roi(price_lakhs: float, monthly_rent: float, appreciation_rate_pct: float) -> dict:
    """
    Calculates primary investment metrics and blends results with matching scenario in synthetic_roi_scenarios.json.
    """
    start_time = time.perf_counter()
    
    # Core mathematical calculations
    price_val = price_lakhs * 100000.0
    rental_yield_pct = (monthly_rent * 12) / price_val * 100 if price_val > 0 else 0.0
    break_even_years = round(price_val / (monthly_rent * 12), 1) if monthly_rent > 0 else 99.9
    projected_10yr_value_lakhs = price_lakhs * ((1 + appreciation_rate_pct / 100.0) ** 10)
    total_10yr_return_pct = ((projected_10yr_value_lakhs - price_lakhs) / price_lakhs) * 100 if price_lakhs > 0 else 0.0
    
    # Assumed 70% LTV EMI logic: 70% of price is loan, 8.67% is EMI factor or monthly payment rate
    # emi = Loan * interest_rate_factor, here formula matches the prompt: price_lakhs * 100000 * 0.7 * 0.00867
    monthly_cashflow = monthly_rent - (price_val * 0.7 * 0.00867)

    # Scans ROI scenarios for blending
    scenarios_file = os.path.join(CURRENT_DIR, "data", "synthetic_roi_scenarios.json")
    matched_scenario = None
    
    try:
        with open(scenarios_file, "r") as f:
            data = json.load(f)
            scenarios = data.get("roi_scenarios", [])
    except Exception:
        scenarios = []

    # Find the closest match based on price and rent
    best_dist = 999.0
    for sc in scenarios:
        sc_price = sc.get("purchase_price_lakhs", 0.0)
        sc_rent = sc.get("monthly_rent_current", 0.0)
        if sc_price > 0 and sc_rent > 0:
            price_dist = abs(sc_price - price_lakhs) / price_lakhs
            rent_dist = abs(sc_rent - monthly_rent) / monthly_rent
            total_dist = price_dist + rent_dist
            # Match is valid if within 15% tolerance
            if price_dist < 0.15 and rent_dist < 0.15 and total_dist < best_dist:
                best_dist = total_dist
                matched_scenario = sc

    # Set up initial return dictionary
    res = {
        "rental_yield_pct": float(rental_yield_pct),
        "break_even_years": float(break_even_years),
        "projected_10yr_value_lakhs": float(projected_10yr_value_lakhs),
        "total_10yr_return_pct": float(total_10yr_return_pct),
        "monthly_cashflow": float(monthly_cashflow),
        "investment_verdict": "BUY" if rental_yield_pct >= 4.0 else "HOLD",
        "verdict_reason": "Solid fundamentals with steady projected yields."
    }

    # Blend cleanly with matched scenario if found
    if matched_scenario:
        sc_ret = matched_scenario.get("calculated_returns", {})
        
        # Weighted average blend (50% math, 50% scenario report)
        res["rental_yield_pct"] = round(0.5 * rental_yield_pct + 0.5 * sc_ret.get("rental_yield_gross_pct", rental_yield_pct), 2)
        res["break_even_years"] = round(0.5 * break_even_years + 0.5 * sc_ret.get("break_even_years", break_even_years), 1)
        res["projected_10yr_value_lakhs"] = round(0.5 * projected_10yr_value_lakhs + 0.5 * sc_ret.get("value_at_10yr_lakhs", projected_10yr_value_lakhs), 2)
        res["total_10yr_return_pct"] = round(0.5 * total_10yr_return_pct + 0.5 * sc_ret.get("total_return_10yr_pct", total_10yr_return_pct), 2)
        res["monthly_cashflow"] = round(0.5 * monthly_cashflow + 0.5 * sc_ret.get("monthly_cashflow_amount", monthly_cashflow), 2)
        
        # Inject scenario qualitative tags
        res["scenario_id"] = matched_scenario.get("scenario_id")
        res["investment_verdict"] = matched_scenario.get("investment_verdict", res["investment_verdict"])
        res["verdict_reason"] = matched_scenario.get("verdict_reason", res["verdict_reason"])
        res["irr_10yr_pct"] = float(sc_ret.get("irr_10yr_pct", 0.0))
        res["best_exit_horizon_years"] = int(sc_ret.get("best_exit_horizon_years", 5))

    inputs = {
        "price_lakhs": price_lakhs,
        "monthly_rent": monthly_rent,
        "appreciation_rate_pct": appreciation_rate_pct
    }
    output_summary = f"rental_yield: {res['rental_yield_pct']:.2f}%, 10yr_value: {res['projected_10yr_value_lakhs']:.1f}L"
    
    _log_telemetry_if_exists("calculate_roi", inputs, output_summary, start_time)

    return res

def get_locality_insights(locality: str, city: str) -> dict:
    """
    Retrieves infrastructure, demand, and risk parameters for a locality.
    Generates a deterministic seed string to stably map values for novel locations.
    """
    start_time = time.perf_counter()
    insights_file = os.path.join(CURRENT_DIR, "data", "synthetic_locality_insights.json")
    
    # Load locality insights database
    try:
        with open(insights_file, "r") as f:
            data = json.load(f)
            insights_list = data.get("locality_insights", [])
    except Exception:
        insights_list = []

    # Search for matching locality and city (case-insensitive)
    target_entry = None
    loc_clean = locality.strip().lower() if locality else ""
    city_clean = city.strip().lower() if city else ""

    for item in insights_list:
        if item.get("locality", "").strip().lower() == loc_clean and item.get("city", "").strip().lower() == city_clean:
            target_entry = item
            break

    # If found, map the fields precisely
    if target_entry:
        res = {
            "infrastructure_score": int(target_entry.get("infrastructure_score", 50)),
            "demand_index": int(target_entry.get("demand_index", 50)),
            "population_growth_pct": float(target_entry.get("population_growth_3yr_cagr_pct", 0.0)),
            "avg_price_trend_pct": float(target_entry.get("avg_price_trend_yoy_pct", 0.0)),
            "top_employers_nearby": list(target_entry.get("top_employers_nearby", []))[:3],
            "connectivity_rating": target_entry.get("connectivity_rating", "Average"),
            "flood_risk": target_entry.get("flood_risk", "Low"),
            "social_infrastructure": dict(target_entry.get("social_infrastructure", {
                "schools_within_3km": 0,
                "hospitals_within_3km": 0,
                "malls_within_5km": 0,
                "parks": 0
            }))
        }
    else:
        # Generate stable, deterministic seed from locality + city
        combined_str = f"{loc_clean}|{city_clean}"
        md5_hash = hashlib.md5(combined_str.encode('utf-8')).hexdigest()
        seed_int = int(md5_hash, 16) & 0xFFFFFFFF
        
        # Local random generator to avoid polluting global random state
        rng = random.Random(seed_int)
        
        employers_pool = [
            "Google", "Microsoft", "Amazon", "Infosys", "TCS", 
            "Cognizant", "Wipro", "Accenture", "Persistent Systems"
        ]
        
        res = {
            "infrastructure_score": rng.randint(45, 95),
            "demand_index": rng.randint(40, 98),
            "population_growth_pct": round(rng.uniform(1.5, 8.5), 1),
            "avg_price_trend_pct": round(rng.uniform(2.5, 14.5), 1),
            "top_employers_nearby": rng.sample(employers_pool, min(3, len(employers_pool))),
            "connectivity_rating": rng.choice(["Poor", "Average", "Good", "Excellent"]),
            "flood_risk": rng.choice(["Low", "Medium", "High"]),
            "social_infrastructure": {
                "schools_within_3km": rng.randint(2, 12),
                "hospitals_within_3km": rng.randint(1, 8),
                "malls_within_5km": rng.randint(0, 5),
                "parks": rng.randint(1, 10)
            }
        }

    inputs = {
        "locality": locality,
        "city": city
    }
    output_summary = f"infrastructure_score: {res['infrastructure_score']}, demand_index: {res['demand_index']}"
    
    _log_telemetry_if_exists("get_locality_insights", inputs, output_summary, start_time)

    return res
