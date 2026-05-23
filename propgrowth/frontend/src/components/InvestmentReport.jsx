import React from 'react';
import GrowthScoreRing from './GrowthScoreRing';

export default function InvestmentReport({ stateData, onReset }) {
  const {
    final_score = 75,
    report = {},
    rag_context = '',
    address = '',
    city = '',
    budget_lakhs = 0,
    bhk_type = '',
    investment_horizon_years = 5
  } = stateData;

  const {
    executive_summary = 'No summary available.',
    growth_verdict = 'HOLD',
    growth_drivers = [],
    risk_factors = [],
    financial_projections = {},
    comparable_analysis = '',
    infrastructure_impact = '',
    final_recommendation = ''
  } = report;

  // Verdict style mapper
  const getVerdictStyle = (verdict) => {
    switch (verdict?.toUpperCase()) {
      case 'STRONG BUY':
        return { color: 'var(--emerald)', bg: 'rgba(16, 185, 129, 0.08)', border: 'var(--emerald)' };
      case 'BUY':
        return { color: 'var(--emerald)', bg: 'rgba(16, 185, 129, 0.04)', border: 'rgba(16, 185, 129, 0.5)' };
      case 'HOLD':
        return { color: 'var(--primary-gold)', bg: 'rgba(240, 180, 41, 0.08)', border: 'var(--primary-gold)' };
      case 'AVOID':
      default:
        return { color: 'var(--crimson)', bg: 'rgba(239, 68, 68, 0.08)', border: 'var(--crimson)' };
    }
  };

  const verdictStyle = getVerdictStyle(growth_verdict);

  // Projections values
  const projections = [
    { label: '1 Year', val: financial_projections?.['1yr_appreciation_pct'] || 0 },
    { label: '3 Years', val: financial_projections?.['3yr_appreciation_pct'] || 0 },
    { label: '5 Years', val: financial_projections?.['5yr_appreciation_pct'] || 0 },
    { label: '10 Years', val: financial_projections?.['10yr_appreciation_pct'] || 0 },
  ];

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '30px',
      paddingBottom: '60px'
    }}>
      
      {/* Header Summary Dashboard Card */}
      <div className="glass-panel" style={{
        padding: '30px',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: 'linear-gradient(90deg, var(--primary-gold), var(--emerald))'
        }} />

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '20px'
        }}>
          <div>
            <span style={{
              fontSize: '0.75rem',
              color: 'var(--primary-gold)',
              letterSpacing: '0.15em',
              fontWeight: '600'
            }}>
              INVESTMENT EVALUATION MATRIX
            </span>
            <h1 style={{
              margin: '6px 0 2px 0',
              fontSize: '2rem',
              color: '#fff'
            }}>
              {city} ACQUISITION
            </h1>
            <p style={{
              margin: 0,
              fontSize: '0.9rem',
              color: 'rgba(255, 255, 255, 0.6)'
            }}>
              {address} | {bhk_type} | Budget ₹{budget_lakhs} Lakhs
            </p>
          </div>

          <button onClick={onReset} className="btn-secondary" style={{
            padding: '10px 20px',
            fontSize: '0.75rem',
            alignSelf: 'center'
          }}>
            Analyze Another Property
          </button>
        </div>

        {/* Inner Grid for Quick Status */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '24px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '30px',
            background: 'rgba(255, 255, 255, 0.01)',
            border: '1px solid rgba(255, 255, 255, 0.03)',
            borderRadius: '10px',
            padding: '24px'
          }}>
            <div style={{ flexShrink: 0, margin: '0 auto' }}>
              <GrowthScoreRing score={final_score} size={160} label="FINAL SCORE" />
            </div>

            <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.4)', letterSpacing: '0.1em' }}>
                  DECISION VERDICT:
                </span>
                <span style={{
                  padding: '4px 12px',
                  borderRadius: '4px',
                  border: `1px solid ${verdictStyle.border}`,
                  color: verdictStyle.color,
                  background: verdictStyle.bg,
                  fontWeight: '700',
                  fontSize: '0.8rem',
                  fontFamily: 'var(--font-heading)',
                  letterSpacing: '0.05em'
                }}>
                  {growth_verdict}
                </span>
              </div>
              <p style={{
                margin: 0,
                fontSize: '0.95rem',
                lineHeight: '1.6',
                color: '#e2e8f0'
              }}>
                {executive_summary}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Breakdown Section */}
      <div className="terminal-grid" style={{ gap: '30px' }}>
        
        {/* Drivers and Risks Panel */}
        <div className="glass-panel" style={{ padding: '30px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div>
            <h3 style={{
              margin: '0 0 16px 0',
              fontSize: '1rem',
              color: 'var(--primary-gold)',
              borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
              paddingBottom: '8px'
            }}>
              Primary Growth Drivers
            </h3>
            <ul style={{
              listStyle: 'none',
              padding: 0,
              margin: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}>
              {growth_drivers.map((driver, idx) => (
                <li key={idx} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  fontSize: '0.9rem',
                  color: '#d1d5db',
                  lineHeight: '1.4'
                }}>
                  <span style={{ color: 'var(--emerald)', fontSize: '1.1rem', lineHeight: '1' }}>▲</span>
                  <span>{driver}</span>
                </li>
              ))}
              {growth_drivers.length === 0 && (
                <li style={{ color: 'rgba(255,255,255,0.3)', fontStyle: 'italic', fontSize: '0.85rem' }}>
                  No explicit drivers identified.
                </li>
              )}
            </ul>
          </div>

          <div>
            <h3 style={{
              margin: '0 0 16px 0',
              fontSize: '1rem',
              color: 'var(--crimson)',
              borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
              paddingBottom: '8px'
            }}>
              Operational Threats & Risks
            </h3>
            <ul style={{
              listStyle: 'none',
              padding: 0,
              margin: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}>
              {risk_factors.map((risk, idx) => (
                <li key={idx} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  fontSize: '0.9rem',
                  color: '#d1d5db',
                  lineHeight: '1.4'
                }}>
                  <span style={{ color: 'var(--crimson)', fontSize: '1.1rem', lineHeight: '1' }}>▼</span>
                  <span>{risk}</span>
                </li>
              ))}
              {risk_factors.length === 0 && (
                <li style={{ color: 'rgba(255,255,255,0.3)', fontStyle: 'italic', fontSize: '0.85rem' }}>
                  No high-impact threats flagged.
                </li>
              )}
            </ul>
          </div>
        </div>

        {/* Projections Visual Chart Panel */}
        <div className="glass-panel" style={{ padding: '30px', display: 'flex', flexDirection: 'column', justifyBetween: 'space-between' }}>
          <div>
            <h3 style={{
              margin: '0 0 4px 0',
              fontSize: '1rem',
              color: 'var(--primary-gold)'
            }}>
              Financial Appreciation Projections
            </h3>
            <p style={{
              margin: '0 0 24px 0',
              fontSize: '0.75rem',
              color: 'rgba(255, 255, 255, 0.4)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              PROJECTED PERCENTAGE COMPOUND GROWTH
            </p>

            {/* Custom Bar Projections */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '20px',
              padding: '10px 0'
            }}>
              {projections.map((p, idx) => {
                // Find maximum projection to scale relatively (default max is 100% or standard range)
                const valNum = parseFloat(p.val) || 0;
                const percentage = Math.min(100, Math.max(0, valNum));
                return (
                  <div key={idx}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: '6px',
                      fontSize: '0.85rem'
                    }}>
                      <span style={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: '600' }}>
                        {p.label}
                      </span>
                      <span className="number-metric" style={{ color: 'var(--emerald)', fontWeight: '700' }}>
                        +{valNum}%
                      </span>
                    </div>

                    {/* Progress Track */}
                    <div style={{
                      width: '100%',
                      height: '10px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderRadius: '5px',
                      overflow: 'hidden',
                      border: '1px solid rgba(255,255,255,0.05)'
                    }}>
                      {/* Bar Fill */}
                      <div style={{
                        width: `${percentage}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, var(--primary-gold) 0%, var(--emerald) 100%)',
                        boxShadow: '0 0 8px var(--emerald-glow)',
                        borderRadius: '5px',
                        transition: 'width 1s cubic-bezier(0.25, 0.8, 0.25, 1)'
                      }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{
            marginTop: '25px',
            padding: '16px',
            background: 'rgba(240, 180, 41, 0.03)',
            border: '1px solid rgba(240, 180, 41, 0.12)',
            borderRadius: '8px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{ fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.5)', letterSpacing: '0.05em' }}>
              RECOMMENDED HOLD EXIT HORIZON:
            </span>
            <span className="number-metric" style={{
              fontSize: '1rem',
              fontWeight: '700',
              color: 'var(--primary-gold)',
              textShadow: '0 0 10px rgba(240, 180, 41, 0.2)'
            }}>
              {financial_projections?.recommended_exit_horizon || `${investment_horizon_years} Years`}
            </span>
          </div>
        </div>
      </div>

      {/* RAG Context Grounding & Analysis Comments */}
      <div className="glass-panel" style={{ padding: '30px' }}>
        <h3 style={{
          margin: '0 0 16px 0',
          fontSize: '1rem',
          color: 'var(--primary-gold)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          paddingBottom: '8px'
        }}>
          Zoning & Regulatory Grounding Context
        </h3>
        
        <div style={{
          maxHeight: '200px',
          overflowY: 'auto',
          background: 'rgba(0, 0, 0, 0.2)',
          border: '1px solid rgba(255, 255, 255, 0.04)',
          borderRadius: '8px',
          padding: '16px',
          fontSize: '0.85rem',
          lineHeight: '1.6',
          color: '#abb2bf',
          fontFamily: 'var(--font-mono)',
          whiteSpace: 'pre-wrap',
          textAlign: 'left'
        }}>
          {rag_context || 'No grounding context retrieved.'}
        </div>
      </div>

      {/* Comparable Properties and Final Recommendation Panel */}
      <div className="glass-panel" style={{ padding: '30px' }}>
        <h3 style={{
          margin: '0 0 16px 0',
          fontSize: '1rem',
          color: 'var(--primary-gold)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          paddingBottom: '8px'
        }}>
          Final Strategic Recommendation
        </h3>
        <p style={{
          margin: '0 0 20px 0',
          fontSize: '0.95rem',
          lineHeight: '1.6',
          color: '#e2e8f0'
        }}>
          {final_recommendation || 'No custom recommendation statement generated.'}
        </p>

        {comparable_analysis && (
          <div style={{ marginTop: '20px' }}>
            <h4 style={{
              margin: '0 0 8px 0',
              fontSize: '0.85rem',
              color: '#fff',
              letterSpacing: '0.05em'
            }}>
              Market Comparables Synopsis:
            </h4>
            <p style={{
              margin: 0,
              fontSize: '0.9rem',
              lineHeight: '1.5',
              color: 'rgba(255, 255, 255, 0.6)'
            }}>
              {comparable_analysis}
            </p>
          </div>
        )}

        {infrastructure_impact && (
          <div style={{ marginTop: '20px' }}>
            <h4 style={{
              margin: '0 0 8px 0',
              fontSize: '0.85rem',
              color: '#fff',
              letterSpacing: '0.05em'
            }}>
              Infrastructure Integration Impact:
            </h4>
            <p style={{
              margin: 0,
              fontSize: '0.9rem',
              lineHeight: '1.5',
              color: 'rgba(255, 255, 255, 0.6)'
            }}>
              {infrastructure_impact}
            </p>
          </div>
        )}
      </div>

    </div>
  );
}
