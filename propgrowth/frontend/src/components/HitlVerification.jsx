import React, { useState } from 'react';
import GrowthScoreRing from './GrowthScoreRing';

export default function HitlVerification({ comps = [], preliminaryScore = 0, onSubmit, isLoading }) {
  // Store checked state for each comp ID. Start with all comps checked by default.
  const [selectedCompIds, setSelectedCompIds] = useState(
    () => comps.reduce((acc, comp) => ({ ...acc, [comp.id]: true }), {})
  );
  
  const [analystNotes, setAnalystNotes] = useState('');

  const handleToggleComp = (id) => {
    setSelectedCompIds(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Gather all comps that are checked
    const approvedComps = comps.filter(comp => selectedCompIds[comp.id]);
    
    onSubmit({
      approved_comps: approvedComps,
      analyst_notes: analystNotes
    });
  };

  const selectedCount = Object.values(selectedCompIds).filter(Boolean).length;

  return (
    <div className="glass-panel" style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '40px',
      position: 'relative'
    }}>
      {/* Top glowing boundary */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '4px',
        background: 'linear-gradient(90deg, var(--emerald), var(--primary-gold))'
      }} />

      <div style={{
        textAlign: 'center',
        marginBottom: '35px'
      }}>
        <h2 style={{
          margin: '0 0 8px 0',
          fontSize: '1.8rem',
          color: '#fff',
          letterSpacing: '0.05em'
        }}>
          Human-in-the-Loop Verification
        </h2>
        <p style={{
          margin: 0,
          fontSize: '0.85rem',
          color: 'rgba(255, 255, 255, 0.5)',
          letterSpacing: '0.05em'
        }}>
          REVIEW PRELIMINARY SCORE & SELECT VALID PROPERTY COMPARABLES
        </p>
      </div>

      <div className="terminal-grid" style={{ gap: '40px' }}>
        {/* Left Pane: SVG Dial and metrics */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          borderRight: '1px solid rgba(255, 255, 255, 0.05)',
          paddingRight: '20px'
        }}>
          <GrowthScoreRing score={preliminaryScore} size={220} label="PRELIMINARY SCORE" />
          
          <div className="glass-panel" style={{
            marginTop: '25px',
            padding: '20px',
            width: '100%',
            maxWidth: '350px',
            background: 'rgba(255, 255, 255, 0.01)',
            textAlign: 'center'
          }}>
            <h4 style={{
              margin: '0 0 10px 0',
              fontSize: '0.75rem',
              color: 'var(--primary-gold)',
              letterSpacing: '0.1em'
            }}>
              INITIAL ANALYSIS COMPLETE
            </h4>
            <p style={{
              margin: 0,
              fontSize: '0.85rem',
              color: 'rgba(255, 255, 255, 0.6)',
              lineHeight: '1.5'
            }}>
              The AI engine completed zoning queries and RAG retrieval. Please verify the market comparables to resume the final weighted scoring process.
            </p>
          </div>
        </div>

        {/* Right Pane: Checklist and Feedback */}
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: '100%' }}>
            
            {/* Checklist */}
            <div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px'
              }}>
                <label style={{
                  fontSize: '0.75rem',
                  color: 'var(--primary-gold)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  fontWeight: '600'
                }}>
                  Comparable Market Properties ({selectedCount} / {comps.length} Selected)
                </label>
                <span style={{ fontSize: '0.7rem', color: 'rgba(255, 255, 255, 0.4)' }}>
                  UNCHECK TO DISCARD OUTLIERS
                </span>
              </div>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                maxHeight: '260px',
                overflowY: 'auto',
                paddingRight: '8px'
              }}>
                {comps.map((comp) => {
                  const isChecked = !!selectedCompIds[comp.id];
                  return (
                    <div
                      key={comp.id}
                      onClick={() => handleToggleComp(comp.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '16px',
                        padding: '14px 18px',
                        background: isChecked ? 'rgba(255, 255, 255, 0.03)' : 'rgba(255, 255, 255, 0.01)',
                        border: `1px solid ${isChecked ? 'rgba(240, 180, 41, 0.25)' : 'rgba(255, 255, 255, 0.04)'}`,
                        borderRadius: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        userSelect: 'none'
                      }}
                    >
                      {/* Checkbox circle */}
                      <div style={{
                        width: '18px',
                        height: '18px',
                        borderRadius: '4px',
                        border: `2px solid ${isChecked ? 'var(--primary-gold)' : 'rgba(255,255,255,0.3)'}`,
                        background: isChecked ? 'var(--primary-gold)' : 'transparent',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.2s ease'
                      }}>
                        {isChecked && (
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#0a0a0f" strokeWidth="4">
                            <path d="M20 6L9 17L4 12" />
                          </svg>
                        )}
                      </div>

                      {/* Details */}
                      <div style={{ flexGrow: 1 }}>
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          marginBottom: '4px'
                        }}>
                          <span style={{ fontSize: '0.9rem', fontWeight: '600', color: '#fff' }}>
                            {comp.title}
                          </span>
                          <span className="number-metric" style={{
                            fontSize: '0.9rem',
                            fontWeight: '600',
                            color: 'var(--primary-gold)'
                          }}>
                            ₹{comp.price_lakhs} Lakhs
                          </span>
                        </div>
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          fontSize: '0.75rem',
                          color: 'rgba(255, 255, 255, 0.5)'
                        }}>
                          <span>{comp.locality}, {comp.city} ({comp.bhk_type})</span>
                          <span>{comp.area_sqft} sqft | {comp.source}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Comments / Analyst notes */}
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
                Analyst Notes / Ground Truth Context
              </label>
              <textarea
                className="luxury-input"
                placeholder="Enter custom sentiment override keys: e.g. 'Strong location, bullish outlook on nearby IT corridor expansion, potential metro connectivity benefit...'"
                rows="3"
                value={analystNotes}
                onChange={(e) => setAnalystNotes(e.target.value)}
                disabled={isLoading}
                style={{
                  resize: 'none',
                  fontSize: '0.85rem',
                  lineHeight: '1.5'
                }}
              />
              <p style={{
                margin: '4px 0 0 0',
                fontSize: '0.65rem',
                color: 'rgba(255, 255, 255, 0.4)',
                fontStyle: 'italic'
              }}>
                Hint: Keywords like 'bullish', 'strong', 'good' trigger positive adjustment. 'risk', 'overpriced', 'concern' trigger negative adjustment.
              </p>
            </div>

            {/* Submit resume triggers */}
            <button
              type="submit"
              className="btn-primary"
              disabled={isLoading || selectedCount === 0}
              style={{
                marginTop: 'auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px'
              }}
            >
              {isLoading ? (
                <>
                  <div className="spinner" />
                  <span>Recalculating score & generating final report...</span>
                </>
              ) : (
                <span>Resume Analysis & Finalize Report</span>
              )}
            </button>
          </form>
        </div>
      </div>
      
      <style>{`
        .spinner {
          width: 18px;
          height: 18px;
          border: 2px solid rgba(10, 10, 15, 0.3);
          border-top-color: #0a0a0f;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
