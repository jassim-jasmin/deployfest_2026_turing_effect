import React, { useState, useEffect } from 'react';

export default function AgentThinking({ messages = [] }) {
  const [typedLines, setTypedLines] = useState([]);
  const [activeLine, setActiveLine] = useState('');
  const [activeIdx, setActiveIdx] = useState(-1);

  useEffect(() => {
    if (messages.length === 0) {
      setTypedLines([]);
      setActiveLine('');
      setActiveIdx(-1);
      return;
    }

    // If a new message is appended
    const lastIdx = messages.length - 1;
    if (lastIdx > activeIdx) {
      // Put previous completed lines
      const prevLines = messages.slice(0, lastIdx);
      setTypedLines(prevLines);
      
      // Start typing the new line
      const targetText = messages[lastIdx];
      setActiveIdx(lastIdx);
      setActiveLine('');
      
      let charIdx = 0;
      const interval = setInterval(() => {
        if (charIdx < targetText.length) {
          setActiveLine(targetText.slice(0, charIdx + 1));
          charIdx++;
        } else {
          clearInterval(interval);
          setTypedLines(prev => [...prev, targetText]);
          setActiveLine('');
        }
      }, 35); // 35ms per character for snappy but satisfying feel
      
      return () => clearInterval(interval);
    }
  }, [messages, activeIdx]);

  return (
    <div className="glass-panel scanline" style={{
      fontFamily: 'var(--font-mono)',
      padding: '24px',
      height: '350px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-start',
      overflowY: 'auto',
      position: 'relative',
      background: 'rgba(10, 10, 15, 0.7)',
      border: '1px solid rgba(240, 180, 41, 0.15)',
      boxShadow: 'inset 0 0 20px rgba(0, 0, 0, 0.8), 0 0 15px rgba(240, 180, 41, 0.05)'
    }}>
      {/* Header bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingBottom: '12px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
        marginBottom: '16px',
        fontSize: '0.7rem',
        color: 'rgba(255, 255, 255, 0.4)',
        letterSpacing: '0.1em'
      }}>
        <span>PROPGROW_COGNITIVE_ENGINE // LIVE_TRACE</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: 'var(--primary-gold)',
            boxShadow: '0 0 8px var(--primary-gold)',
            animation: 'pulse 1.5s infinite'
          }} />
          <span>ACTIVE</span>
        </div>
      </div>

      {/* Terminal log lines */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        fontSize: '0.9rem',
        lineHeight: '1.4',
        color: '#d1d5db',
        textAlign: 'left'
      }}>
        {typedLines.map((line, i) => (
          <div key={i} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
            <span style={{ color: 'rgba(255,255,255,0.25)', fontSize: '0.75rem', marginTop: '3px' }}>
              [{String(i + 1).padStart(3, '0')}]
            </span>
            <span>{line}</span>
          </div>
        ))}
        
        {activeLine && (
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', color: '#fff' }}>
            <span style={{ color: 'rgba(255,255,255,0.25)', fontSize: '0.75rem', marginTop: '3px' }}>
              [{String(typedLines.length + 1).padStart(3, '0')}]
            </span>
            <span>
              {activeLine}
              <span className="blinking-cursor">_</span>
            </span>
          </div>
        )}

        {messages.length === 0 && (
          <div style={{
            color: 'rgba(255,255,255,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '200px',
            fontSize: '0.85rem'
          }}>
            <span>Awaiting sequence execution instructions...</span>
          </div>
        )}
      </div>

      <style>{`
        .blinking-cursor {
          animation: blink 0.8s infinite;
          color: var(--primary-gold);
          font-weight: bold;
        }
        @keyframes blink {
          0%, 100% { opacity: 0; }
          50% { opacity: 1; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}
