import React from 'react';
import './WhyChooseUs.css';


const IconDynamicPrecision = () => (
  <svg viewBox="0 0 400 240" className="why-svg-illustration" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <filter id="glow-rose" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
      <filter id="glow-slate" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
      <filter id="glow-sage" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
    </defs>
    
    
    <rect x="10" y="10" width="380" height="220" rx="16" fill="rgba(255, 255, 255, 0.45)" stroke="rgba(255, 255, 255, 0.8)" strokeWidth="2" />

    <g className="float-layer-1">
      
      <line x1="60" y1="30" x2="60" y2="190" stroke="#94A3B8" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="60" y1="190" x2="360" y2="190" stroke="#94A3B8" strokeWidth="1.5" strokeLinecap="round"/>

      <line x1="60" y1="80" x2="350" y2="80" stroke="#CBD5E1" strokeWidth="1" strokeDasharray="4 4" />
      <line x1="60" y1="135" x2="350" y2="135" stroke="#CBD5E1" strokeWidth="1" strokeDasharray="4 4" />

      
      <text x="25" y="115" transform="rotate(-90 25,115)" fill="#475569" fontSize="11" fontFamily="Inter" fontWeight="700" letterSpacing="1">AGWP [W/m²]</text>
      <text x="35" y="84" fill="#64748B" fontSize="10" fontFamily="Inter" fontWeight="600">1.0</text>
      <text x="35" y="139" fill="#64748B" fontSize="10" fontFamily="Inter" fontWeight="600">0.5</text>
      <text x="35" y="194" fill="#64748B" fontSize="10" fontFamily="Inter" fontWeight="600">0.0</text>

      <text x="50" y="210" fill="#64748B" fontSize="11" fontFamily="Inter" fontWeight="700">2025</text>
      <text x="125" y="210" fill="#64748B" fontSize="11" fontFamily="Inter" fontWeight="700">2055</text>
      <text x="215" y="210" fill="#64748B" fontSize="11" fontFamily="Inter" fontWeight="700">2085</text>
      <text x="305" y="210" fill="#64748B" fontSize="11" fontFamily="Inter" fontWeight="700">2115</text>
    </g>

    
    <g className="float-layer-2">
      
      
      <path 
        d="M 60 190 L 140 130 L 230 70 L 320 30" 
        fill="none" 
        stroke="#ee9280ff" 
        strokeWidth="3.5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        filter="url(#glow-rose)"
        className="svg-draw-path" 
        style={{ animationDelay: '0s' }}
      />
      <circle cx="320" cy="30" r="4" fill="#FFFFFF" stroke="#D98A7B" strokeWidth="2" filter="url(#glow-rose)" className="svg-node-dot" style={{ animationDelay: '0s' }}/>

      
      <path 
        d="M 60 190 L 140 150 L 230 105 L 320 75" 
        fill="none" 
        stroke="#7ca9e2ff" 
        strokeWidth="3.5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        filter="url(#glow-slate)"
        className="svg-draw-path" 
        style={{ animationDelay: '0.4s' }} /* 延时 0.4s 开始生长 */
      />
      <circle cx="320" cy="75" r="4" fill="#FFFFFF" stroke="#87A2A9" strokeWidth="2" filter="url(#glow-slate)" className="svg-node-dot" style={{ animationDelay: '0.4s' }}/>

      
      <path 
        d="M 60 190 L 140 170 L 230 145 L 320 125" 
        fill="none" 
        stroke="#62c14bff" 
        strokeWidth="3.5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        filter="url(#glow-sage)"
        className="svg-draw-path" 
        style={{ animationDelay: '0.8s' }} 
      />
      <circle cx="320" cy="125" r="4" fill="#FFFFFF" stroke="#9BB096" strokeWidth="2" filter="url(#glow-sage)" className="svg-node-dot" style={{ animationDelay: '0.8s' }}/>
    </g>
  </svg>
);


const IconContextualExpertise = () => (
  <svg viewBox="0 0 400 240" className="why-svg-illustration" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <filter id="card-shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="15" stdDeviation="20" floodColor="#000000" floodOpacity="0.06"/>
      </filter>
      
      <filter id="icon-glow" x="-50%" y="-50%" width="200%" height="200%">
        <feDropShadow dx="0" dy="8" stdDeviation="12" floodColor="#9333EA" floodOpacity="0.35"/>
      </filter>
      
      <linearGradient id="purple-grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#C084FC" />
        <stop offset="100%" stopColor="#7C3AED" />
      </linearGradient>
    </defs>

   
    <rect x="10" y="10" width="380" height="220" rx="16" fill="rgba(255, 255, 255, 0.45)" stroke="rgba(255, 255, 255, 0.8)" strokeWidth="2" />

    <g className="float-layer-3">
      <rect x="25" y="40" width="145" height="140" rx="8" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1.5" />
      
      <rect x="195" y="60" width="170" height="135" rx="16" fill="rgba(255, 255, 255, 0.2)" stroke="rgba(255, 255, 255, 0.3)" strokeWidth="1" />
    </g>

    
    <g className="float-layer-2">
      <text x="35" y="60" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">LCA METRIC</text>
      <text x="125" y="60" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">VALUE</text>
      <line x1="25" y1="68" x2="170" y2="68" stroke="#E2E8F0" strokeWidth="1.5" />
      
      <text x="35" y="85" fill="#475569" fontSize="9" fontFamily="Inter" fontWeight="600">Ref. Service Life</text>
      <text x="125" y="85" fill="#0F172A" fontSize="9" fontFamily="Inter" fontWeight="700">50 yrs</text>
      <line x1="25" y1="96" x2="170" y2="96" stroke="#E2E8F0" strokeWidth="1" />
      
      <line x1="25" y1="134" x2="170" y2="134" stroke="#E2E8F0" strokeWidth="1" />
      <text x="35" y="152" fill="#475569" fontSize="9" fontFamily="Inter" fontWeight="600">Static GWP100</text>
      <text x="125" y="152" fill="#0F172A" fontSize="9" fontFamily="Inter" fontWeight="700">Fixed</text>

      <rect x="185" y="50" width="170" height="135" rx="16" fill="rgba(255, 255, 255, 0.5)" stroke="rgba(255, 255, 255, 0.6)" strokeWidth="1" />
    </g>

    <g className="float-layer-1">
      <rect x="30" y="103" width="135" height="24" rx="4" fill="rgba(147, 51, 234, 0.1)" stroke="#A855F7" strokeWidth="1" />
      <text x="35" y="119" fill="#7E22CE" fontSize="9" fontFamily="Inter" fontWeight="800">Dynamic Factor</text>
      <text x="125" y="119" fill="#7E22CE" fontSize="9" fontFamily="Inter" fontWeight="800">f(t, i)</text>

      <path d="M 165 115 L 180 115" fill="none" stroke="#A855F7" strokeWidth="1.5" strokeDasharray="3 3" />
      <circle cx="180" cy="115" r="2.5" fill="#A855F7" />

      <rect x="175" y="40" width="170" height="135" rx="16" fill="#FFFFFF" stroke="rgba(255, 255, 255, 0.9)" strokeWidth="1" />
      
      <rect x="225" y="52" width="70" height="16" rx="8" fill="#F1F5F9" />
      <text x="260" y="62" fill="#64748B" fontSize="7" fontFamily="Inter" fontWeight="800" letterSpacing="0.5" textAnchor="middle">OPTION GUIDE</text>

      <circle cx="260" cy="85" r="14" fill="url(#purple-grad)" filter="url(#icon-glow)" />
      <circle cx="260" cy="85" r="6" fill="none" stroke="#FFFFFF" strokeWidth="1.5" />
      <path d="M 260 81 L 260 85 L 263 85" fill="none" stroke="#FFFFFF" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />

      <text x="260" y="115" fill="#0F172A" fontSize="13" fontFamily="Inter" fontWeight="800" textAnchor="middle">Dynamic Factor</text>
      <text x="260" y="132" fill="#475569" fontSize="8" fontFamily="Inter" fontWeight="500" textAnchor="middle">Time-dependent metric reflecting exact</text>
      <text x="260" y="144" fill="#475569" fontSize="8" fontFamily="Inter" fontWeight="500" textAnchor="middle">emission timing &amp; continuous GHG decay.</text>
    </g>

          <g transform="translate(155, 125)"> 
        
        <g className="float-layer-cursor">
          <path 
            d="M0 0 L0 22 L5.5 17.5 L10 26.5 L13 25 L9 16.5 L15.5 16.5 Z" 
            fill="#0F172A" 
            stroke="#FFFFFF" 
            strokeWidth="1.5" 
          />
        </g>
      </g>
  </svg>
);

const IconSeamlessBIM = () => (
  <svg viewBox="0 0 480 280" className="why-svg-illustration" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <filter id="panel-shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="15" stdDeviation="25" floodColor="#000000" floodOpacity="0.08"/>
      </filter>
      <linearGradient id="progress-grad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stopColor="#F59E0B" />
        <stop offset="100%" stopColor="#10B981" />
      </linearGradient>
    </defs>


    <g className="float-layer-3">
      <rect x="15" y="15" width="450" height="270" rx="20" fill="rgba(255, 255, 255, 0.85)" stroke="#FFFFFF" strokeWidth="2" />
      <text x="40" y="50" fill="#0F172A" fontSize="18" fontFamily="Inter" fontWeight="800" letterSpacing="-0.5">Model Insights</text>
      <text x="40" y="68" fill="#64748B" fontSize="10.5" fontFamily="Inter" fontWeight="500">Analysis complete. Ready for Carbon Evaluation.</text>
    </g>


    <g className="float-layer-2">
      {/* Top Left */}
      <rect x="40" y="90" width="230" height="83" rx="12" fill="#F0FDF4" stroke="#D1FAE5" strokeWidth="1.5" />
      <text x="55" y="108" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">TOTAL FLOOR AREA</text>
      
      {/* Top Right */}
      <rect x="285" y="90" width="155" height="83" rx="12" fill="#F0FDF4" stroke="#D1FAE5" strokeWidth="1.5" />
      <text x="300" y="108" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">SUCCESS RATE</text>
      
      {/* Bottom Left */}
      <rect x="40" y="185" width="120" height="85" rx="12" fill="#F0FDF4" stroke="#D1FAE5" strokeWidth="1.5" />
      <text x="55" y="198" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">SOURCE FILE</text>
      <text x="55" y="242" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">AUTO-MAPPED</text>
      
      {/* Bottom Right  */}
      <rect x="175" y="185" width="265" height="85" rx="12" fill="#F0FDF4" stroke="#D1FAE5" strokeWidth="1.5" />
      <text x="190" y="198" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">ELEMENTS BREAKDOWN</text>
      
      <path d="M 190 238 L 270 238 M 300 238 L 415 238" stroke="#CBD5E1" strokeWidth="1" strokeDasharray="2 2" />
      <path d="M 190 252 L 270 252 M 300 252 L 415 252" stroke="#CBD5E1" strokeWidth="1" strokeDasharray="2 2" />
    </g>

    <g className="float-layer-1">
      {/* Top Left Data */}
      <text x="55" y="138" fill="#0F172A" fontSize="26" fontFamily="Inter" fontWeight="800" letterSpacing="-1">3,493.6</text>
      <text x="160" y="138" fill="#64748B" fontSize="11" fontFamily="Inter" fontWeight="700">m²</text>
      <text x="55" y="152" fill="#10B981" fontSize="8" fontFamily="Inter" fontWeight="800">↑ 100% Geometry extracted</text>
      <rect x="55" y="160" width="200" height="4" rx="2" fill="#E2E8F0" />
      <rect x="55" y="160" width="160" height="4" rx="2" fill="url(#progress-grad)" />

      {/* Top Right Data */}
      <circle cx="362" cy="140" r="22" fill="none" stroke="#E2E8F0" strokeWidth="4.5" />
      <circle cx="362" cy="140" r="22" fill="none" stroke="#10B981" strokeWidth="4.5" strokeDasharray="138" strokeDashoffset="0" />
      <text x="362" y="145" fill="#0F172A" fontSize="16" fontFamily="Inter" fontWeight="800" textAnchor="middle">100<tspan fontSize="6">%</tspan></text>

      {/* Bottom Left Data */}
      <rect x="55" y="206" width="85" height="7" rx="3.5" fill="#0F172A" opacity="0.8" />
      <rect x="55" y="218" width="55" height="7" rx="3.5" fill="#0F172A" opacity="0.8" />
      <text x="55" y="258" fill="#0F172A" fontSize="16" fontFamily="Inter" fontWeight="800">7<tspan fontSize="9" fill="#64748B" fontWeight="600" dx="3">materials</tspan></text>

      {/* Bottom Right Data */}
      <text x="190" y="220" fill="#0F172A" fontSize="22" fontFamily="Inter" fontWeight="800">301<tspan fontSize="9" fill="#64748B" fontWeight="600" dx="4">total</tspan></text>
      
      <text x="190" y="238" fill="#475569" fontSize="8.5" fontFamily="Inter" fontWeight="700">Column</text>
      <text x="270" y="238" fill="#0F172A" fontSize="8.5" fontFamily="Inter" fontWeight="800" textAnchor="end">118</text>
      <text x="190" y="252" fill="#475569" fontSize="8.5" fontFamily="Inter" fontWeight="700">Wall</text>
      <text x="270" y="252" fill="#0F172A" fontSize="8.5" fontFamily="Inter" fontWeight="800" textAnchor="end">62</text>
      
      {/* BuildingElementPart  */}
      <text x="300" y="238" fill="#475569" fontSize="8.5" fontFamily="Inter" fontWeight="700">BuildingElementPart</text>
      <text x="415" y="238" fill="#0F172A" fontSize="8.5" fontFamily="Inter" fontWeight="800" textAnchor="end">109</text>
      <text x="300" y="252" fill="#475569" fontSize="8.5" fontFamily="Inter" fontWeight="700">Slab</text>
      <text x="415" y="252" fill="#0F172A" fontSize="8.5" fontFamily="Inter" fontWeight="800" textAnchor="end">8</text>
    </g>

      <g transform="translate(275, 225)"> 
     
        <g className="float-layer-cursor">
          <path 
            d="M0 0 L0 22 L5.5 17.5 L10 26.5 L13 25 L9 16.5 L15.5 16.5 Z" 
            fill="#0F172A" 
            stroke="#FFFFFF" 
            strokeWidth="1.5" 
          />
        </g>
      </g>
  </svg>
);


const WhyChooseUs = () => {
  return (
    <section className="why-parallax-container">
      <div className="why-solid-bg">
        <div className="animated-blob blob-1"></div>
        <div className="animated-blob blob-2"></div>
        <div className="animated-blob blob-3"></div>
      </div>

      <div className="why-split-layout">
        <div className="why-left-track">
          <h2 className="why-sticky-title">Why<br/>Choose Us.</h2>
          <div className="why-sticky-desc">
              <p className="why-highlight-text">
                Our platform distills advanced academic research into a seamless workflow, turning intricate data into actionable insights.<br></br><br></br> By automating deep-level calculations, we empower you to focus on design while maintaining total confidence in your carbon impact data.
              </p>
          </div>
        </div>

        <div className="why-right-track">
          <div className="text-spacer-entry"></div>

          <div className="why-text-content">
            <div className="why-feature-block">
              <div className="why-placeholder-container">
                <IconDynamicPrecision />
              </div>
              <p className="why-reveal-text why-reveal-heading">Dynamic Precision.</p>
              <p className="why-reveal-text why-reveal-desc">
                Powered by IPCC-aligned dynamic algorithms to precisely track real-time carbon decay across the entire lifecycle.
              </p>
            </div>

            <div className="why-feature-block">
              <div className="why-placeholder-container">
                <IconContextualExpertise />
              </div>
              <p className="why-reveal-text why-reveal-heading">Contextual Expertise.</p>
              <p className="why-reveal-text why-reveal-desc">
                Interactive tooltips seamlessly integrate into your workflow, making complex LCA terminology instantly accessible.
              </p>
            </div>

            <div className="why-feature-block">
              <div className="why-placeholder-container">
                 <IconSeamlessBIM />
              </div>
              <p className="why-reveal-text why-reveal-heading">Seamless BIM to Insights.</p>
              <p className="why-reveal-text why-reveal-desc">
                One-click IFC parsing automatically transforms complex carbon footprints into visual, actionable insights.
              </p>
            </div>
          </div>
          <div className="text-spacer-bottom"></div>
        </div>
      </div>
    </section>
  );
};

export default WhyChooseUs;