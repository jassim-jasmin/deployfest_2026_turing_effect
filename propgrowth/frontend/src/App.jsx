import React, { useState, useEffect, useRef } from 'react';
import PropertyInput from './components/PropertyInput';
import AgentThinking from './components/AgentThinking';
import HitlVerification from './components/HitlVerification';
import InvestmentReport from './components/InvestmentReport';
import TelemetryMetrics from './components/TelemetryMetrics';

// Structured Mock Database based on ds.json
const MOCK_COMPS = [
  { "id": "COMP_001", "city": "Pune", "locality": "Hinjewadi Phase 2", "title": "Spacious 2BHK in IT Hub", "bhk_type": "2BHK", "price_lakhs": 85.5, "area_sqft": 1050, "price_per_sqft": 8143, "monthly_rent": 28000, "listing_age_days": 12, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_002", "city": "Pune", "locality": "Wakad", "title": "Modern 3BHK Apartment", "bhk_type": "3BHK", "price_lakhs": 145.0, "area_sqft": 1600, "price_per_sqft": 9062, "monthly_rent": 42000, "listing_age_days": 8, "nearby_metro": false, "source": "99Acres" },
  { "id": "COMP_003", "city": "Pune", "locality": "Baner", "title": "1BHK in Quiet Locality", "bhk_type": "1BHK", "price_lakhs": 55.0, "area_sqft": 650, "price_per_sqft": 8462, "monthly_rent": 16000, "listing_age_days": 25, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_004", "city": "Pune", "locality": "Kothrud", "title": "2BHK with City View", "bhk_type": "2BHK", "price_lakhs": 110.0, "area_sqft": 1150, "price_per_sqft": 9565, "monthly_rent": 30000, "listing_age_days": 4, "nearby_metro": false, "source": "99Acres" },
  { "id": "COMP_005", "city": "Pune", "locality": "Hadapsar", "title": "3BHK Family Home", "bhk_type": "3BHK", "price_lakhs": 160.0, "area_sqft": 1800, "price_per_sqft": 8889, "monthly_rent": 45000, "listing_age_days": 17, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_006", "city": "Pune", "locality": "Viman Nagar", "title": "Modern 2BHK Apartment", "bhk_type": "2BHK", "price_lakhs": 95.0, "area_sqft": 1000, "price_per_sqft": 9500, "monthly_rent": 25000, "listing_age_days": 30, "nearby_metro": false, "source": "99Acres" },
  { "id": "COMP_007", "city": "Pune", "locality": "Nibm Road", "title": "1BHK Studio Apartment", "bhk_type": "1BHK", "price_lakhs": 52.0, "area_sqft": 600, "price_per_sqft": 8667, "monthly_rent": 14000, "listing_age_days": 22, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_008", "city": "Bangalore", "locality": "Whitefield", "title": "2BHK in Tech Hub", "bhk_type": "2BHK", "price_lakhs": 150.0, "area_sqft": 1200, "price_per_sqft": 12500, "monthly_rent": 45000, "listing_age_days": 6, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_009", "city": "Bangalore", "locality": "Electronic City", "title": "1BHK Near Factory", "bhk_type": "1BHK", "price_lakhs": 75.0, "area_sqft": 650, "price_per_sqft": 11538, "monthly_rent": 20000, "listing_age_days": 14, "nearby_metro": false, "source": "99Acres" },
  { "id": "COMP_010", "city": "Bangalore", "locality": "Sarjapur Road", "title": "3BHK with Garden View", "bhk_type": "3BHK", "price_lakhs": 210.0, "area_sqft": 2000, "price_per_sqft": 10500, "monthly_rent": 60000, "listing_age_days": 10, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_011", "city": "Bangalore", "locality": "HSR Layout", "title": "2BHK in Green Society", "bhk_type": "2BHK", "price_lakhs": 135.0, "area_sqft": 1100, "price_per_sqft": 12273, "monthly_rent": 38000, "listing_age_days": 20, "nearby_metro": false, "source": "99Acres" },
  { "id": "COMP_012", "city": "Bangalore", "locality": "Koramangala", "title": "1BHK in Prime Locality", "bhk_type": "1BHK", "price_lakhs": 100.0, "area_sqft": 700, "price_per_sqft": 14286, "monthly_rent": 30000, "listing_age_days": 5, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_013", "city": "Bangalore", "locality": "Yelahanka", "title": "2BHK in Affordable Zone", "bhk_type": "2BHK", "price_lakhs": 85.0, "area_sqft": 1000, "price_per_sqft": 8500, "monthly_rent": 24000, "listing_age_days": 25, "nearby_metro": false, "source": "99Acres" },
  { "id": "COMP_014", "city": "Mumbai", "locality": "Thane West", "title": "3BHK in Suburban Area", "bhk_type": "3BHK", "price_lakhs": 280.0, "area_sqft": 1800, "price_per_sqft": 15556, "monthly_rent": 75000, "listing_age_days": 9, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_015", "city": "Mumbai", "locality": "Navi Mumbai", "title": "2BHK Near IT Park", "bhk_type": "2BHK", "price_lakhs": 320.0, "area_sqft": 1400, "price_per_sqft": 22857, "monthly_rent": 90000, "listing_age_days": 11, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_016", "city": "Mumbai", "locality": "Andheri East", "title": "1BHK in Prime Location", "bhk_type": "1BHK", "price_lakhs": 180.0, "area_sqft": 750, "price_per_sqft": 24000, "monthly_rent": 50000, "listing_age_days": 3, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_017", "city": "Mumbai", "locality": "Powai", "title": "3BHK Near University", "bhk_type": "3BHK", "price_lakhs": 260.0, "area_sqft": 1600, "price_per_sqft": 16250, "monthly_rent": 70000, "listing_age_days": 8, "nearby_metro": true, "source": "99Acres" },
  { "id": "COMP_018", "city": "Mumbai", "locality": "Mira Road", "title": "2BHK in New Development", "bhk_type": "2BHK", "price_lakhs": 190.0, "area_sqft": 1200, "price_per_sqft": 15833, "monthly_rent": 48000, "listing_age_days": 17, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_019", "city": "Mumbai", "locality": "Kharghar", "title": "3BHK in IT Hub", "bhk_type": "3BHK", "price_lakhs": 240.0, "area_sqft": 1500, "price_per_sqft": 16000, "monthly_rent": 65000, "listing_age_days": 15, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_020", "city": "Hyderabad", "locality": "Gachibowli", "title": "3BHK in IT Hub", "bhk_type": "3BHK", "price_lakhs": 145.0, "area_sqft": 1700, "price_per_sqft": 8529, "monthly_rent": 45000, "listing_age_days": 10, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_021", "city": "Hyderabad", "locality": "HITEC City", "title": "2BHK in IT Hub", "bhk_type": "2BHK", "price_lakhs": 110.0, "area_sqft": 1200, "price_per_sqft": 9167, "monthly_rent": 35000, "listing_age_days": 14, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_022", "city": "Hyderabad", "locality": "Kondapur", "title": "3BHK Near IT Hub", "bhk_type": "3BHK", "price_lakhs": 120.0, "area_sqft": 1500, "price_per_sqft": 8000, "monthly_rent": 40000, "listing_age_days": 6, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_023", "city": "Hyderabad", "locality": "Manikonda", "title": "2BHK in New Area", "bhk_type": "2BHK", "price_lakhs": 95.0, "area_sqft": 1000, "price_per_sqft": 9500, "monthly_rent": 30000, "listing_age_days": 18, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_024", "city": "Hyderabad", "locality": "Narsingi", "title": "3BHK Near IT Hub", "bhk_type": "3BHK", "price_lakhs": 105.0, "area_sqft": 1400, "price_per_sqft": 7500, "monthly_rent": 38000, "listing_age_days": 22, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_025", "city": "Hyderabad", "locality": "Miyapur", "title": "2BHK in Residential Area", "bhk_type": "2BHK", "price_lakhs": 85.0, "area_sqft": 1000, "price_per_sqft": 8500, "monthly_rent": 28000, "listing_age_days": 13, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_026", "city": "Noida", "locality": "Sector 62", "title": "3BHK in IT Hub", "bhk_type": "3BHK", "price_lakhs": 120.0, "area_sqft": 1500, "price_per_sqft": 8000, "monthly_rent": 40000, "listing_age_days": 9, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_027", "city": "Noida", "locality": "Sector 137", "title": "2BHK in Residential Area", "bhk_type": "2BHK", "price_lakhs": 95.0, "area_sqft": 1200, "price_per_sqft": 7917, "monthly_rent": 32000, "listing_age_days": 16, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_028", "city": "Noida", "locality": "Greater Noida West", "title": "3BHK Near IT Hub", "bhk_type": "3BHK", "price_lakhs": 105.0, "area_sqft": 1400, "price_per_sqft": 7500, "monthly_rent": 36000, "listing_age_days": 20, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_029", "city": "Noida", "locality": "Sector 150", "title": "2BHK in IT Hub", "bhk_type": "2BHK", "price_lakhs": 85.0, "area_sqft": 1000, "price_per_sqft": 8500, "monthly_rent": 30000, "listing_age_days": 11, "nearby_metro": true, "source": "Prestige Estates" },
  { "id": "COMP_030", "city": "Noida", "locality": "Expressway", "title": "3BHK Near IT Hub", "bhk_type": "3BHK", "price_lakhs": 110.0, "area_sqft": 1300, "price_per_sqft": 8462, "monthly_rent": 38000, "listing_age_days": 14, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_031", "city": "Chennai", "locality": "OMR", "title": "2BHK in IT Hub", "bhk_type": "2BHK", "price_lakhs": 95.0, "area_sqft": 1100, "price_per_sqft": 8636, "monthly_rent": 32000, "listing_age_days": 10, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_032", "city": "Chennai", "locality": "Perambur", "title": "3BHK in Residential Area", "bhk_type": "3BHK", "price_lakhs": 85.0, "area_sqft": 1300, "price_per_sqft": 6538, "monthly_rent": 28000, "listing_age_days": 18, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_033", "city": "Chennai", "locality": "Velachery", "title": "2BHK in IT Hub", "bhk_type": "2BHK", "price_lakhs": 105.0, "area_sqft": 1200, "price_per_sqft": 8750, "monthly_rent": 36000, "listing_age_days": 12, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_034", "city": "Chennai", "locality": "Sholinganallur", "title": "3BHK Near IT Hub", "bhk_type": "3BHK", "price_lakhs": 120.0, "area_sqft": 1400, "price_per_sqft": 8571, "monthly_rent": 40000, "listing_age_days": 8, "nearby_metro": true, "source": "MagicBricks" },
  { "id": "COMP_035", "city": "Chennai", "locality": "Medavakkam", "title": "2BHK in Residential Area", "bhk_type": "2BHK", "price_lakhs": 75.0, "area_sqft": 1000, "price_per_sqft": 7500, "monthly_rent": 26000, "listing_age_days": 24, "nearby_metro": false, "source": "MagicBricks" },
  { "id": "COMP_036", "city": "Chennai", "locality": "Anna Nagar", "title": "3BHK in Established Locality", "bhk_type": "3BHK", "price_lakhs": 100.0, "area_sqft": 1350, "price_per_sqft": 7407, "monthly_rent": 34000, "listing_age_days": 20, "nearby_metro": true, "source": "MagicBricks" },
];

const MOCK_RAG = [
  "Pune Metropolitan Region Development Authority (PMRDA) has approved the extension of Pune Metro Line 3 from Hinjewadi Phase 1 to Hinjewadi Phase 3, adding three new stations at Rajiv Gandhi Infotech Park Gate 1, Phase 2 Junction, and Maan Village. The project carries a capital outlay of Rs 2,840 crore and is scheduled for completion by Q3 2027. Properties within 600 metres of the proposed Phase 2 Junction station have already recorded a 9 to 12 percent price premium over comparable properties outside the catchment zone.",
  "Brihanmumbai Municipal Corporation has rezoned a 42-hectare parcel in Vikhroli East from industrial warehouse use to high-density mixed-use commercial under Development Plan 2034 amendments notified in October 2024. The revised Floor Space Index of 4.0 against the earlier 1.0 permits high-rise residential towers up to 40 floors. Adjacent residential localities of Powai and Kanjurmarg are forecast to see spillover demand growth of 15 to 20 percent over the next 36 months.",
  "Hyderabad Metro Rail Limited has received final clearance from the Telangana government for the Phase 2 extension connecting Raidurgam station on the Blue Line to the proposed Financial District terminus near Narsingi. The 8.4-kilometre corridor includes four new underground stations and is expected to be operational by Q1 2028. Residential micro-markets within one kilometre of the Narsingi interchange site have seen a 14 percent jump in new project launches since the announcement.",
  "Bangalore Metropolitan Region Development Authority issued a zoning notification rezoning a 110-hectare industrial belt along Sarjapur Road between Carmelram and Bellandur from light industrial to mixed-use residential and commercial. The change enables FSI of 3.5 and is expected to unlock approximately 18,000 new residential units by 2028. Immediate catchment localities Bellandur and Kadabeesanahalli have already recorded a 22 percent increase in land transaction volumes in the subsequent quarter.",
  "Greater Noida Industrial Development Authority has approved the Integrated Township Policy for Sector 12 Greater Noida West, permitting private developers to build integrated townships exceeding 50 hectares with a land use mix of 60 percent residential and 40 percent commercial. The policy is expected to attract Rs 4,200 crore in private investment and create 11,000 residential units over five years. The Aqua Metro Line terminus at Sector 137 is within 2.2 kilometres of the designated township zone.",
  "Tamil Nadu Industrial Development Corporation has notified the establishment of the Chennai Peripheral Ring Road Industrial Corridor along a 62-kilometre stretch from Poonamallee to Maraimalai Nagar passing through Sholinganallur and Medavakkam. The corridor includes designated IT and manufacturing SEZ clusters at three nodes. Residential localities within two kilometres of the Sholinganallur node are projected to benefit from 25,000 new knowledge-economy jobs by 2027.",
  "The Pune Municipal Corporation Smart City Mission has designated Kothrud and Erandwane as Priority Development Zones under the Pune Smart City Phase 3 plan, allocating Rs 780 crore for underground utility ducting, fibre-optic smart grid infrastructure, and pedestrian-priority streetscaping on 18 key roads.",
  "Navi Mumbai International Airport is on track for partial operations handling 10 million passengers annually by December 2025 under the CIDCO development authority master plan. TOD zone within 1.5 kilometres of the proposed airport metro station with permissible FSI of 5.0.",
  "Noida Authority has notified a Special Development Zone for the Film City project in Sector 21 Greater Noida covering 230 hectares. The integrated media and entertainment complex will house production studios. Sector 150 and Sector 168 have been repositioned to target entertainment industry professionals."
];

export default function App() {
  const [appState, setAppState] = useState('input'); // 'input' | 'analyzing' | 'hitl' | 'complete'
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Shared State Schema
  const [stateData, setStateData] = useState({
    thread_id: '',
    address: '',
    city: '',
    budget_lakhs: 100,
    bhk_type: '2BHK',
    investment_horizon_years: 5,
    comps: [],
    locality_insights: {},
    rag_context: '',
    roi_estimates: {},
    preliminary_score: 0,
    hitl_approved: false,
    approved_comps: [],
    analyst_notes: '',
    final_score: 0,
    report: {},
    stream_messages: []
  });

  // Telemetry Metrics Store
  const [telemetry, setTelemetry] = useState({
    total_latency_ms: 0,
    tool_calls: { search_properties: 0, calculate_roi: 0, get_locality_insights: 0, rag_search: 0 },
    rag_retrievals: 0,
    gemini_calls: 0,
    traces: []
  });

  // Polling ref/intervals
  const pollIntervalRef = useRef(null);

  // Helper to log telemetry trace
  const addTelemetryTrace = (name, detail, latency) => {
    const timestamp = new Date().toLocaleTimeString();
    setTelemetry(prev => {
      const updatedToolCalls = { ...prev.tool_calls };
      if (name in updatedToolCalls) {
        updatedToolCalls[name] += 1;
      } else if (name === 'rag_retrieval') {
        prev.rag_retrievals += 1;
      } else if (name === 'gemini_inference') {
        prev.gemini_calls += 1;
      }
      
      return {
        ...prev,
        total_latency_ms: prev.total_latency_ms + latency,
        tool_calls: updatedToolCalls,
        traces: [
          { timestamp, name, detail, latency },
          ...prev.traces
        ]
      };
    });
  };

  // Safe fetch telemetry summary from live backend
  const fetchLiveTelemetry = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/telemetry');
      if (res.ok) {
        const data = await res.json();
        setTelemetry(data);
      }
    } catch (e) {
      console.warn("Failed fetching live telemetry, falling back to cached local storage.", e);
    }
  };

  // Effect to clean up polling
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  // Polling fallback loop
  const startPolling = (thread_id) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    pollIntervalRef.current = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/analyze/status/${thread_id}`);
        if (!res.ok) throw new Error("Status API request failed.");

        const data = await res.json();
        // data matches: { stream_messages: [...], status: "running" | "awaiting_hitl" | "complete" }
        
        setStateData(prev => ({
          ...prev,
          stream_messages: data.stream_messages
        }));

        if (data.status === 'awaiting_hitl') {
          clearInterval(pollIntervalRef.current);
          
          // Re-fetch full active state parameters to populate HITL screen
          // We assume a GET or returning state from the last start is populated. Let's transition to HITL.
          // In live API, the thread state stores the preliminary variables.
          // Let's populate the local comps / preliminary score from state
          setAppState('hitl');
          setIsLoading(false);
          addTelemetryTrace('polling_check', 'Status transition to awaiting_hitl detected.', 45);
        } else if (data.status === 'complete') {
          clearInterval(pollIntervalRef.current);
          // Complete, we fetch the final completed details or telemetry
          setAppState('complete');
          setIsLoading(false);
          fetchLiveTelemetry();
        }
      } catch (err) {
        console.error("Polling error: ", err);
      }
    }, 1500);
  };

  // Submit Handler for PropertyInput
  const handleStartAnalysis = async (inputData) => {
    setIsLoading(true);
    setAppState('analyzing');
    
    const startTime = Date.now();
    const mockThreadId = 'thread_' + Math.random().toString(36).substr(2, 9);
    
    // Set initial configuration
    setStateData(prev => ({
      ...prev,
      ...inputData,
      thread_id: mockThreadId,
      stream_messages: []
    }));

    if (isLiveMode) {
      try {
        const res = await fetch('http://localhost:8000/api/analyze/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(inputData)
        });
        if (!res.ok) throw new Error("CORS or offline backend connection error.");
        
        const data = await res.json();
        // Response yields state params containing thread_id
        setStateData(prev => ({
          ...prev,
          thread_id: data.thread_id,
          comps: data.comps || [],
          preliminary_score: data.preliminary_score || 70,
          rag_context: data.rag_context || '',
          stream_messages: data.stream_messages || ["🏘️ Initiating live backend thread sequence..."]
        }));

        addTelemetryTrace('api_start', 'Invoked start_analysis node mapping.', Date.now() - startTime);
        
        // Begin status polling loop
        startPolling(data.thread_id);

      } catch (err) {
        console.error(err);
        alert("Unable to reach live backend at http://localhost:8000. Switching to Simulation Mode.");
        setIsLiveMode(false);
        simulateAnalysis(inputData, mockThreadId);
      }
    } else {
      simulateAnalysis(inputData, mockThreadId);
    }
  };

  // Mock Analysis Simulation State Machine
  const simulateAnalysis = (inputData, threadId) => {
    const timelines = [
      { msg: "🏘️ Fetching comparable properties and market data...", time: 1000 },
      { msg: "📋 Retrieving zoning laws and infrastructure master plans...", time: 2500 },
      { msg: "⚙️ Calculating preliminary growth score...", time: 4000 }
    ];

    // Filter MOCK_COMPS based on selected city
    const matchedComps = MOCK_COMPS.filter(
      c => c.city.toLowerCase() === inputData.city.toLowerCase()
    ).slice(0, 4);

    // Filter MOCK_RAG for matched city context
    const matchingRag = MOCK_RAG.find(
      r => r.toLowerCase().includes(inputData.city.toLowerCase())
    ) || "No specific zoning or infrastructure data found for this query.";

    // Calculate score
    const budgetFactor = Math.min(100, Math.max(20, (inputData.budget_lakhs / 500) * 100));
    const preliminary_score = Math.round(60 + (budgetFactor * 0.2) + (inputData.investment_horizon_years * 2));

    timelines.forEach((step, idx) => {
      setTimeout(() => {
        setStateData(prev => ({
          ...prev,
          stream_messages: [...prev.stream_messages, step.msg]
        }));
        
        // Log telemetry
        if (idx === 0) addTelemetryTrace('search_properties', `Retrieved ${matchedComps.length} comps for ${inputData.city}`, 180);
        if (idx === 1) addTelemetryTrace('rag_retrieval', `Queried zoning data collection`, 240);
        if (idx === 2) addTelemetryTrace('calculate_roi', `ROI estimates calculated. Score: ${preliminary_score}`, 110);

        // Transition to HITL
        if (idx === timelines.length - 1) {
          setTimeout(() => {
            setStateData(prev => ({
              ...prev,
              comps: matchedComps,
              preliminary_score: preliminary_score,
              rag_context: matchingRag
            }));
            setAppState('hitl');
            setIsLoading(false);
          }, 1200);
        }
      }, step.time);
    });
  };

  // Submit Handler for HITL Resume
  const handleResumeAnalysis = async (hitlData) => {
    setIsLoading(true);
    setAppState('analyzing');
    const startTime = Date.now();

    // Append Resume messages
    setStateData(prev => ({
      ...prev,
      approved_comps: hitlData.approved_comps,
      analyst_notes: hitlData.analyst_notes,
      stream_messages: [...prev.stream_messages, "✅ Analyst review received. Processing approved comparables..."]
    }));

    if (isLiveMode) {
      try {
        const payload = {
          thread_id: stateData.thread_id,
          approved_comps: hitlData.approved_comps,
          analyst_notes: hitlData.analyst_notes
        };
        const res = await fetch('http://localhost:8000/api/analyze/resume', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("Resume endpoint failed.");
        const finalData = await res.json();
        
        setStateData(prev => ({
          ...prev,
          final_score: finalData.final_score,
          report: finalData.report,
          stream_messages: finalData.stream_messages || [...prev.stream_messages, "📝 Generating investment analysis report...", "✅ Analysis sequence complete."]
        }));

        addTelemetryTrace('api_resume', 'Resumed engine compile.', Date.now() - startTime);
        setAppState('complete');
        setIsLoading(false);
        fetchLiveTelemetry();

      } catch (err) {
        console.error(err);
        alert("Error connecting with backend. Resuming mock calculation fallback.");
        simulateResume(hitlData);
      }
    } else {
      simulateResume(hitlData);
    }
  };

  // Mock Resume Simulation
  const simulateResume = (hitlData) => {
    const timelines = [
      { msg: "📊 Calculating final weighted investment score...", time: 1000 },
      { msg: "📝 Generating investment analysis report...", time: 2500 }
    ];

    timelines.forEach((step, idx) => {
      setTimeout(() => {
        setStateData(prev => ({
          ...prev,
          stream_messages: [...prev.stream_messages, step.msg]
        }));

        if (idx === 0) addTelemetryTrace('calculate_roi', 'Recalculating weighted metric matrix.', 95);
        if (idx === 1) addTelemetryTrace('gemini_inference', 'Gemini structured JSON parsing model completed.', 850);

        if (idx === timelines.length - 1) {
          setTimeout(() => {
            // Compute final score using selected comps count & analyst notes adjustments
            const modifier = hitlData.analyst_notes.toLowerCase().includes('bullish') || hitlData.analyst_notes.toLowerCase().includes('strong') ? 5 : 
                             hitlData.analyst_notes.toLowerCase().includes('risk') || hitlData.analyst_notes.toLowerCase().includes('concern') ? -5 : 0;
            
            const finalScore = Math.min(100, Math.max(0, stateData.preliminary_score + modifier));
            
            // Build mock structured JSON report
            const mockVerdict = finalScore >= 81 ? 'STRONG BUY' : finalScore >= 66 ? 'BUY' : finalScore >= 41 ? 'HOLD' : 'AVOID';
            const mockReport = {
              executive_summary: `The acquisition model for the property in ${stateData.city} is highly dependent on infrastructure integration. A final rating of ${finalScore}/100 indicates clear potential.`,
              growth_verdict: mockVerdict,
              growth_drivers: [
                `Active locality demand in ${stateData.city} with multiple tier-1 builders nearby.`,
                `Projected appreciation benefit anchored within target investment horizon.`,
                hitlData.analyst_notes ? `Analyst observation: "${hitlData.analyst_notes}"` : 'Favorable market comparable alignment.'
              ],
              risk_factors: [
                "Zoning restrictions in adjacent micro-markets.",
                "Short-term pricing volatility risk."
              ],
              financial_projections: {
                "1yr_appreciation_pct": Math.round(5 + (finalScore * 0.05)),
                "3yr_appreciation_pct": Math.round(18 + (finalScore * 0.15)),
                "5yr_appreciation_pct": Math.round(35 + (finalScore * 0.3)),
                "10yr_appreciation_pct": Math.round(80 + (finalScore * 0.75)),
                "recommended_exit_horizon": `${stateData.investment_horizon_years} Years`
              },
              comparable_analysis: `Analyzed ${hitlData.approved_comps.length} comparable properties matching targeted BHK values in ${stateData.city}. Mean valuation indices remain well within typical standard deviation bounds.`,
              infrastructure_impact: "RAG vector indices mapping zoning laws highlight positive proximity overlays matching metro corridor transit expansion lines.",
              final_recommendation: `Recommended to execute acquisition targeting key entry thresholds. Maintain standard hold timeline of ${stateData.investment_horizon_years} years.`
            };

            setStateData(prev => ({
              ...prev,
              final_score: finalScore,
              report: mockReport,
              stream_messages: [...prev.stream_messages, "✅ Analysis sequence complete."]
            }));

            setAppState('complete');
            setIsLoading(false);
          }, 1200);
        }
      }, step.time);
    });
  };

  const handleReset = () => {
    setAppState('input');
    setStateData({
      thread_id: '',
      address: '',
      city: 'Pune',
      budget_lakhs: 100,
      bhk_type: '2BHK',
      investment_horizon_years: 5,
      comps: [],
      locality_insights: {},
      rag_context: '',
      roi_estimates: {},
      preliminary_score: 0,
      hitl_approved: false,
      approved_comps: [],
      analyst_notes: '',
      final_score: 0,
      report: {},
      stream_messages: []
    });
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      padding: '20px'
    }}>
      
      {/* Luxury Terminal Header Navigation */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 24px',
        marginBottom: '40px',
        borderBottom: '1px solid var(--border-color)',
        background: 'rgba(10, 10, 15, 0.5)',
        backdropFilter: 'blur(8px)',
        borderRadius: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{
            fontSize: '1.4rem',
            fontFamily: 'var(--font-heading)',
            fontWeight: '800',
            background: 'linear-gradient(135deg, var(--primary-gold) 0%, var(--emerald) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '0.08em'
          }}>
            PropGrowth AI
          </span>
          <span style={{
            fontSize: '0.65rem',
            fontFamily: 'var(--font-mono)',
            color: 'rgba(255, 255, 255, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '2px 8px',
            borderRadius: '12px',
            letterSpacing: '0.1em'
          }}>
            v1.0.0-PROD
          </span>
        </div>

        {/* Dual Mode Switch Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{
            fontSize: '0.75rem',
            color: 'rgba(255, 255, 255, 0.5)',
            letterSpacing: '0.05em'
          }}>
            SYSTEM CONNECTION:
          </span>
          
          <button
            onClick={() => {
              if (appState !== 'input') {
                if (!confirm("Changing connection mode will reset the active compilation sequence. Proceed?")) return;
                handleReset();
              }
              setIsLiveMode(!isLiveMode);
            }}
            style={{
              background: isLiveMode ? 'rgba(16, 185, 129, 0.1)' : 'rgba(240, 180, 41, 0.1)',
              border: `1px solid ${isLiveMode ? 'var(--emerald)' : 'var(--primary-gold)'}`,
              color: isLiveMode ? 'var(--emerald)' : 'var(--primary-gold)',
              padding: '6px 16px',
              borderRadius: '6px',
              fontSize: '0.7rem',
              fontWeight: '700',
              fontFamily: 'var(--font-heading)',
              cursor: 'pointer',
              letterSpacing: '0.08em',
              transition: 'all 0.3s ease',
              boxShadow: `0 0 10px ${isLiveMode ? 'var(--emerald-glow)' : 'var(--primary-gold-glow)'}`
            }}
          >
            {isLiveMode ? 'LIVE API GATEWAY' : 'SIMULATION WORKSPACE'}
          </button>
        </div>
      </header>

      {/* Main Screen Router */}
      <main style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        {appState === 'input' && (
          <PropertyInput onSubmit={handleStartAnalysis} isLoading={isLoading} />
        )}
        
        {appState === 'analyzing' && (
          <div style={{ maxWidth: '650px', width: '100%', margin: '0 auto' }}>
            <h3 style={{
              textAlign: 'center',
              fontSize: '1rem',
              color: 'var(--primary-gold)',
              marginBottom: '20px',
              letterSpacing: '0.1em'
            }}>
              AGENT COGNITIVE COMPILE SEQUENCE IN PROGRESS
            </h3>
            <AgentThinking messages={stateData.stream_messages} />
          </div>
        )}

        {appState === 'hitl' && (
          <HitlVerification
            comps={stateData.comps}
            preliminaryScore={stateData.preliminary_score}
            onSubmit={handleResumeAnalysis}
            isLoading={isLoading}
          />
        )}

        {appState === 'complete' && (
          <InvestmentReport stateData={stateData} onReset={handleReset} />
        )}
      </main>

      {/* Observability Telemetry Drop-down drawer */}
      <TelemetryMetrics
        telemetryData={telemetry}
        isLiveMode={isLiveMode}
        onRefresh={isLiveMode ? fetchLiveTelemetry : null}
      />
    </div>
  );
}
