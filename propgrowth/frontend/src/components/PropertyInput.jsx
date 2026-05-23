import React, { useState } from 'react';

export default function PropertyInput({ onSubmit, isLoading }) {
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('Pune');
  const [budget, setBudget] = useState(100); // in Lakhs
  const [bhk, setBhk] = useState('2BHK');
  const [horizon, setHorizon] = useState(5); // in years
  
  const cities = ['Pune', 'Bangalore', 'Mumbai', 'Hyderabad', 'Noida', 'Chennai'];
  const bhkOptions = ['1BHK', '2BHK', '3BHK', '4BHK+'];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!address.trim()) {
      alert('Please enter a valid property address.');
      return;
    }
    if (budget <= 0 || budget > 500) {
      alert('Budget must be between ₹1 Lakh and ₹500 Lakhs.');
      return;
    }
    onSubmit({
      address,
      city,
      budget_lakhs: parseFloat(budget),
      bhk_type: bhk,
      investment_horizon_years: parseInt(horizon)
    });
  };

  return (
    <div className="glass-panel glass-panel-glow" style={{
      maxWidth: '650px',
      margin: '0 auto',
      padding: '40px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Decorative luxury gradient block */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '4px',
        background: 'linear-gradient(90deg, var(--primary-gold), var(--emerald), var(--primary-gold))'
      }} />

      <h2 style={{
        margin: '0 0 10px 0',
        fontSize: '1.8rem',
        color: '#fff',
        textAlign: 'center',
        background: 'linear-gradient(135deg, #fff 0%, var(--primary-gold) 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        PropGrowth AI Terminal
      </h2>
      <p style={{
        margin: '0 0 35px 0',
        fontSize: '0.9rem',
        color: 'rgba(255, 255, 255, 0.6)',
        textAlign: 'center',
        letterSpacing: '0.05em'
      }}>
        ENTER TARGET ACQUISITION PARAMETERS
      </p>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Address */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontSize: '0.75rem',
            color: 'var(--primary-gold)',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            fontWeight: '600'
          }}>
            Property Address / Locality
          </label>
          <input
            type="text"
            className="luxury-input"
            placeholder="e.g. Hinjewadi Phase 2, near IT Park"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            disabled={isLoading}
            required
          />
        </div>

        {/* City & Budget */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontSize: '0.75rem',
              color: 'var(--primary-gold)',
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              fontWeight: '600'
            }}>
              Target City
            </label>
            <select
              className="luxury-input luxury-select"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              disabled={isLoading}
            >
              {cities.map(c => (
                <option key={c} value={c} style={{ background: '#0a0a0f', color: '#fff' }}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontSize: '0.75rem',
              color: 'var(--primary-gold)',
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              fontWeight: '600'
            }}>
              Budget (₹ Lakhs)
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="number"
                min="1"
                max="500"
                className="luxury-input number-metric"
                placeholder="Budget in Lakhs"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                disabled={isLoading}
                style={{ paddingRight: '45px' }}
                required
              />
              <span style={{
                position: 'absolute',
                right: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '0.85rem',
                color: 'rgba(255, 255, 255, 0.4)',
                pointerEvents: 'none'
              }}>
                Lakhs
              </span>
            </div>
          </div>
        </div>

        {/* BHK Toggle Selection */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontSize: '0.75rem',
            color: 'var(--primary-gold)',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            fontWeight: '600'
          }}>
            BHK Configuration
          </label>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '10px',
            background: 'rgba(255,255,255,0.02)',
            padding: '4px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)'
          }}>
            {bhkOptions.map(option => (
              <button
                key={option}
                type="button"
                onClick={() => setBhk(option)}
                disabled={isLoading}
                style={{
                  background: bhk === option ? 'var(--primary-gold)' : 'transparent',
                  color: bhk === option ? '#0a0a0f' : 'rgba(255,255,255,0.7)',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '10px 0',
                  cursor: 'pointer',
                  fontWeight: '700',
                  fontFamily: 'var(--font-heading)',
                  fontSize: '0.8rem',
                  transition: 'all 0.25s ease'
                }}
              >
                {option}
              </button>
            ))}
          </div>
        </div>

        {/* Horizon slider */}
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '4px',
            fontSize: '0.75rem',
            color: 'var(--primary-gold)',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            fontWeight: '600'
          }}>
            <span>Investment Horizon</span>
            <span className="number-metric" style={{ color: '#fff', fontSize: '0.85rem' }}>
              {horizon} Years
            </span>
          </div>
          <input
            type="range"
            min="1"
            max="10"
            className="luxury-range"
            value={horizon}
            onChange={(e) => setHorizon(e.target.value)}
            disabled={isLoading}
          />
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '0.65rem',
            color: 'rgba(255, 255, 255, 0.4)',
            marginTop: '-5px'
          }}>
            <span>1 Year</span>
            <span>5 Years</span>
            <span>10 Years</span>
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading}
          style={{
            marginTop: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px'
          }}
        >
          {isLoading ? (
            <>
              <div style={{
                width: '18px',
                height: '18px',
                border: '2px solid rgba(10, 10, 15, 0.3)',
                borderTopColor: '#0a0a0f',
                borderRadius: '50%',
                animation: 'spin 0.8s linear infinite'
              }} />
              <span>Analyzing Target...</span>
            </>
          ) : (
            <span>Initiate Analysis Sequence</span>
          )}
        </button>

      </form>
      
      {/* Keyframe animation for spinner */}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
