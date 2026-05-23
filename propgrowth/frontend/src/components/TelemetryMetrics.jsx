import React, { useState } from 'react';

export default function TelemetryMetrics({ telemetryData = {}, isLoading = false, isLiveMode = false, onRefresh }) {
  const [isOpen, setIsOpen] = useState(false);

  const {
    total_latency_ms = 0,
    tool_calls = { search_properties: 0, calculate_roi: 0, get_locality_insights: 0, rag_search: 0 },
    rag_retrievals = 0,
    gemini_calls = 0,
    traces = []
  } = telemetryData;

  const toggleAccordion = () => {
    setIsOpen(!isOpen);
    if (!isOpen && onRefresh) {
      onRefresh();
    }
  };

  return (
    <div className="glass-panel" style={{
      position: 'fixed',
      bottom: '16px',
      right: '16px',
      width: '380px',
      zIndex: 1000,
      background: 'rgba(10, 10, 15, 0.95)',
      border: '1px solid rgba(240, 180, 41, 0.25)',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.8)',
      overflow: 'hidden',
      transition: 'max-height 0.4s cubic-bezier(0.25, 0.8, 0.25, 1)',
      maxHeight: isOpen ? '500px' : '48px'
    }}>
      {/* Accordion Toggle Header */}
      <div
        onClick={toggleAccordion}
        style={{
          padding: '12px 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          userSelect: 'none',
          background: 'rgba(255, 255, 255, 0.02)',
          borderBottom: isOpen ? '1px solid rgba(255, 255, 255, 0.08)' : 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: isLiveMode ? 'var(--emerald)' : 'var(--primary-gold)',
            boxShadow: `0 0 6px ${isLiveMode ? 'var(--emerald)' : 'var(--primary-gold)'}`
          }} />
          <span style={{
            fontSize: '0.75rem',
            fontFamily: 'var(--font-heading)',
            fontWeight: '700',
            letterSpacing: '0.08em',
            color: '#fff'
          }}>
            SYSTEM TELEMETRY
          </span>
          <span style={{
            fontSize: '0.6rem',
            background: 'rgba(255, 255, 255, 0.1)',
            padding: '2px 6px',
            borderRadius: '4px',
            color: 'rgba(255,255,255,0.6)'
          }}>
            {isLiveMode ? 'LIVE API' : 'MOCK'}
          </span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {onRefresh && isOpen && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRefresh();
              }}
              disabled={isLoading}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--primary-gold)',
                cursor: 'pointer',
                fontSize: '0.7rem',
                fontWeight: '600',
                padding: '2px 4px'
              }}
            >
              Refresh
            </button>
          )}
          <span style={{
            fontSize: '0.8rem',
            color: 'rgba(255, 255, 255, 0.4)',
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s ease'
          }}>
            ▼
          </span>
        </div>
      </div>

      {/* Accordion Content */}
      {isOpen && (
        <div style={{
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          height: '450px',
          overflowY: 'auto',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.8rem'
        }}>
          {/* Latency & Summary */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
            background: 'rgba(255, 255, 255, 0.02)',
            padding: '12px',
            borderRadius: '6px',
            border: '1px solid rgba(255, 255, 255, 0.04)'
          }}>
            <div>
              <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: '0.65rem' }}>TOTAL LATENCY</div>
              <div style={{ color: 'var(--primary-gold)', fontSize: '1rem', fontWeight: '700', marginTop: '2px' }}>
                {total_latency_ms} ms
              </div>
            </div>
            <div>
              <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: '0.65rem' }}>GEMINI CALLS</div>
              <div style={{ color: 'var(--emerald)', fontSize: '1rem', fontWeight: '700', marginTop: '2px' }}>
                {gemini_calls}
              </div>
            </div>
          </div>

          {/* Tool Calls Counters */}
          <div>
            <div style={{
              fontSize: '0.65rem',
              color: 'rgba(255, 255, 255, 0.4)',
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Active Processing Call Traces
            </div>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                <span style={{ color: 'rgba(255,255,255,0.6)' }}>search_properties</span>
                <span className="number-metric" style={{ color: '#fff' }}>{tool_calls.search_properties}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                <span style={{ color: 'rgba(255,255,255,0.6)' }}>calculate_roi</span>
                <span className="number-metric" style={{ color: '#fff' }}>{tool_calls.calculate_roi}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                <span style={{ color: 'rgba(255,255,255,0.6)' }}>get_locality_insights</span>
                <span className="number-metric" style={{ color: '#fff' }}>{tool_calls.get_locality_insights}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                <span style={{ color: 'rgba(255,255,255,0.6)' }}>rag_retrievals</span>
                <span className="number-metric" style={{ color: '#fff' }}>{rag_retrievals}</span>
              </div>
            </div>
          </div>

          {/* Trace details */}
          <div>
            <div style={{
              fontSize: '0.65rem',
              color: 'rgba(255, 255, 255, 0.4)',
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Telemetry Trace Logs
            </div>
            
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              maxHeight: '180px',
              overflowY: 'auto',
              background: 'rgba(0, 0, 0, 0.2)',
              borderRadius: '4px',
              padding: '8px'
            }}>
              {traces.length > 0 ? (
                traces.map((trace, index) => (
                  <div
                    key={index}
                    style={{
                      fontSize: '0.7rem',
                      lineHeight: '1.4',
                      padding: '4px 0',
                      borderBottom: index < traces.length - 1 ? '1px solid rgba(255,255,255,0.03)' : 'none',
                      color: 'rgba(255,255,255,0.8)'
                    }}
                  >
                    <span style={{ color: 'var(--primary-gold)' }}>[{trace.timestamp}]</span>{' '}
                    <span style={{ color: 'var(--emerald)' }}>{trace.name}</span>{' '}
                    <span>{trace.detail}</span>{' '}
                    <span style={{ color: 'rgba(255, 255, 255, 0.3)' }}>({trace.latency}ms)</span>
                  </div>
                ))
              ) : (
                <div style={{
                  color: 'rgba(255,255,255,0.2)',
                  fontSize: '0.7rem',
                  padding: '10px 0',
                  textAlign: 'center'
                }}>
                  No trace data recorded.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
