from pathlib import Path
import random
import json
import os

random.seed(42)  # Reproducible results

CITIES = {
    "Pune": ["Hinjewadi", "Wakad", "Baner", "Aundh", "Kharadi", "Viman Nagar", "Magarpatta", "Hadapsar"],
    "Bangalore": ["Whitefield", "Electronic City", "HSR Layout", "Koramangala", "Indiranagar", "Marathahalli", "Sarjapur", "Yelahanka"],
    "Mumbai": ["Bandra", "Andheri", "Powai", "Thane", "Navi Mumbai", "Borivali", "Goregaon", "Malad"],
    "Hyderabad": ["Gachibowli", "Hitec City", "Kondapur", "Financial District", "Madhapur", "Kukatpally", "Manikonda", "Shamshabad"],
    "Noida": ["Sector 62", "Sector 78", "Sector 137", "Greater Noida West", "Sector 150", "Noida Extension", "Sector 68", "Sector 168"],
    "Chennai": ["OMR", "Velachery", "Porur", "Anna Nagar", "Tambaram", "Sholinganallur", "Perungudi", "Thuraipakkam"]
}

EMPLOYERS = {
    "Pune": ["Infosys", "Tech Mahindra", "TCS", "Persistent Systems", "Cognizant", "ZS Associates"],
    "Bangalore": ["Google", "Amazon", "Flipkart", "Infosys", "Wipro", "PhonePe", "Oracle"],
    "Mumbai": ["Reliance", "Tata Consultancy", "Jio", "HDFC Bank", "ICICI", "Adani Group", "L&T"],
    "Hyderabad": ["Microsoft", "Amazon", "Google", "Deloitte", "PwC", "Cyient", "Genpact"],
    "Noida": ["Samsung", "HCL", "Adobe", "Paytm", "Barclays", "MakeMyTrip", "Genpact"],
    "Chennai": ["TCS", "Cognizant", "Zoho", "Hyundai", "Ford", "Ashok Leyland", "BMW"]
}

BHK_TYPES = ["1BHK", "2BHK", "3BHK", "4BHK"]
CONNECTIVITY = ["Excellent", "Good", "Average", "Poor"]
FLOOD_RISK = ["Low", "Medium", "High"]
SOURCES = ["MagicBricks", "99acres", "Housing.com", "NoBroker", "Local Broker"]

def generate_record(idx):
    city = random.choice(list(CITIES.keys()))
    locality = random.choice(CITIES[city])
    bhk = random.choice(BHK_TYPES)
    
    # Realistic Indian market ranges
    price_range = {"1BHK": (25, 70), "2BHK": (45, 120), "3BHK": (70, 250), "4BHK": (150, 500)}[bhk]
    area_range = {"1BHK": (450, 650), "2BHK": (750, 1100), "3BHK": (1100, 1800), "4BHK": (1800, 3000)}[bhk]
    
    price_lakhs = round(random.uniform(*price_range), 1)
    area_sqft = random.randint(*area_range)
    price_per_sqft = round(price_lakhs * 100000 / area_sqft)
    monthly_rent = round(price_lakhs * 100000 * random.uniform(0.025, 0.045) / 12)
    
    distance_km = round(random.uniform(0.1, 3.5), 1)
    nearby_metro = distance_km <= 0.8
    infra_score = random.randint(35, 95)
    demand_index = random.randint(40, 98)
    pop_growth = round(random.uniform(1.5, 6.0), 1)
    price_trend = round(random.uniform(-2.0, 12.0), 1)
    
    return {
        "id": f"PROP-{idx+1:04d}",
        "title": f"{bhk} Premium Residency in {locality}",
        "location": f"{locality}, {city}",
        "price": price_lakhs,
        "bhk": bhk,
        "area_sqft": area_sqft,
        "price_per_sqft": price_per_sqft,
        "monthly_rent": monthly_rent,
        "listing_age_days": random.randint(1, 90),
        "distance_km": distance_km,
        "nearby_metro": nearby_metro,
        "source": random.choice(SOURCES),
        "infrastructure_score": infra_score,
        "demand_index": demand_index,
        "population_growth_pct": pop_growth,
        "avg_price_trend_pct": price_trend,
        "top_employers_nearby": random.sample(EMPLOYERS[city], 3),
        "connectivity_rating": random.choice(CONNECTIVITY),
        "flood_risk": random.choices(FLOOD_RISK, weights=[0.6, 0.3, 0.1])[0],
        "social_infrastructure": {
            "schools": random.randint(2, 12),
            "hospitals": random.randint(1, 6),
            "malls": random.randint(1, 8)
        }
    }

# Generate 500 records
dataset = [generate_record(i) for i in range(500)]

dataset_path = Path("data")
dataset_path.mkdir(exist_ok=True)

# Save to JSON
os.makedirs("data", exist_ok=True)
with open("data/mock_properties_500.json", "w") as f:
    json.dump(dataset, f, indent=2)

print("✅ Generated data/mock_properties_500.json with 500 records.")
