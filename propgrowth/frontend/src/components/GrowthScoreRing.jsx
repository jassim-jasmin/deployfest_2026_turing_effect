import React, { useEffect, useState } from 'react';

export default function GrowthScoreRing({ score = 0, size = 180, label = 'Growth Score' }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  
  useEffect(() => {
    // Animate transition to target score on mount/update
    const duration = 1000; // 1s
    const steps = 30;
    const stepTime = duration / steps;
    let step = 0;
    
    const interval = setInterval(() => {
      step++;
      const progress = step / steps;
      // Easing out quadratic
      const easeProgress = progress * (2 - progress);
      const current = Math.round(easeProgress * score);
      
      setAnimatedScore(current);
      
      if (step >= steps) {
        clearInterval(interval);
        setAnimatedScore(score);
      }
    }, stepTime);
    
    return () => clearInterval(interval);
  }, [score]);

  // Color mapping based on thresholds
  // 0-40 crimson, 41-65 amber, 66-80 gold, 81-100 emerald
  const getColorScheme = (val) => {
    if (val <= 40) {
      return {
        color: 'var(--crimson)',
        glow: 'var(--crimson-glow)',
        label: 'CRITICAL RISK',
      };
    } else if (val <= 65) {
      return {
        color: 'var(--amber)',
        glow: 'var(--amber-glow)',
        label: 'MODERATE APPRECIATION',
      };
    } else if (val <= 80) {
      return {
        color: 'var(--primary-gold)',
        glow: 'var(--primary-gold-glow)',
        label: 'HIGH GROWTH potential',
      };
    } else {
      return {
        color: 'var(--emerald)',
        glow: 'var(--emerald-glow)',
        label: 'PRIME ASSET',
      };
    }
  };

  const scheme = getColorScheme(score);
  
  // SVG Ring Math
  const radius = 70;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      position: 'relative'
    }}>
      {/* SVG Radial Dial */}
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 160 160" style={{ transform: 'rotate(-90deg)' }}>
          {/* Background Track Circle */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="transparent"
            stroke="rgba(255, 255, 255, 0.03)"
            strokeWidth={strokeWidth}
          />
          {/* Main Progress Arc */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="transparent"
            stroke={scheme.color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{
              transition: 'stroke-dashoffset 0.5s ease-out, stroke 0.5s ease-out',
              filter: `drop-shadow(0 0 8px ${scheme.glow})`
            }}
          />
        </svg>

        {/* Center Text Panel */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center'
        }}>
          <span style={{
            fontSize: '0.65rem',
            color: 'rgba(255, 255, 255, 0.4)',
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            marginBottom: '2px'
          }}>
            {label}
          </span>
          <span className="number-metric" style={{
            fontSize: '3rem',
            fontWeight: '700',
            color: '#fff',
            lineHeight: '1',
            textShadow: `0 0 15px ${scheme.glow}`
          }}>
            {animatedScore}
          </span>
          <span style={{
            fontSize: '0.75rem',
            color: 'rgba(255, 255, 255, 0.5)',
            letterSpacing: '0.05em'
          }}>
            / 100
          </span>
        </div>
      </div>

      {/* Threshold Status Label */}
      <div style={{
        marginTop: '16px',
        padding: '6px 16px',
        borderRadius: '20px',
        background: `rgba(${scheme.color === 'var(--crimson)' ? '239,68,68' : scheme.color === 'var(--amber)' ? '245,158,11' : scheme.color === 'var(--primary-gold)' ? '240,180,41' : '16,185,129'}, 0.08)`,
        border: `1px solid ${scheme.color}`,
        color: scheme.color,
        fontSize: '0.7rem',
        fontFamily: 'var(--font-heading)',
        fontWeight: '700',
        letterSpacing: '0.15em',
        textTransform: 'uppercase',
        boxShadow: `0 0 10px rgba(${scheme.color === 'var(--crimson)' ? '239,68,68' : scheme.color === 'var(--amber)' ? '245,158,11' : scheme.color === 'var(--primary-gold)' ? '240,180,41' : '16,185,129'}, 0.15)`
      }}>
        {scheme.label}
      </div>
    </div>
  );
}
