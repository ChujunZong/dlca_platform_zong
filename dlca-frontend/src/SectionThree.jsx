import React, { useState } from 'react';
import './SectionThree.css';

const SectionThree = ({ onModelUploadClick }) => {
  const [activeTheme, setActiveTheme] = useState(null);

  return (
    <section className={`section-three theme-${activeTheme || 'default'}`}>
      <div className="s3-dynamic-bg">
        <div className="bg-panel bg-left">
          <div className="dynamic-or"><span>OR</span></div>
        </div>
        <div className="bg-panel bg-right"></div>
      </div>

      <div className="global-bg-layer bg-building-explode">
        <div className="building-container isometric-blueprint">
          <div className="iso-layer l1">
            <div className="platform orange-accent"><div className="hole-cutout"></div><div className="abstract-pool"></div></div>
            <div className="stairs s1"></div>
          </div>
          <div className="iso-layer l2">
            <div className="platform grid-pattern"><div className="hole-cutout main-shaft"></div><div className="abstract-sofa"></div></div>
             <div className="stairs s2"></div>
          </div>
          <div className="iso-layer l3">
            <div className="platform grid-pattern"><div className="abstract-plant"></div></div>
            <div className="stairs s3"></div>
          </div>
          <div className="iso-layer l4"><div className="platform orange-accent sm"></div></div>
          <div className="connector-line c1"></div><div className="connector-line c2"></div><div className="connector-dot d1"></div>
        </div>
      </div>

      <div className="global-bg-layer bg-carbon-blueprint">
        <div className="building-container isometric-blueprint data-container">
          <div className="data-base-grid">
             <div className="time-tick t1"><span>2024</span></div>
             <div className="time-tick t2"><span>2030</span></div>
             <div className="time-tick t3"><span>2050</span></div>
          </div>
          <div className="emission-group group-1">
            <div className="emitter-base high-danger"></div>
            <div className="smoke-particle dark s1"></div><div className="smoke-particle dark s2"></div><div className="smoke-particle dark s3"></div>
            <div className="co2-label danger">450kg CO₂</div>
          </div>
          <div className="emission-group group-2">
            <div className="emitter-base mid-warn"></div>
            <div className="smoke-particle grey s1"></div><div className="smoke-particle grey s2"></div>
          </div>
          <div className="emission-group group-3">
            <div className="emitter-base low-safe"></div>
            <div className="smoke-particle light s1"></div>
          </div>
          <div className="emission-group group-4">
            <div className="emitter-base net-zero"></div>
            <div className="nature-sprout"></div>
            <div className="co2-label success">NET ZERO</div>
          </div>
          <div className="reduction-line"></div>
        </div>
      </div>

      <div className="s3-container">
        
        <div className="s3-header">
          <p className="s3-subtitle">GET STARTED</p>
          <h2 className="s3-art-heading">
            <span className="s3-art-serif">Choose</span><br/>
            <span className="s3-art-sans">Your Path.</span>
          </h2>
        </div>

        <div className="cards-wrapper">
          {/* left：path A */}
          <div 
            className={`minimal-card card-tech ${activeTheme === 'creative' ? 'vanish' : ''}`}
            onMouseEnter={() => setActiveTheme('tech')}
            onMouseLeave={() => setActiveTheme(null)}
            onClick={onModelUploadClick} 
            style={{ cursor: 'pointer' }} 
          >
            <div className="card-content">
              <div className="icon-box">
                <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
              </div>
              <span className="card-label">PROFESSIONAL</span>
              <h3 className="card-title">I Have a Model</h3>
              <p className="card-text">Import existing BIM or CityGML data. <br/>Watch your building deconstruct into data points.</p>
              
              <button className="card-link" style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
                Initialize <span className="arrow">→</span>
              </button>
            </div>
          </div>

          {/* right：path B */}
          <div 
            className={`minimal-card card-creative ${activeTheme === 'tech' ? 'vanish' : ''}`}
            onMouseEnter={() => setActiveTheme('creative')}
            onMouseLeave={() => setActiveTheme(null)}
          >
            <div className="card-content">
              <div className="icon-box">
                <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="M12 19l7-7 3 3-7 7-3-3z"></path><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path><path d="M2 2l7.586 7.586"></path><circle cx="11" cy="11" r="2"></circle></svg>
              </div>
              <span className="card-label">SIMPLIFIED</span>
              <h3 className="card-title">Start from Scratch</h3>
              <p className="card-text">Simulate carbon impact over time.<br/>Optimize form before you build.</p>
              
              <a href="/tool" target="_blank" rel="noopener noreferrer" className="card-link" style={{ textDecoration: 'none' }}>
                Launch Tool <span className="arrow">→</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SectionThree;