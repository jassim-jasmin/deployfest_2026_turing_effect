"""
PropGrowth AI — Synthetic Dataset Generator
============================================
Generates all synthetic datasets programmatically (pure Python, no LLM).
Only master_plans.txt uses Gemini API.

Usage:
    pip install google-generativeai
    GEMINI_API_KEY=your_key python generate_synthetic_data.py

Outputs (written to ./backend/data/):
    synthetic_comps.json
    synthetic_locality_insights.json
    synthetic_roi_scenarios.json
    hitl_test_scenarios.json
    edge_cases.json
    mock_telemetry_traces.json
    master_plans.txt  <-- Gemini only
"""

import json
import os
import random
import hashlib
import uuid
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── output directory ──────────────────────────────────────────────────────────
OUT_DIR = Path("backend/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)   # reproducible output

# =============================================================================
# SHARED REFERENCE DATA
# =============================================================================

CITIES = {
    "Pune": {
        "localities": ["Hinjewadi", "Wakad", "Baner", "Kothrud", "Hadapsar", "Viman Nagar", "Nibm Road"],
        "price_min": 60, "price_max": 180,
        "appreciation_min": 15, "appreciation_max": 28,
        "rent_multiplier": 0.32,         # monthly_rent = price_lakhs * multiplier * 1000
        "metro": ["Hinjewadi", "Wakad", "Baner"],
    },
    "Bangalore": {
        "localities": ["Whitefield", "Electronic City", "Sarjapur Road", "HSR Layout", "Koramangala", "Yelahanka"],
        "price_min": 70, "price_max": 220,
        "appreciation_min": 18, "appreciation_max": 32,
        "rent_multiplier": 0.36,
        "metro": ["Whitefield", "Koramangala", "HSR Layout"],
    },
    "Mumbai": {
        "localities": ["Thane West", "Navi Mumbai", "Andheri East", "Powai", "Mira Road", "Kharghar"],
        "price_min": 90, "price_max": 350,
        "appreciation_min": 10, "appreciation_max": 18,
        "rent_multiplier": 0.42,
        "metro": ["Andheri East", "Powai"],
    },
    "Hyderabad": {
        "localities": ["Gachibowli", "HITEC City", "Kondapur", "Manikonda", "Narsingi", "Miyapur"],
        "price_min": 55, "price_max": 160,
        "appreciation_min": 20, "appreciation_max": 35,
        "rent_multiplier": 0.38,
        "metro": ["HITEC City", "Miyapur", "Kondapur"],
    },
    "Noida": {
        "localities": ["Sector 62", "Sector 137", "Greater Noida West", "Sector 150", "Expressway"],
        "price_min": 50, "price_max": 130,
        "appreciation_min": 12, "appreciation_max": 22,
        "rent_multiplier": 0.28,
        "metro": ["Sector 62", "Sector 137"],
    },
    "Chennai": {
        "localities": ["OMR", "Perambur", "Velachery", "Sholinganallur", "Medavakkam", "Anna Nagar"],
        "price_min": 55, "price_max": 150,
        "appreciation_min": 10, "appreciation_max": 20,
        "rent_multiplier": 0.30,
        "metro": ["Anna Nagar", "Velachery"],
    },
}

BUILDERS = [
    "Prestige Estates", "Brigade Group", "Sobha Limited", "Godrej Properties",
    "Lodha Group", "DLF Limited", "Puravankara", "Mahindra Lifespaces",
    "Kolte-Patil", "Shapoorji Pallonji", "Embassy Group", "Tata Housing",
    "Merlin Group", "Phoenix Mills", "Oberoi Realty",
]

AMENITIES_POOL = [
    "Gymnasium", "Swimming Pool", "Clubhouse", "24x7 Security",
    "Power Backup", "Landscaped Gardens", "Children Play Area",
    "Badminton Court", "Jogging Track", "Intercom", "Car Wash Area",
    "Indoor Games Room", "Yoga Deck", "Senior Citizen Corner",
]

EMPLOYERS = {
    "Pune":      ["Infosys", "Wipro", "TCS", "Persistent Systems", "Cognizant", "Bajaj Auto"],
    "Bangalore": ["Infosys", "Wipro", "Accenture", "IBM", "Amazon", "Flipkart"],
    "Mumbai":    ["HDFC Bank", "Reliance", "TCS", "JP Morgan", "Deutsche Bank"],
    "Hyderabad": ["Microsoft", "Google", "Amazon", "Cognizant", "Tech Mahindra"],
    "Noida":     ["HCL Technologies", "Infosys", "Samsung", "Adobe", "Sapient"],
    "Chennai":   ["TCS", "Cognizant", "Hyundai", "Ford", "Amazon"],
}

FURNISHING = ["Unfurnished", "Semi-Furnished", "Fully Furnished"]
BHK_TYPES  = ["1BHK", "2BHK", "2BHK", "3BHK", "3BHK", "4BHK+"]   # weighted towards 2/3

SOURCES = ["MagicBricks", "99acres", "Housing.com", "NoBroker", "Square Yards"]


def _seed(text: str) -> random.Random:
    """Return a seeded Random instance from a string — ensures determinism per locality."""
    h = int(hashlib.md5(text.encode()).hexdigest(), 16)
    r = random.Random(h)
    return r


def _emi(principal_lakhs: float, rate_annual_pct: float, tenure_years: int) -> int:
    p = principal_lakhs * 100_000
    r = rate_annual_pct / 12 / 100
    n = tenure_years * 12
    if r == 0:
        return int(p / n)
    emi = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return int(emi)


def _project_name(builder: str, locality: str) -> str:
    suffixes = ["Infinity", "Grandeur", "Serenity", "Heights", "Vista",
                "Greens", "Enclave", "Residency", "Park", "Square"]
    r = _seed(builder + locality)
    return f"{builder.split()[0]} {r.choice(suffixes)}"


# =============================================================================
# 1. COMPARABLE PROPERTIES  →  synthetic_comps.json
# =============================================================================

def generate_comps() -> dict:
    comps = []
    idx = 1

    for city, cfg in CITIES.items():
        count = 7 if city in ("Pune", "Bangalore") else 6
        for locality in cfg["localities"][:count]:
            r = _seed(city + locality + str(idx))

            bhk       = r.choice(BHK_TYPES)
            price     = round(r.uniform(cfg["price_min"], cfg["price_max"]), 1)
            area      = r.randint(650, 1800)
            psf       = round(price * 100_000 / area)
            rent      = int(price * cfg["rent_multiplier"] * 1000)
            near_metro = locality in cfg["metro"]
            builder   = r.choice(BUILDERS)
            appre     = round(r.uniform(cfg["appreciation_min"], cfg["appreciation_max"]), 1)
            amenities = r.sample(AMENITIES_POOL, k=r.randint(4, 7))

            comps.append({
                "id":                    f"COMP_{idx:03d}",
                "city":                  city,
                "locality":              locality,
                "title":                 f"Spacious {bhk} in {locality}",
                "bhk_type":              bhk,
                "price_lakhs":           price,
                "area_sqft":             area,
                "price_per_sqft":        psf,
                "monthly_rent":          rent,
                "listing_age_days":      r.randint(2, 90),
                "floor":                 f"{r.randint(2,28)}th of {r.randint(15,35)}",
                "age_of_property_years": r.randint(0, 10),
                "furnishing":            r.choice(FURNISHING),
                "parking":               r.random() > 0.15,
                "nearby_metro":          near_metro,
                "metro_distance_km":     round(r.uniform(0.2, 0.7), 1) if near_metro else round(r.uniform(1.5, 4.5), 1),
                "distance_from_city_center_km": round(r.uniform(4, 25), 1),
                "builder":               builder,
                "project_name":          _project_name(builder, locality),
                "amenities":             amenities,
                "appreciation_last_3yr_pct": appre,
                "demand_score":          r.randint(55, 95),
                "source":                r.choice(SOURCES),
                "verified":              r.random() > 0.25,
            })
            idx += 1

    return {"comps": comps}


# =============================================================================
# 2. LOCALITY INSIGHTS  →  synthetic_locality_insights.json
# =============================================================================

CONNECTIVITY = ["Excellent", "Good", "Average", "Poor"]
FLOOD_RISK   = ["Low", "Low", "Low", "Medium", "High"]
AQI          = ["Good", "Moderate", "Moderate", "Poor"]
PRICE_SEGMENT = ["Affordable", "Mid-Range", "Mid-Premium", "Premium", "Luxury"]

METRO_LINES = {
    "Hinjewadi":       "Pune Metro Line 3 (Upcoming 2027)",
    "Wakad":           "Pune Metro Line 3 Extension (2028)",
    "Baner":           "Pune Metro Line 3 (Upcoming 2027)",
    "Whitefield":      "Namma Metro Purple Line (Operational)",
    "Koramangala":     "Namma Metro Green Line (2026)",
    "HSR Layout":      "Namma Metro Green Line (2026)",
    "HITEC City":      "Hyderabad Metro Red Line (Operational)",
    "Miyapur":         "Hyderabad Metro Red Line (Operational)",
    "Kondapur":        "Hyderabad Metro Red Line (Operational)",
    "Andheri East":    "Mumbai Metro Line 1 (Operational)",
    "Powai":           "Mumbai Metro Line 6 (2026)",
    "Anna Nagar":      "Chennai Metro Phase 2 (2026)",
    "Velachery":       "Chennai Metro Green Line (Operational)",
    "Sector 62":       "Delhi Metro Blue Line Extension (Operational)",
    "Sector 137":      "Delhi Metro Aqua Line (Operational)",
}

SUMMARIES = {
    "Hinjewadi":       "Prime IT corridor driven by Rajiv Gandhi Infotech Park. Strong rental demand, Metro Line 3 a major 2027 catalyst.",
    "Wakad":           "Emerging residential hub near Hinjewadi IT Park with rapid infrastructure growth.",
    "Baner":           "Premium residential zone with excellent social infrastructure and proximity to IT hubs.",
    "Kothrud":         "Established residential area with strong end-user demand and good connectivity.",
    "Hadapsar":        "Growing IT and industrial hub with significant affordable housing supply.",
    "Viman Nagar":     "Near Pune airport, premium locality with consistent appreciation.",
    "Nibm Road":       "Developing residential corridor in South Pune with good value proposition.",
    "Whitefield":      "Bangalore's largest IT corridor, high rental yields, Metro now operational.",
    "Electronic City": "Massive IT cluster housing Infosys, Wipro campuses. Affordable entry point.",
    "Sarjapur Road":   "Fast growing corridor connecting Electronic City and Whitefield IT hubs.",
    "HSR Layout":      "Premium locality with strong startup ecosystem and high-quality social infra.",
    "Koramangala":     "Bangalore's most coveted address. Highest rental yields in the city.",
    "Yelahanka":       "North Bangalore emerging zone near new Bangalore Airport road.",
    "Thane West":      "MMR's fastest growing node. Excellent rail connectivity to Mumbai.",
    "Navi Mumbai":     "Planned township with excellent infrastructure. Airport project a key catalyst.",
    "Andheri East":    "Commercial hub, Metro operational, strong rental market.",
    "Powai":           "Premium lake-view locality near IIT Bombay, strong NRI demand.",
    "Mira Road":       "Affordable Mumbai suburb with improving connectivity.",
    "Kharghar":        "Navi Mumbai planned node with good infrastructure and affordability.",
    "Gachibowli":      "Hyderabad's financial district. Fastest appreciating micro-market in India.",
    "HITEC City":      "Hyderabad's tech capital. NASSCOM hub, highest office absorption in south India.",
    "Kondapur":        "Premium residential zone adjacent to HITEC City with Metro connectivity.",
    "Manikonda":       "Affordable zone next to Gachibowli, strong investment returns.",
    "Narsingi":        "Emerging western Hyderabad corridor near Financial District.",
    "Miyapur":         "Hyderabad Metro terminus, affordable entry into city's growth corridor.",
    "Sector 62":       "Noida's established IT sector with DLF, HCL campuses.",
    "Sector 137":      "Metro connectivity, near Noida-Greater Noida Expressway.",
    "Greater Noida West": "Affordable NCR zone, massive under-construction inventory.",
    "Sector 150":      "Noida's greenest sector, sports city project driving premiumisation.",
    "Expressway":      "Yamuna Expressway industrial corridor, long-term investment play.",
    "OMR":             "Chennai's IT corridor (Old Mahabalipuram Road), long stretch with varied micro-markets.",
    "Perambur":        "North Chennai industrial and residential zone, affordable.",
    "Velachery":       "South Chennai commercial hub, Metro operational, strong rental demand.",
    "Sholinganallur":  "OMR IT park zone, high rental yields from tech workforce.",
    "Medavakkam":      "Affordable South Chennai suburb with improving connectivity.",
    "Anna Nagar":      "Premium established Chennai locality, Metro Phase 2 upcoming.",
}

def generate_locality_insights() -> dict:
    insights = []
    for city, cfg in CITIES.items():
        for locality in cfg["localities"]:
            r = _seed(city + locality)
            near_metro = locality in cfg["metro"]
            infra      = r.randint(68, 92) if near_metro else r.randint(42, 72)
            demand     = min(100, infra + r.randint(-5, 15))

            insights.append({
                "city":                    city,
                "locality":                locality,
                "infrastructure_score":    infra,
                "demand_index":            demand,
                "supply_index":            r.randint(40, 85),
                "population_growth_3yr_cagr_pct": round(r.uniform(2.1, 6.8), 1),
                "avg_price_trend_yoy_pct": round(r.uniform(
                    cfg["appreciation_min"] / 3,
                    cfg["appreciation_max"] / 2), 1),
                "rental_yield_avg_pct":    round(r.uniform(2.8, 4.9), 2),
                "vacancy_rate_pct":        round(r.uniform(3.5, 14.0), 1),
                "connectivity_rating":     r.choice(CONNECTIVITY[:2]) if near_metro else r.choice(CONNECTIVITY[1:]),
                "metro_connectivity":      near_metro,
                "metro_line":              METRO_LINES.get(locality, "No metro planned"),
                "flood_risk":              r.choice(FLOOD_RISK),
                "air_quality_index":       r.choice(AQI),
                "walkability_score":       r.randint(35, 80),
                "top_employers_nearby":    r.sample(EMPLOYERS[city], k=min(4, len(EMPLOYERS[city]))),
                "social_infrastructure": {
                    "schools_within_3km":   r.randint(3, 15),
                    "hospitals_within_3km": r.randint(2, 8),
                    "malls_within_5km":     r.randint(1, 5),
                    "parks":                r.randint(2, 10),
                },
                "price_segment":           r.choice(PRICE_SEGMENT),
                "investor_type_recommended": r.choice([
                    "Long-term appreciation",
                    "Rental income focused",
                    "Balanced appreciation + yield",
                    "Capital gains play",
                ]),
                "avg_transaction_volume_monthly": r.randint(45, 280),
                "luxury_project_count":    r.randint(0, 6),
                "affordable_project_count": r.randint(0, 8),
                "under_construction_projects": r.randint(3, 22),
                "locality_summary":        SUMMARIES.get(locality, f"Emerging locality in {city} with growth potential."),
            })

    return {"locality_insights": insights}


# =============================================================================
# 3. ROI SCENARIOS  →  synthetic_roi_scenarios.json
# =============================================================================

def _calc_emi_monthly(price_lakhs, loan_pct, rate_pct, tenure_years):
    loan  = price_lakhs * loan_pct / 100
    emi   = _emi(loan, rate_pct, tenure_years)
    return loan, emi


def generate_roi_scenarios() -> dict:
    scenarios = []

    # (city, locality, verdict, appreciation_range)
    templates = [
        ("Hyderabad", "HITEC City",       "STRONG BUY", (14, 18)),
        ("Hyderabad", "Gachibowli",       "STRONG BUY", (13, 17)),
        ("Bangalore", "Whitefield",       "STRONG BUY", (12, 16)),
        ("Bangalore", "Sarjapur Road",    "BUY",        (11, 15)),
        ("Pune",      "Hinjewadi",        "BUY",        (11, 14)),
        ("Pune",      "Wakad",            "BUY",        (10, 13)),
        ("Pune",      "Baner",            "BUY",        (9,  13)),
        ("Mumbai",    "Powai",            "BUY",        (9,  12)),
        ("Mumbai",    "Thane West",       "BUY",        (8,  11)),
        ("Noida",     "Sector 150",       "BUY",        (9,  13)),
        ("Bangalore", "Koramangala",      "STRONG BUY", (12, 16)),
        ("Hyderabad", "Kondapur",         "STRONG BUY", (13, 17)),
        ("Pune",      "Viman Nagar",      "BUY",        (9,  13)),
        ("Chennai",   "OMR",              "BUY",        (8,  12)),
        ("Bangalore", "Electronic City",  "BUY",        (10, 14)),
        ("Mumbai",    "Andheri East",     "HOLD",       (7,  10)),
        ("Noida",     "Sector 62",        "HOLD",       (7,  10)),
        ("Chennai",   "Sholinganallur",   "HOLD",       (7,  10)),
        ("Mumbai",    "Mira Road",        "HOLD",       (5,  8)),
        ("Noida",     "Greater Noida West","HOLD",      (5,  8)),
        ("Chennai",   "Medavakkam",       "HOLD",       (6,  9)),
        ("Pune",      "Nibm Road",        "HOLD",       (6,  9)),
        ("Noida",     "Expressway",       "AVOID",      (3,  6)),
        ("Mumbai",    "Kharghar",         "AVOID",      (4,  7)),
        ("Chennai",   "Perambur",         "AVOID",      (3,  5)),
        ("Hyderabad", "Narsingi",         "AVOID",      (4,  7)),
    ]

    for i, (city, locality, verdict, appre_range) in enumerate(templates, 1):
        r        = _seed(city + locality + "roi")
        cfg      = CITIES[city]
        price    = round(r.uniform(cfg["price_min"], cfg["price_max"]), 1)
        appre    = round(r.uniform(*appre_range), 1)
        rent     = int(price * cfg["rent_multiplier"] * 1000)
        loan_pct = 70
        rate     = round(r.uniform(8.5, 9.25), 2)
        tenure   = 20
        loan_l, emi = _calc_emi_monthly(price, loan_pct, rate, tenure)

        gross_yield = round((rent * 12) / (price * 100_000) * 100, 2)
        net_yield   = round(gross_yield * 0.75, 2)
        break_even  = round(price * 100_000 / (rent * 12), 1)
        val_5yr     = round(price * (1 + appre / 100) ** 5,  1)
        val_10yr    = round(price * (1 + appre / 100) ** 10, 1)
        ret_10yr    = round((val_10yr - price) / price * 100, 1)
        irr         = round(appre * 0.92 + gross_yield * 0.4, 1)
        cashflow    = rent - emi

        verdict_reasons = {
            "STRONG BUY": f"IT corridor with {appre}% YoY appreciation. Metro connectivity drives rental premium.",
            "BUY":        f"Solid fundamentals. {gross_yield:.1f}% rental yield with steady {appre}% appreciation.",
            "HOLD":       f"Stable market. Moderate {appre}% appreciation. Watch for supply overhang.",
            "AVOID":      f"Oversupplied micro-market. {appre}% appreciation insufficient to offset carrying costs.",
        }

        scenarios.append({
            "scenario_id":       f"ROI_{i:03d}",
            "city":              city,
            "locality":          locality,
            "property_type":     f"{r.choice(['2BHK','3BHK'])} Apartment",
            "purchase_price_lakhs": price,
            "monthly_rent_current": rent,
            "appreciation_rate_annual_pct": appre,
            "loan_details": {
                "loan_amount_lakhs": round(loan_l, 1),
                "loan_pct":          loan_pct,
                "interest_rate_pct": rate,
                "tenure_years":      tenure,
                "emi_monthly":       emi,
            },
            "calculated_returns": {
                "rental_yield_gross_pct":    gross_yield,
                "rental_yield_net_pct":      net_yield,
                "monthly_cashflow_positive": cashflow > 0,
                "monthly_cashflow_amount":   cashflow,
                "break_even_years":          break_even,
                "value_at_5yr_lakhs":        val_5yr,
                "value_at_10yr_lakhs":       val_10yr,
                "total_return_10yr_pct":     ret_10yr,
                "irr_10yr_pct":              irr,
                "best_exit_horizon_years":   5 if verdict in ("STRONG BUY", "BUY") else 10,
            },
            "investment_verdict": verdict,
            "verdict_reason":     verdict_reasons[verdict],
        })

    return {"roi_scenarios": scenarios}


# =============================================================================
# 4. HITL TEST SCENARIOS  →  hitl_test_scenarios.json
# =============================================================================

HITL_TEMPLATES = [
    ("Hinjewadi Phase 2, Pune",     "Pune",      "APPROVE_WITH_NOTES", "BULLISH",
     "Strong buy fundamentals here. Infosys and Wipro campuses within 800m justify the rental premium. "
     "Removing Wakad comp as it distorts psf average downward. Metro Line 3 extension is a real 2027 catalyst.", 3),
    ("Whitefield, Bangalore",       "Bangalore", "APPROVE_ALL",         "BULLISH",
     "All comps valid. Whitefield Metro is now operational — this alone justifies the 18% YoY premium. Solid BUY.", 2),
    ("HITEC City, Hyderabad",       "Hyderabad", "MODIFY_AND_APPROVE",  "BULLISH",
     "Removing the Manikonda comp (6km away, different micro-market). HITEC City fundamentals remain exceptional. "
     "Microsoft and Google offices at walking distance make this a category-1 investment zone.", 4),
    ("Baner, Pune",                 "Pune",      "APPROVE_WITH_NOTES",  "BULLISH",
     "Baner-Balewadi corridor is underpriced vs Hinjewadi. Strong social infra. Approving all comps. "
     "Recommend long horizon — 7-10 years for maximum capital gains.", 1),
    ("Electronic City, Bangalore",  "Bangalore", "FLAG_RISKS",          "BEARISH",
     "Concern: oversupply of 2BHK units in Phase 1 and Phase 2. Vacancy rates elevated at 11-13%. "
     "Rental yields weak. Approving with caution — only suitable for long-horizon investors comfortable with short-term pain.", -4),
    ("Gachibowli, Hyderabad",       "Hyderabad", "APPROVE_ALL",         "BULLISH",
     "Gachibowli Financial District is the strongest micro-market in India right now. All comps valid and conservative. "
     "Strong buy — buyer should move fast in this corridor.", 5),
    ("Thane West, Mumbai",          "Mumbai",    "MODIFY_AND_APPROVE",  "NEUTRAL",
     "Removing the Mira Road comp — separate market entirely. Thane West fundamentals are solid "
     "but appreciation will lag IT corridors. Good for end-users, moderate for pure investors.", 0),
    ("Sector 137, Noida",           "Noida",     "FLAG_RISKS",          "BEARISH",
     "Risk: massive unsold inventory from 2017-2021 era is still being absorbed. Builder delays "
     "in this corridor are a concern. Approving with a risk flag — only RERA-registered ready-to-move.", -5),
    ("OMR, Chennai",                "Chennai",   "APPROVE_WITH_NOTES",  "NEUTRAL",
     "OMR is a long corridor — comps from beyond Sholinganallur are not comparable. Approving first 3. "
     "Steady market, not exciting but stable income play for conservative investors.", 1),
    ("Koramangala, Bangalore",      "Bangalore", "APPROVE_ALL",         "BULLISH",
     "Koramangala 5th Block is recession-proof Bangalore real estate. All comps valid and underpriced. "
     "Startup ecosystem + premium social infra = best rental yield in city. Strong buy.", 5),
]

def generate_hitl_scenarios() -> dict:
    scenarios = []
    for i, (prop, city, action, sentiment, notes, delta) in enumerate(HITL_TEMPLATES, 1):
        r = _seed(prop)
        comps_total    = r.randint(3, 5)
        comps_removed  = 1 if action in ("APPROVE_WITH_NOTES", "MODIFY_AND_APPROVE") else 0
        comps_approved = comps_total - comps_removed

        positive_kw = ["strong", "solid", "buy", "upside", "catalyst", "exceptional",
                       "valid", "underpriced", "conservative", "growth", "premium"]
        negative_kw = ["concern", "risk", "oversupply", "weak", "caution", "avoid",
                       "elevated", "lag", "delay", "pain"]

        keywords = [w for w in (positive_kw if sentiment == "BULLISH" else negative_kw)
                    if w in notes.lower()][:4]

        scenarios.append({
            "scenario_id":           f"HITL_{i:03d}",
            "property_queried":      prop,
            "city":                  city,
            "ai_presented_comps_count": comps_total,
            "analyst_action":        action,
            "comps_removed_count":   comps_removed,
            "removal_reason":        (
                f"Comp {r.randint(2,4)} is {r.randint(3,7)}km away — outside valid comparable radius."
                if comps_removed > 0 else None
            ),
            "analyst_notes":         notes,
            "sentiment":             sentiment,
            "sentiment_keywords":    keywords,
            "expected_score_adjustment": delta,
            "approved_comps_count":  comps_approved,
        })

    return {"hitl_scenarios": scenarios}


# =============================================================================
# 5. EDGE CASES  →  edge_cases.json
# =============================================================================

EDGE_TEMPLATES = [
    ("VERY_HIGH_BUDGET",    "Koramangala 5th Block", "Bangalore", 450, "4BHK+", 10,
     "Return ultra-premium comps only (villas, penthouses). Luxury segment appreciation 8-12%.",
     "price_per_sqft calculation if budget > 500L", "Return Prestige/Brigade villas and luxury penthouses only"),
    ("VERY_HIGH_BUDGET",    "Juhu Beach Road",        "Mumbai",    520, "4BHK+", 7,
     "Handle Mumbai luxury tier (sea-facing). Price/sqft can exceed ₹1L/sqft.",
     "ROI calc overflow at very high absolute values", "Sea-facing Juhu/Bandra luxury apartments only"),
    ("VERY_LOW_BUDGET",     "Sector 62",              "Noida",      22, "1BHK",  5,
     "Return studio/micro-apartment comps. Rental yield focus.",
     "No comps found if budget filter too strict — return nearest bracket", "Sub-25L studio listings"),
    ("VERY_LOW_BUDGET",     "Medavakkam",             "Chennai",    18, "1BHK",  3,
     "Affordable segment. Fallback to nearest budget bracket if no exact matches.",
     "Empty comps array crashing score calculator", "Affordable 1BHK listings near budget"),
    ("SHORT_HORIZON",       "Hinjewadi Phase 2",      "Pune",       85, "2BHK",  1,
     "1-year horizon means trading not investing. Flag as short-term flip scenario.",
     "Appreciation formula gives near-zero gain for 1yr — score may show 0", "Current-year listings only"),
    ("SHORT_HORIZON",       "HITEC City",             "Hyderabad",  95, "2BHK",  1,
     "Flag: 1-year horizon unlikely to recover transaction costs (stamp duty ~5%).",
     "ROI shows negative net return after transaction costs", "Recent listings with quick resale potential"),
    ("UNKNOWN_LOCALITY",    "Nandoshi Village",       "Pune",       65, "2BHK",  5,
     "Unknown locality — fallback to city-level insights. Warn user data is approximate.",
     "KeyError in locality_insights dict lookup", "Return generic Pune comps as fallback"),
    ("UNKNOWN_LOCALITY",    "Zingari Layout",         "Bangalore",  80, "2BHK",  7,
     "Misspelled/unknown locality. Fuzzy match or fallback to nearest known locality.",
     "rag_search returns empty — no grounding context", "Generic Bangalore outskirts comps"),
    ("MISMATCH_BHK_BUDGET", "Whitefield",             "Bangalore",  30, "4BHK+", 5,
     "4BHK with 30L budget is impossible in Bangalore. Return cheapest available and warn user.",
     "Budget filter returns empty list", "Return disclaimer + nearest affordable BHK type"),
    ("MISMATCH_BHK_BUDGET", "Powai",                  "Mumbai",     25, "3BHK",  7,
     "3BHK Powai for 25L doesn't exist. Return closest match with price mismatch warning.",
     "Score calc divides by zero if no comps", "Show 1BHK options with upgrade recommendation"),
    ("OVERSUPPLIED_MARKET", "Greater Noida West",     "Noida",      55, "2BHK", 10,
     "High unsold inventory. AI should flag oversupply. Score should be capped low.",
     "Demand index artificially high from old data", "Include stalled project warnings in report"),
    ("OVERSUPPLIED_MARKET", "Sector 150",             "Noida",      70, "3BHK", 10,
     "Sports City project may have distorted original projections. Flag builder credibility.",
     "RAG context may not contain specific builder delay info", "Filter for RERA-registered only"),
    ("FLOOD_PRONE_AREA",    "Saidapet Low Zone",      "Chennai",    60, "2BHK",  5,
     "Known flood-risk area. Report must include flood risk warning prominently.",
     "Flood risk score missing from locality data for new/unknown localities", "Add flood disclaimer to report header"),
    ("FLOOD_PRONE_AREA",    "Kurla East",             "Mumbai",     75, "2BHK",  7,
     "Low-lying Mumbai suburb. Monsoon flood risk must be in risk_factors.",
     "Risk section omits flood if not explicitly in RAG context", "Include BMC flood zone data"),
    ("NEW_DEVELOPMENT_ZONE","Navi Mumbai Airport Zone","Mumbai",   120, "3BHK", 10,
     "Less than 2 years of price data. AI must note limited historical data.",
     "Appreciation rate calc unreliable with < 24 months data", "Project-launch pricing only, no resale comps"),
    ("HIGH_NRI_DEMAND",     "Kondapur",               "Hyderabad",  95, "2BHK",  7,
     "NRI-heavy locality. USD/INR hedging argument should appear in report.",
     "NRI demand not in standard locality_insights schema", "Include NRI-friendly projects with dollar rental yields"),
    ("HIGH_NRI_DEMAND",     "Kothrud",                "Pune",       90, "3BHK", 10,
     "High NRI demand from Pune diaspora in US/UK. Report should note foreign remittance advantage.",
     "NRI angle missing if not prompted", "Premium projects with NRI payment plans"),
    ("COMMERCIAL_ADJACENT", "Hadapsar MIDC Zone",     "Pune",       70, "2BHK",  7,
     "Adjacent to MIDC industrial zone — noise/air quality concerns vs industrial demand.",
     "Infrastructure score may be misleadingly high due to job density", "Include industrial zone proximity warning"),
    ("COMMERCIAL_ADJACENT", "Whitefield ITPL Fringe",  "Bangalore",  88, "2BHK",  5,
     "Commercial-residential boundary. ITPL expansion may eat into residential zones.",
     "Zoning rezoning risk not captured in static RAG data", "Flag DP zoning revision risk"),
    ("VERY_LONG_HORIZON",   "Sector 150 Sports City", "Noida",      65, "2BHK", 15,
     "15-year horizon. Projections become speculative. AI should widen confidence intervals.",
     "Compound appreciation formula gives astronomically high values for 15yr",
     "Cap projections at 10yr and add note about extrapolation risk"),
]

def generate_edge_cases() -> dict:
    cases = []
    for i, (cat, addr, city, budget, bhk, horizon, expected, failure, hint) in enumerate(EDGE_TEMPLATES, 1):
        cases.append({
            "case_id":             f"EDGE_{i:03d}",
            "category":            cat,
            "input": {
                "address":                  addr,
                "city":                     city,
                "budget_lakhs":             budget,
                "bhk_type":                 bhk,
                "investment_horizon_years": horizon,
            },
            "expected_behavior":      expected,
            "potential_failure_point": failure,
            "mock_comp_hint":          hint,
        })
    return {"edge_cases": cases}


# =============================================================================
# 6. MOCK TELEMETRY TRACES  →  mock_telemetry_traces.json
# =============================================================================

VERDICTS = ["STRONG BUY", "STRONG BUY", "BUY", "BUY", "BUY", "HOLD", "HOLD", "AVOID"]

NODE_NAMES = [
    "fetch_market_data", "inject_rag_context", "calculate_preliminary",
    "hitl_verification", "calculate_final_score", "generate_report",
]

RAG_PREVIEWS = {
    "Pune":      "Pune Metro Line 3 extension to Hinjewadi Phase 3 approved...",
    "Bangalore": "Namma Metro Phase 2B extension to Whitefield operational since...",
    "Mumbai":    "Navi Mumbai International Airport construction on schedule for...",
    "Hyderabad": "Hyderabad Metro Red Line extension to Shamshabad approved...",
    "Noida":     "Yamuna Expressway Industrial Development Authority approved...",
    "Chennai":   "Chennai Metro Phase 2 corridor connecting OMR to city centre...",
}

HITL_ACTIONS = ["APPROVE_ALL", "APPROVE_WITH_NOTES", "MODIFY_AND_APPROVE", "FLAG_RISKS"]


def _random_trace_id(r):
    return r.randbytes(8).hex() + r.randbytes(6).hex()


def _ts(base: datetime, delta_seconds: int) -> str:
    return (base + timedelta(seconds=delta_seconds)).isoformat().replace("+00:00", "Z")


def generate_telemetry_traces() -> dict:
    traces   = []
    base_dt  = datetime(2024, 11, 15, 9, 0, 0, tzinfo=timezone.utc)

    trace_inputs = []
    for city, cfg in CITIES.items():
        for loc in cfg["localities"][:3]:
            trace_inputs.append((city, loc))
    random.shuffle(trace_inputs)
    trace_inputs = trace_inputs[:15]

    for i, (city, locality) in enumerate(trace_inputs):
        r          = _seed(city + locality + "telemetry")
        cfg        = CITIES[city]
        price      = round(r.uniform(cfg["price_min"], cfg["price_max"]), 1)
        rent       = int(price * cfg["rent_multiplier"] * 1000)
        appre      = round(r.uniform(cfg["appreciation_min"], cfg["appreciation_max"]), 1)
        prelim     = r.randint(55, 82)
        analyst_delta = r.randint(-6, 7)
        final      = max(10, min(100, prelim + analyst_delta))
        verdict    = r.choice(VERDICTS)

        hitl_wait       = r.randint(15_000, 95_000)
        gemini_lat      = r.randint(2800, 6200)
        fetch_lat       = r.randint(95, 210)
        rag_lat         = r.randint(245, 480)
        calc_lat        = r.randint(55, 130)
        calc_final_lat  = r.randint(80, 155)
        total_lat       = fetch_lat + rag_lat + calc_lat + hitl_wait + calc_final_lat + gemini_lat

        start_ts = base_dt + timedelta(hours=i * 2, minutes=r.randint(0, 55))
        end_ts   = start_ts + timedelta(milliseconds=total_lat)

        rag_scores = sorted([round(r.uniform(0.55, 0.95), 2) for _ in range(3)], reverse=True)

        traces.append({
            "trace_id":          _random_trace_id(r),
            "thread_id":         "thread_" + r.randbytes(6).hex(),
            "timestamp_start":   start_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timestamp_end":     end_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_latency_ms":  total_lat,
            "property_queried":  f"{locality}, {city}",
            "status":            "completed",
            "nodes_executed":    NODE_NAMES,
            "node_timings_ms": {
                "fetch_market_data":    fetch_lat,
                "inject_rag_context":   rag_lat,
                "calculate_preliminary": calc_lat,
                "hitl_verification":    hitl_wait,
                "calculate_final_score": calc_final_lat,
                "generate_report":      gemini_lat,
            },
            "tool_calls": [
                {
                    "tool":     "search_properties",
                    "latency_ms": r.randint(55, 130),
                    "inputs":   {
                        "location":   f"{locality}, {city}",
                        "budget_min": round(price * 0.8, 1),
                        "budget_max": round(price * 1.2, 1),
                        "bhk_type":   r.choice(["2BHK", "3BHK"]),
                    },
                    "output_summary": f"{r.randint(3,4)} comps returned, avg price {price}L",
                },
                {
                    "tool":     "get_locality_insights",
                    "latency_ms": r.randint(30, 80),
                    "inputs":   {"locality": locality, "city": city},
                    "output_summary": f"infrastructure_score: {r.randint(55,90)}, demand_index: {r.randint(60,95)}",
                },
                {
                    "tool":     "rag_search",
                    "latency_ms": rag_lat,
                    "inputs":   {"query": f"infrastructure development zoning {city} {locality}"},
                    "output_summary": f"3 chunks retrieved — top relevance {rag_scores[0]}",
                },
                {
                    "tool":     "calculate_roi",
                    "latency_ms": r.randint(8, 20),
                    "inputs":   {
                        "price_lakhs":           price,
                        "monthly_rent":          rent,
                        "appreciation_rate_pct": appre,
                    },
                    "output_summary": f"rental_yield: {round(rent*12/price/1000, 1)}%, 10yr_value: {round(price*(1+appre/100)**10, 0)}L",
                },
            ],
            "rag_retrievals": {
                "query":              f"infrastructure development zoning {city} {locality}",
                "chunks_retrieved":   3,
                "top_chunk_preview":  RAG_PREVIEWS.get(city, "Urban development project approved..."),
                "relevance_scores":   rag_scores,
            },
            "gemini_call": {
                "model":             "gemini-1.5-flash",
                "prompt_tokens":     r.randint(1600, 2200),
                "completion_tokens": r.randint(480, 780),
                "latency_ms":        gemini_lat,
                "finish_reason":     "stop",
            },
            "hitl_interaction": {
                "wait_time_ms":             hitl_wait,
                "analyst_action":           r.choice(HITL_ACTIONS),
                "comps_removed":            r.randint(0, 2),
                "analyst_notes_length_chars": r.randint(80, 320),
            },
            "scores": {
                "preliminary_score": prelim,
                "final_score":       final,
                "score_delta":       analyst_delta,
            },
            "final_verdict": verdict,
        })

    return {"mock_traces": traces}


# =============================================================================
# 7. MASTER PLANS — generated via Gemini API
# =============================================================================

MASTER_PLANS_FALLBACK = """\
Pune Metropolitan Region Development Authority (PMRDA) has approved the extension of Pune Metro Line 3 from Hinjewadi Phase 1 to Hinjewadi Phase 3, adding three new stations at Rajiv Gandhi Infotech Park Gate 1, Phase 2 Junction, and Maan Village. The project carries a capital outlay of Rs 2,840 crore and is scheduled for completion by Q3 2027. Properties within 600 metres of the proposed Phase 2 Junction station have already recorded a 9 to 12 percent price premium over comparable properties outside the catchment zone.

Brihanmumbai Municipal Corporation has rezoned a 42-hectare parcel in Vikhroli East from industrial warehouse use to high-density mixed-use commercial under Development Plan 2034 amendments notified in October 2024. The revised Floor Space Index of 4.0 against the earlier 1.0 permits high-rise residential towers up to 40 floors. Adjacent residential localities of Powai and Kanjurmarg are forecast to see spillover demand growth of 15 to 20 percent over the next 36 months.

Hyderabad Metro Rail Limited has received final clearance from the Telangana government for the Phase 2 extension connecting Raidurgam station on the Blue Line to the proposed Financial District terminus near Narsingi. The 8.4-kilometre corridor includes four new underground stations and is expected to be operational by Q1 2028. Residential micro-markets within one kilometre of the Narsingi interchange site have seen a 14 percent jump in new project launches since the announcement.

Bangalore Metropolitan Region Development Authority issued a zoning notification rezoning a 110-hectare industrial belt along Sarjapur Road between Carmelram and Bellandur from light industrial to mixed-use residential and commercial. The change enables FSI of 3.5 and is expected to unlock approximately 18,000 new residential units by 2028. Immediate catchment localities Bellandur and Kadabeesanahalli have already recorded a 22 percent increase in land transaction volumes in the subsequent quarter.

Greater Noida Industrial Development Authority has approved the Integrated Township Policy for Sector 12 Greater Noida West, permitting private developers to build integrated townships exceeding 50 hectares with a land use mix of 60 percent residential and 40 percent commercial. The policy is expected to attract Rs 4,200 crore in private investment and create 11,000 residential units over five years. The Aqua Metro Line terminus at Sector 137 is within 2.2 kilometres of the designated township zone.

Tamil Nadu Industrial Development Corporation has notified the establishment of the Chennai Peripheral Ring Road Industrial Corridor along a 62-kilometre stretch from Poonamallee to Maraimalai Nagar passing through Sholinganallur and Medavakkam. The corridor includes designated IT and manufacturing SEZ clusters at three nodes. Residential localities within two kilometres of the Sholinganallur node are projected to benefit from 25,000 new knowledge-economy jobs by 2027.

The Pune Municipal Corporation Smart City Mission has designated Kothrud and Erandwane as Priority Development Zones under the Pune Smart City Phase 3 plan, allocating Rs 780 crore for underground utility ducting, fibre-optic smart grid infrastructure, and pedestrian-priority streetscaping on 18 key roads. Smart city designation has historically correlated with a 7 to 11 percent price appreciation premium in comparable zones across Indian metros.

Hyderabad Outer Ring Road Elevated Corridor Phase 2 connecting the HICC Novotel junction on the ORR to Patancheru MIDC has received environmental clearance from the Telangana Environment Protection Board. The 34-kilometre elevated expressway will provide direct four-lane connectivity between HITEC City and the Patancheru industrial corridor. Land parcels within 500 metres of the proposed Gachibowli interchange have already been acquired by three tier-1 residential developers totalling Rs 1,120 crore in land transactions.

Navi Mumbai International Airport is on track for partial operations handling 10 million passengers annually by December 2025 under the CIDCO development authority master plan. The airport is located in Ulwe node Navi Mumbai and will catalyse commercial and hospitality development in Ulwe, Dronagiri, and Kharghar sectors. CIDCO has notified a Transit-Oriented Development zone within 1.5 kilometres of the proposed airport metro station with permissible FSI of 5.0.

Bangalore Development Authority has amended the Revised Master Plan 2031 to designate the North Bangalore Aerospace and Defence Corridor spanning Devanahalli, Doddaballapur, and Yelahanka as a High-Tech Manufacturing and Residential Mixed-Use Zone. The corridor encompasses 4,200 hectares and is anchored by the existing Aerospace SEZ housing Hindustan Aeronautics Limited, Boeing, and Safran facilities. Residential demand in Yelahanka has grown 31 percent year-on-year following the corridor notification.

Chennai Metropolitan Development Authority has approved the TOD Policy Framework for the Phase 2 Chennai Metro corridors, permitting FSI of 4.0 within 500 metres and 3.0 within 800 metres of metro station centrelines on the proposed Lighthouse to Poonamallee and Madhavaram to Sholinganallur corridors. Affected localities include Anna Nagar West, Kilpauk, Ashok Nagar, and Adyar. The TOD notification is expected to trigger redevelopment of approximately 2,400 older residential plots within the influence zones by 2030.

Noida Authority has notified a Special Development Zone for the Film City project in Sector 21 Greater Noida covering 230 hectares. The integrated media and entertainment complex will house production studios, post-production facilities, luxury hotels, and ancillary residential development. The nearest metro station at Sector 137 on the Aqua Line is 3.8 kilometres from the Film City site with a proposed shuttle connectivity corridor. Residential projects in Sector 150 and Sector 168 have been repositioned to target entertainment industry professionals.

Pune Municipal Corporation in partnership with Maharashtra Housing and Area Development Authority has launched the Integrated Affordable Housing Scheme for Hadapsar and Kondhwa covering 8,400 units across six designated sites. The scheme targets households with annual income below Rs 18 lakh and offers units at indexed prices between Rs 28 lakh and Rs 52 lakh. The affordable housing designation is expected to improve overall locality demand scores as it anchors a broader residential ecosystem in South Pune.

Hyderabad Metropolitan Development Authority has fast-tracked the development of the Tukkuguda Aerospace and Defence Manufacturing Cluster in Shamshabad near the Rajiv Gandhi International Airport. The cluster spans 1,400 hectares and has attracted anchor investments from Tata Advanced Systems, L&T Defence, and Bharat Forge totalling Rs 9,800 crore. Residential localities in Shadnagar and Kothur along the Hyderabad-Bangalore National Highway 44 corridor are projected to see employment-driven housing demand growth of 18 to 24 percent annually through 2028.

Bangalore Bruhat Mahanagara Palike has approved the Peripheral Ring Road project connecting Tumakuru Road in the northwest to Hosur Road in the southeast via a 73-kilometre six-lane arterial corridor. The road passes through Yelahanka, Hennur, Varthur, and Sarjapur providing orbital connectivity independent of the city centre. Land along the PRR alignment has been acquired at a government declared guideline value of Rs 3,200 per square foot with market transactions in advance land parcels occurring at Rs 4,800 to 6,200 per square foot.

Mumbai Metropolitan Region Development Authority has notified the Trans Harbour Rail Link integration plan connecting the Thane-Panvel Trans Harbour Line with the proposed Navi Mumbai Metro Line 1 at Belapur interchange. The integration will create a seamless 62-kilometre suburban rail and metro arc from CST Mumbai to NMIA airport. Residential localities in Kharghar, Belapur, and Nerul are expected to see commute times to Mumbai CBD drop from 75 minutes to 42 minutes upon full integration by 2026.

Directorate of Town and Country Planning Telangana has approved the Hyderabad Zoning Regulations 2024 Amendment introducing a new High Density Mixed Use Commercial Zone category applicable to 18 designated growth nodes across the Outer Ring Road corridor. The amendment permits residential towers up to 50 floors with ground floor commercial mandatory activation within the designated nodes. Kondapur, Nanakramguda, and Kokapet have been designated as Priority Nodes under the amendment.

Maharashtra Industrial Development Corporation has received Union Cabinet approval for the Pune-Nashik High Speed Rail Corridor feasibility project covering 235 kilometres with proposed stations at Chakan, Alandi, Manchar, Sangamner, and Nashik Road. While the project is at pre-feasibility stage with a timeline of 2032 to 2036, land values along the proposed corridor in Chakan and Talegaon have already appreciated 18 percent in the 12 months following the Union Cabinet announcement.

Greater Chennai Corporation has approved a Rs 1,400 crore Stormwater Drain and Flood Mitigation Master Plan targeting 22 historically flood-prone wards in South Chennai including parts of Velachery, Pallikaranai, and Thoraipakkam. The project involves construction of 12 retention basins, channelisation of 8 primary drains, and elevation of 34 kilometres of arterial roads. Successful completion expected by 2026 is projected to upgrade flood risk rating for approximately 4,200 residential plots from High to Low, directly impacting property valuations by an estimated 8 to 15 percent.

Delhi-Mumbai Industrial Corridor Development Corporation has notified Phase 2 of the Integrated Manufacturing Cluster at Greater Noida Dadri node covering 6,200 hectares. The cluster is anchored by the existing Inland Container Depot and will add a multi-modal logistics hub and warehousing zone. Employment projections indicate 95,000 direct jobs by 2030. Residential micro-markets in Sector 1 Greater Noida and Ecotech zones have seen registered property transactions increase 44 percent year-on-year since the Phase 2 notification.
"""


def generate_master_plans_with_gemini(api_key: str) -> str:
    """Call Gemini to generate master_plans.txt. Falls back to built-in text if API fails."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = """You are an urban planning document writer for Indian cities.
Write exactly 10 additional paragraphs of urban development facts suitable for a real estate investment RAG knowledge base.
Cover cities: Pune, Bangalore, Mumbai, Hyderabad, Noida, Chennai.
Each paragraph must describe ONE specific project (metro, IT park, rezoning, highway, smart city, affordable housing).
Include: project name, exact locality, timeline (2024-2029), distance impact in metres, expected price impact percentage, responsible authority.
Write in a formal planning document tone. Separate paragraphs with a single blank line.
Do NOT number paragraphs. Do NOT use headings or markdown. Plain text only."""

        response = model.generate_content(prompt)
        extra    = response.text.strip()
        print("✅ Gemini generated additional master plans content")
        return MASTER_PLANS_FALLBACK + "\n\n" + extra

    except Exception as e:
        print(f"⚠️  Gemini call failed ({e}). Using built-in fallback master_plans.txt (20 paragraphs).")
        return MASTER_PLANS_FALLBACK


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("PropGrowth AI — Synthetic Data Generator")
    print("=" * 60)

    # 1. Comps
    print("\n[1/6] Generating comparable properties...")
    comps = generate_comps()
    (OUT_DIR / "synthetic_comps.json").write_text(json.dumps(comps, indent=2))
    print(f"      ✅ {len(comps['comps'])} comps written → backend/data/synthetic_comps.json")

    # 2. Locality insights
    print("\n[2/6] Generating locality insights...")
    insights = generate_locality_insights()
    (OUT_DIR / "synthetic_locality_insights.json").write_text(json.dumps(insights, indent=2))
    print(f"      ✅ {len(insights['locality_insights'])} localities → backend/data/synthetic_locality_insights.json")

    # 3. ROI scenarios
    print("\n[3/6] Generating ROI scenarios...")
    roi = generate_roi_scenarios()
    (OUT_DIR / "synthetic_roi_scenarios.json").write_text(json.dumps(roi, indent=2))
    print(f"      ✅ {len(roi['roi_scenarios'])} scenarios → backend/data/synthetic_roi_scenarios.json")

    # 4. HITL scenarios
    print("\n[4/6] Generating HITL test scenarios...")
    hitl = generate_hitl_scenarios()
    (OUT_DIR / "hitl_test_scenarios.json").write_text(json.dumps(hitl, indent=2))
    print(f"      ✅ {len(hitl['hitl_scenarios'])} scenarios → backend/data/hitl_test_scenarios.json")

    # 5. Edge cases
    print("\n[5/6] Generating edge cases...")
    edges = generate_edge_cases()
    (OUT_DIR / "edge_cases.json").write_text(json.dumps(edges, indent=2))
    print(f"      ✅ {len(edges['edge_cases'])} cases → backend/data/edge_cases.json")

    # 6. Telemetry traces
    print("\n[6/6] Generating mock telemetry traces...")
    telemetry = generate_telemetry_traces()
    (OUT_DIR / "mock_telemetry_traces.json").write_text(json.dumps(telemetry, indent=2))
    print(f"      ✅ {len(telemetry['mock_traces'])} traces → backend/data/mock_telemetry_traces.json")

    # 7. Master plans (Gemini)
    print("\n[7/7] Generating master_plans.txt via Gemini...")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("      ℹ️  GEMINI_API_KEY not set — using built-in fallback (20 paragraphs).")
        content = MASTER_PLANS_FALLBACK
    else:
        content = generate_master_plans_with_gemini(api_key)

    (OUT_DIR / "master_plans.txt").write_text(content)
    para_count = len([p for p in content.split("\n\n") if p.strip()])
    print(f"      ✅ {para_count} paragraphs → backend/data/master_plans.txt")

    print("\n" + "=" * 60)
    print("All datasets generated successfully!")
    print("=" * 60)
    print("\nFiles created:")
    for f in sorted(OUT_DIR.glob("*")):
        size = f.stat().st_size
        print(f"  {f.name:<45} {size/1024:>6.1f} KB")


if __name__ == "__main__":
    main()
