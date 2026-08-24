import React from 'react';
import './HowItWorks.css';


const IconStep1 = () => (
  <svg viewBox="0 0 400 240" className="how-svg-illustration" xmlns="http://www.w3.org/2000/svg">
  
    <rect x="10" y="20" width="380" height="200" rx="16" fill="rgba(255, 255, 255, 0.6)" stroke="#FFFFFF" strokeWidth="2" style={{filter: 'drop-shadow(0 15px 25px rgba(234,88,12,0.05))'}} />
    
    <g transform="translate(35, 50)">
      <g className="float-layer-2">
        {/* Path 1: IFC Upload */}
        <rect x="0" y="0" width="140" height="140" rx="12" fill="#FFFBF7" stroke="#FFEDD5" strokeWidth="1.5" strokeDasharray="4 4" />
        <circle cx="70" cy="55" r="24" fill="rgba(234, 88, 12, 0.1)" />
        <path d="M70 43 L70 67 M58 55 L82 55" stroke="#EA580C" strokeWidth="3" strokeLinecap="round" />
        <text x="70" y="100" fill="#1E293B" fontSize="13" fontFamily="Inter" fontWeight="800" textAnchor="middle">Upload .IFC</text>
        <text x="70" y="118" fill="#64748B" fontSize="10" fontFamily="Inter" fontWeight="600" textAnchor="middle">Path 1: 3D Model</text>
      </g>
    </g>

    <g transform="translate(200, 120)">
      <g className="float-layer-1">
        <circle cx="0" cy="0" r="16" fill="#FFFFFF" stroke="#FFEDD5" strokeWidth="1.5" style={{filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.05))'}} />
        <text x="0" y="4" fill="#94A3B8" fontSize="11" fontFamily="Inter" fontWeight="800" textAnchor="middle">OR</text>
      </g>
    </g>

    {/* Path 2: Form Input */}
    <g transform="translate(225, 50)">
      <g className="float-layer-3">
        <rect x="0" y="0" width="140" height="140" rx="12" fill="#FFFFFF" stroke="#FFEDD5" strokeWidth="1.5" />
        <rect x="20" y="30" width="60" height="8" rx="4" fill="#E2E8F0" />
        <rect x="20" y="50" width="100" height="12" rx="4" fill="#F8FAFC" />
        <rect x="20" y="75" width="40" height="8" rx="4" fill="#E2E8F0" />
        <rect x="20" y="95" width="100" height="12" rx="4" fill="#F8FAFC" />
        <circle cx="105" cy="35" r="10" fill="rgba(234, 88, 12, 0.15)" />
        <path d="M102 35 L104 37 L109 32" fill="none" stroke="#EA580C" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        <text x="70" y="125" fill="#64748B" fontSize="10" fontFamily="Inter" fontWeight="600" textAnchor="middle">Path 2: Manual Input</text>
      </g>
    </g>
  </svg>
);

const IconStep2 = () => (
  <svg 
    viewBox="0 0 760 420" 
    className="how-svg-illustration" 
    style={{ maxWidth: '760px', width: '100%' }} 
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <clipPath id="typing-mask">
        <rect x="15" y="14" height="25" width="0" className="ani-mask-rect" />
      </clipPath>
    </defs>
    
    <style>
      {`
        @keyframes building-top {
          0%, 15% { transform: translateY(0); }
          25%, 75% { transform: translateY(-25px); } 
          85%, 100% { transform: translateY(0); }
        }
        @keyframes building-bot {
          0%, 15% { transform: translateY(0); }
          25%, 75% { transform: translateY(25px); }
          85%, 100% { transform: translateY(0); }
        }
        @keyframes card-top-fade {
          0%, 25% { opacity: 0; transform: translateX(-15px); }
          30%, 75% { opacity: 1; transform: translateX(0); }
          80%, 100% { opacity: 0; transform: translateX(-15px); }
        }
        @keyframes card-mid-fade {
          0%, 35% { opacity: 0; transform: translateX(-15px); }
          40%, 75% { opacity: 1; transform: translateX(0); }
          80%, 100% { opacity: 0; transform: translateX(-15px); }
        }
        @keyframes card-bot-fade {
          0%, 45% { opacity: 0; transform: translateX(-15px); }
          50%, 75% { opacity: 1; transform: translateX(0); }
          80%, 100% { opacity: 0; transform: translateX(-15px); }
        }
        @keyframes rect-grow {
          0%, 10% { width: 0px; }
          30%, 80% { width: 65px; }
          85%, 100% { width: 0px; }
        }
        @keyframes cursor-move-1 {
          0%, 10% { transform: translateX(0); opacity: 1; }
          30%, 80% { transform: translateX(65px); opacity: 0; }
          85%, 100% { transform: translateX(0); opacity: 0; }
        }
        @keyframes pointer-move {
          0%, 25% { transform: translate(190px, 170px); opacity: 0; }
          28% { transform: translate(190px, 170px); opacity: 1; }
          35% { transform: translate(145px, 113px); opacity: 1; } 
          38% { transform: translate(145px, 113px) scale(0.85); opacity: 1; } 
          42% { transform: translate(145px, 113px) scale(1); opacity: 1; } 
          46%, 100% { transform: translate(160px, 145px); opacity: 0; } 
        }
        @keyframes click-b4 {
          0%, 35% { fill: #FFFBF7; stroke: #FFEDD5; }
          40%, 80% { fill: rgba(234,88,12,0.1); stroke: #EA580C; }
          85%, 100% { fill: #FFFBF7; stroke: #FFEDD5; }
        }
        @keyframes text-click-b4 {
          0%, 35% { fill: #64748B; font-weight: 600; }
          40%, 80% { fill: #EA580C; font-weight: 800; }
          85%, 100% { fill: #64748B; font-weight: 600; }
        }
        @keyframes baseline-glow {
          0%, 42% { opacity: 0.4; filter: grayscale(1); transform: scale(0.98); }
          45%, 80% { opacity: 1; filter: grayscale(0); transform: scale(1.02); }
          85%, 100% { opacity: 0.4; filter: grayscale(1); transform: scale(0.98); }
        }

        .ani-ifc-top { animation: building-top 6s cubic-bezier(0.25, 1, 0.5, 1) infinite; }
        .ani-ifc-bot { animation: building-bot 6s cubic-bezier(0.25, 1, 0.5, 1) infinite; }
        .ani-card-top { animation: card-top-fade 6s ease-out infinite; }
        .ani-card-mid { animation: card-mid-fade 6s ease-out infinite; }
        .ani-card-bot { animation: card-bot-fade 6s ease-out infinite; }
        .ani-mask-rect { animation: rect-grow 6s steps(15, end) infinite; }
        .ani-cursor-1 { animation: cursor-move-1 6s steps(15, end) infinite; }
        .ani-pointer { animation: pointer-move 6s ease-in-out infinite; transform-origin: top left; }
        .ani-box-b4 { animation: click-b4 6s ease-in-out infinite; }
        .ani-text-b4 { animation: text-click-b4 6s ease-in-out infinite; }
        .ani-baseline { animation: baseline-glow 6s cubic-bezier(0.25, 1, 0.5, 1) infinite; transform-origin: 100px 17px; }
      `}
    </style>

    <rect x="20" y="20" width="720" height="380" rx="32" fill="rgba(255, 255, 255, 0.6)" stroke="#FFFFFF" strokeWidth="2" style={{filter: 'drop-shadow(0 15px 30px rgba(234,88,12,0.06))'}} />
    
    <g transform="translate(65, 60) scale(1.3)">
      <text x="5" y="0" fill="#EA580C" fontSize="10.5" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">PATH 1: IFC AUTO-MAPPING</text>
      
      <g transform="translate(18, 25)">
        <g className="ani-ifc-bot">
          <polygon points="35,115 55,125 35,135 15,125" fill="#FFE4C4" stroke="#EA580C" strokeWidth="1.5"/>
        </g>
        
        <g>
          <polygon points="15,60 35,70 35,135 15,125" fill="#FFF0E0" stroke="#EA580C" strokeWidth="1.5"/>
          <g transform="translate(15, 60) skewY(26.565)">
            {[8, 19, 30, 41, 52].map(y => (
              <g key={y}>
                <rect x="4" y={y} width="4" height="6.5" rx="0.5" fill="#FFFFFF" opacity="0.9"/>
                <rect x="12" y={y} width="4" height="6.5" rx="0.5" fill="#FFFFFF" opacity="0.9"/>
              </g>
            ))}
          </g>
          
          <polygon points="35,70 55,60 55,125 35,135" fill="#FFD8B3" stroke="#EA580C" strokeWidth="1.5"/>
          <g transform="translate(35, 70) skewY(-26.565)">
            {[8, 19, 30, 41, 52].map(y => (
              <g key={y}>
                <rect x="4" y={y} width="4" height="6.5" rx="0.5" fill="#FFFFFF" opacity="0.7"/>
                <rect x="12" y={y} width="4" height="6.5" rx="0.5" fill="#FFFFFF" opacity="0.7"/>
              </g>
            ))}
          </g>
        </g>
        
        <g className="ani-ifc-top">
          <polygon points="35,50 55,60 35,70 15,60" fill="#FFF8F0" stroke="#EA580C" strokeWidth="1.5"/>
        </g>
      </g>

      <g className="ani-card-top" transform="translate(0, 10)">
        <rect x="100" y="48" width="115" height="24" rx="6" fill="#FFFFFF" stroke="#FFEDD5" strokeWidth="1" />
        <text x="108" y="63" fill="#0F172A" fontSize="9" fontFamily="Inter" fontWeight="800">Slab_200mm</text>
      </g>
      <g className="ani-card-mid" transform="translate(0, 10)">
        <rect x="100" y="88" width="115" height="24" rx="6" fill="#FFFFFF" stroke="#FFEDD5" strokeWidth="1" />
        <text x="108" y="103" fill="#0F172A" fontSize="9" fontFamily="Inter" fontWeight="800">Wall_Ext_Brick</text>
      </g>
      <g className="ani-card-bot" transform="translate(0, 10)">
        <rect x="100" y="128" width="115" height="24" rx="6" fill="#FFFFFF" stroke="#FFEDD5" strokeWidth="1" />
        <text x="108" y="143" fill="#0F172A" fontSize="9" fontFamily="Inter" fontWeight="800">Foundation_Piles</text>
      </g>
    </g>

    <g transform="translate(440, 60) scale(1.3)">
      <text x="5" y="0" fill="#EA580C" fontSize="10.5" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">PATH 2: FORM INPUT</text>

      <g transform="translate(0, 25)">
        <text x="5" y="0" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="700">Total Floor Area (m²)</text>
        <rect x="5" y="8" width="190" height="32" rx="6" fill="#FFFBF7" stroke="#FFEDD5" strokeWidth="1" />
        <text x="15" y="30" fill="#1E293B" fontSize="13" fontFamily="Inter" fontWeight="800" clipPath="url(#typing-mask)">3,493.6</text>
        <line x1="15" y1="14" x2="15" y2="30" stroke="#EA580C" strokeWidth="1.5" className="ani-cursor-1" />
      </g>

      <g transform="translate(0, 90)">
        <text x="5" y="0" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="700">Dynamic Factor</text>
        
        <rect x="5" y="8" width="36" height="22" rx="4" fill="#FFFBF7" stroke="#FFEDD5" strokeWidth="1" />
        <text x="23" y="23" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="600" textAnchor="middle">B1</text>
        <rect x="46" y="8" width="36" height="22" rx="4" fill="#FFFBF7" stroke="#FFEDD5" strokeWidth="1" />
        <text x="64" y="23" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="600" textAnchor="middle">B2</text>
        <rect x="87" y="8" width="36" height="22" rx="4" fill="#FFFBF7" stroke="#FFEDD5" strokeWidth="1" />
        <text x="105" y="23" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="600" textAnchor="middle">B3</text>
        
        <rect x="128" y="8" width="36" height="22" rx="4" className="ani-box-b4" fill="#FFFBF7" stroke="#FFEDD5" strokeWidth="1" />
        <text x="146" y="23" className="ani-text-b4" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="600" textAnchor="middle">B4</text>
        
        <rect x="169" y="8" width="36" height="22" rx="4" fill="#FFFBF7" stroke="#FFEDD5" strokeWidth="1" />
        <text x="187" y="23" fill="#64748B" fontSize="8" fontFamily="Inter" fontWeight="600" textAnchor="middle">B5</text>
      </g>

      <g className="ani-pointer">
        <path d="M0 0 L0 18 L4.5 13.5 L8 20 L10 19 L6.5 12.5 L12 12.5 Z" fill="#0F172A" stroke="#FFFFFF" strokeWidth="1.5" style={{filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.2))'}} />
      </g>

      <g transform="translate(0, 160)">
        <g className="ani-baseline">
          <rect x="5" y="0" width="190" height="34" rx="8" fill="#10B981" style={{filter: 'drop-shadow(0 6px 15px rgba(16,185,129,0.3))'}} />
          <circle cx="35" cy="17" r="8" fill="rgba(255,255,255,0.2)" />
          <path d="M32 17 L34 19 L38 15" fill="none" stroke="#FFFFFF" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          <text x="110" y="21" fill="#FFFFFF" fontSize="11" fontFamily="Inter" fontWeight="800" textAnchor="middle">Run Calculation</text>
        </g>
      </g>
    </g>
  </svg>
);


const IconStep3 = () => (
  <svg 
    viewBox="0 0 760 420" 
    className="how-svg-illustration" 
    style={{ maxWidth: '760px', width: '100%', height: 'auto' }} 
    xmlns="http://www.w3.org/2000/svg"
  >
    <style>
      {`
        
        @keyframes container-loop {
          0%, 5% { opacity: 0; transform: translateY(15px); }
          10%, 90% { opacity: 1; transform: translateY(0); }
          95%, 100% { opacity: 0; transform: translateY(-15px); }
        }

        
        @keyframes line-grow {
          0%, 8% { stroke-dasharray: 600; stroke-dashoffset: 600; }
          35%, 90% { stroke-dasharray: 600; stroke-dashoffset: 0; }
          95%, 100% { stroke-dasharray: 600; stroke-dashoffset: 600; }
        }

        
        @keyframes cursor-x-sweep {
          0%, 20% { opacity: 0; transform: translateX(60px); }
          25% { opacity: 1; transform: translateX(160px); } 
          35% { opacity: 1; transform: translateX(160px); } 
          55% { opacity: 1; transform: translateX(250px); } 
          75% { opacity: 1; transform: translateX(250px); }
          80%, 100% { opacity: 0; transform: translateX(260px); }
        }

        @keyframes mouse-y-float {
          0%, 11% { transform: translate(-5px, 257px); }
          25%, 45% { transform: translate(-5px, 175px); } 
          55%, 75% { transform: translate(-5px, 135px); } 
          80%, 100% { transform: translate(-5px, 257px); }
        }

        @keyframes tt1-fade {
          0%, 20% { opacity: 0; transform: translateY(10px); }
          28%, 42% { opacity: 1; transform: translateY(0); }
          45%, 100% { opacity: 0; transform: translateY(-10px); }
        }

        @keyframes tt2-fade {
          0%, 55% { opacity: 0; transform: translateY(10px); }
          58%, 72% { opacity: 1; transform: translateY(0); }
          75%, 100% { opacity: 0; transform: translateY(-10px); }
        }

        @keyframes active-pulse {
          0%, 100% { fill: #EFF6FF; stroke: #BFDBFE; }
          50% { fill: #DBEAFE; stroke: #93C5FD; }
        }

        .ani-content { animation: container-loop 12s cubic-bezier(0.25, 1, 0.5, 1) infinite; }
        .ani-line { animation: line-grow 12s cubic-bezier(0.25, 1, 0.5, 1) infinite; }
        .ani-cursor-x { animation: cursor-x-sweep 12s ease-in-out infinite; }
        .ani-mouse-y { animation: mouse-y-float 12s ease-in-out infinite; }
        .ani-tt1 { animation: tt1-fade 12s ease-in-out infinite; }
        .ani-tt2 { animation: tt2-fade 12s ease-in-out infinite; }
        .ani-active-item { animation: active-pulse 3s infinite; }
      `}
    </style>

    <rect x="20" y="20" width="720" height="380" rx="24" fill="rgba(255, 255, 255, 0.6)" stroke="#FFFFFF" strokeWidth="2" style={{filter: 'drop-shadow(0 15px 30px rgba(234,88,12,0.06))'}} />

    <g className="ani-content">
      
      <g transform="translate(40, 40)">
        
        {/* CHART ANNOTATIONS */}
        <rect x="0" y="0" width="220" height="150" rx="12" fill="#FFFFFF" stroke="#F1F5F9" strokeWidth="1" />
        <text x="15" y="25" fill="#475569" fontSize="10" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">CHART ANNOTATIONS</text>
        <g transform="translate(15, 50)">
          <line x1="0" y1="0" x2="10" y2="0" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" />
          <rect x="20" y="-3" width="150" height="4" rx="2" fill="#E2E8F0" />
          <rect x="20" y="5" width="110" height="4" rx="2" fill="#E2E8F0" />
          
          <line x1="0" y1="25" x2="10" y2="25" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round" />
          <rect x="20" y="22" width="160" height="4" rx="2" fill="#E2E8F0" />
          <rect x="20" y="30" width="130" height="4" rx="2" fill="#E2E8F0" />
          
          <line x1="0" y1="50" x2="10" y2="50" stroke="#10B981" strokeWidth="2" strokeLinecap="round" />
          <rect x="20" y="47" width="140" height="4" rx="2" fill="#E2E8F0" />
          
          <line x1="0" y1="75" x2="10" y2="75" stroke="#EC4899" strokeWidth="2" strokeLinecap="round" />
          <rect x="20" y="72" width="120" height="4" rx="2" fill="#E2E8F0" />
        </g>

        {/* GENERATED PDF REPORTS */}
        <g transform="translate(0, 170)">
          <rect x="0" y="0" width="220" height="170" rx="12" fill="#FFFFFF" stroke="#F1F5F9" strokeWidth="1" />
          <text x="15" y="25" fill="#475569" fontSize="10" fontFamily="Inter" fontWeight="800" letterSpacing="0.5">GENERATED PDF REPORTS</text>
          <g transform="translate(15, 45)">
            <rect x="0" y="0" width="190" height="24" rx="6" fill="#F8FAFC" />
            <rect x="10" y="10" width="130" height="4" rx="2" fill="#CBD5E1" />
            
            <rect x="0" y="32" width="190" height="24" rx="6" fill="#F8FAFC" />
            <rect x="10" y="42" width="150" height="4" rx="2" fill="#CBD5E1" />
            
            <rect x="0" y="64" width="190" height="24" rx="6" fill="#F8FAFC" />
            <rect x="10" y="74" width="110" height="4" rx="2" fill="#CBD5E1" />
            
            <rect x="0" y="96" width="190" height="28" rx="6" strokeWidth="1" className="ani-active-item" />
            <text x="10" y="114" fill="#1D4ED8" fontSize="10" fontFamily="Inter" fontWeight="800">  Breakdown: FLOOR</text>
          </g>
        </g>
      </g>

      <g transform="translate(280, 40)">
        <rect x="0" y="0" width="440" height="340" rx="12" fill="#FFFFFF" stroke="#F1F5F9" strokeWidth="1" style={{filter: 'drop-shadow(0 4px 10px rgba(0,0,0,0.02))'}} />
        
        <text x="20" y="55" fill="#64748B" fontSize="8.5" fontFamily="Inter" fontWeight="600">Absolute Global Warming Potential</text>
        <text x="20" y="69" fill="#64748B" fontSize="8.5" fontFamily="Inter" fontWeight="600">(AGWP) [W m⁻² yr]</text>

        <text x="50" y="100" fill="#94A3B8" fontSize="9" fontFamily="Inter" textAnchor="end">4.00e-9</text>
        <line x1="60" y1="97" x2="410" y2="97" stroke="#F1F5F9" strokeWidth="1" strokeDasharray="4 4" />
        
        <text x="50" y="180" fill="#94A3B8" fontSize="9" fontFamily="Inter" textAnchor="end">2.00e-9</text>
        <line x1="60" y1="177" x2="410" y2="177" stroke="#F1F5F9" strokeWidth="1" strokeDasharray="4 4" />
        
        <text x="50" y="260" fill="#94A3B8" fontSize="9" fontFamily="Inter" textAnchor="end">0</text>
        <line x1="60" y1="257" x2="410" y2="257" stroke="#CBD5E1" strokeWidth="1.5" />

        <g transform="translate(0, 275)" fill="#94A3B8" fontSize="9" fontFamily="Inter" textAnchor="middle">
          <text x="60">2026</text>
          <text x="110">2032</text>
          <text x="160">2038</text>
          <text x="210">2044</text>
          <text x="260">2050</text>
          <text x="340">2100</text>
          <text x="390">2122</text>
        </g>

        <g transform="translate(60, 257)">
          <path d="M 0 0 Q 200 -130 350 -160" fill="none" stroke="#F59E0B" strokeWidth="2" className="ani-line" />
          <path d="M 0 0 L 350 -130" fill="none" stroke="#3B82F6" strokeWidth="2" className="ani-line" />
          <path d="M 0 0 L 350 -40" fill="none" stroke="#EC4899" strokeWidth="1.5" className="ani-line" />
          <path d="M 0 0 L 350 -10" fill="none" stroke="#10B981" strokeWidth="1.5" className="ani-line" />
        </g>


        <g transform="translate(60, 305)">
          <rect x="0" y="0" width="350" height="8" rx="4" fill="#F1F5F9" />
          <rect x="0" y="0" width="120" height="8" rx="4" fill="#CBD5E1" />
        </g>

        <g className="ani-cursor-x">
          
          <line x1="0" y1="50" x2="0" y2="257" stroke="#94A3B8" strokeWidth="1.5" strokeDasharray="4 4" />
          
          <g className="ani-mouse-y">
            <path d="M0 0 L0 18 L4.5 13.5 L8 20 L10 19 L6.5 12.5 L12 12.5 Z" fill="#0F172A" stroke="#FFFFFF" strokeWidth="1.5" style={{filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))'}} />
          </g>

          <g className="ani-tt1" transform="translate(15, 45)">
            <rect x="0" y="0" width="165" height="100" rx="8" fill="#1E293B" style={{filter: 'drop-shadow(0 15px 25px rgba(0,0,0,0.3))'}} />
            <text x="15" y="20" fill="#F8FAFC" fontSize="11" fontFamily="Inter" fontWeight="800">Year: 2038</text>
            <line x1="15" y1="28" x2="150" y2="28" stroke="#334155" strokeWidth="1" />
            <g transform="translate(15, 42)">
              <circle cx="0" cy="-3" r="3" fill="#F59E0B" />
              <rect x="8" y="-6" width="60" height="4" rx="2" fill="#475569" />
              <text x="135" y="0" fill="#F59E0B" fontSize="9" fontFamily="Inter" fontWeight="800" textAnchor="end">1.42e-9</text>
            </g>
            <g transform="translate(15, 57)">
              <circle cx="0" cy="-3" r="3" fill="#3B82F6" />
              <rect x="8" y="-6" width="70" height="4" rx="2" fill="#475569" />
              <text x="135" y="0" fill="#3B82F6" fontSize="9" fontFamily="Inter" fontWeight="800" textAnchor="end">1.15e-9</text>
            </g>
            <g transform="translate(15, 72)">
              <circle cx="0" cy="-3" r="3" fill="#EC4899" />
              <rect x="8" y="-6" width="40" height="4" rx="2" fill="#475569" />
              <text x="135" y="0" fill="#EC4899" fontSize="9" fontFamily="Inter" fontWeight="800" textAnchor="end">3.80e-10</text>
            </g>
            <g transform="translate(15, 87)">
              <circle cx="0" cy="-3" r="3" fill="#10B981" />
              <rect x="8" y="-6" width="50" height="4" rx="2" fill="#475569" />
              <text x="135" y="0" fill="#10B981" fontSize="9" fontFamily="Inter" fontWeight="800" textAnchor="end">5.20e-11</text>
            </g>
          </g>

          <g className="ani-tt2" transform="translate(15, 45)">
            <rect x="0" y="0" width="165" height="100" rx="8" fill="#1E293B" style={{filter: 'drop-shadow(0 15px 25px rgba(0,0,0,0.3))'}} />
            <text x="15" y="20" fill="#F8FAFC" fontSize="11" fontFamily="Inter" fontWeight="800">Year: 2049</text>
            <line x1="15" y1="28" x2="150" y2="28" stroke="#334155" strokeWidth="1" />
            <g transform="translate(15, 42)">
              <circle cx="0" cy="-3" r="3" fill="#F59E0B" />
              <rect x="8" y="-6" width="80" height="4" rx="2" fill="#475569" />
              <text x="135" y="0" fill="#F59E0B" fontSize="9" fontFamily="Inter" fontWeight="800" textAnchor="end">2.59e-9</text>
            </g>
            <g transform="translate(15, 57)">
              <circle cx="0" cy="-3" r="3" fill="#3B82F6" />
              <rect x="8" y="-6" width="90" height="4" rx="2" fill="#475569" />
              <text x="135" y="0" fill="#3B82F6" fontSize="9" fontFamily="Inter" fontWeight="800" textAnchor="end">2.20e-9</text>
            </g>
            <g transform="translate(15, 72)">
              <circle cx="0" cy="-3" r="3" fill="#EC4899" />
              <rect x="8" y="-6" width="60" height="4" rx="2" fill="#475569" />
              <text x="135" y="0" fill="#EC4899" fontSize="9" fontFamily="Inter" fontWeight="800" textAnchor="end">7.00e-10</text>
            </g>
            <g transform="translate(15, 87)">
              <circle cx="0" cy="-3" r="3" fill="#10B981" />
              <rect x="8" y="-6" width="70" height="4" rx="2" fill="#475569" />
              <text x="135" y="0" fill="#10B981" fontSize="9" fontFamily="Inter" fontWeight="800" textAnchor="end">9.84e-11</text>
            </g>
          </g>

        </g>
      </g>
    </g>
  </svg>
);

const HowItWorks = () => {
  return (
    <section className="how-parallax-container">
      <div className="how-solid-bg">
        <div className="how-animated-blob how-blob-1"></div>
        <div className="how-animated-blob how-blob-2"></div>
      </div>

      <div className="how-split-layout">
        
        <div className="how-left-track">
          <h2 className="how-sticky-title">
            How It<br/>Works.
          </h2>
          
          <div className="how-sticky-desc">
            <p className="how-highlight-text">
              Whether you have a detailed model or just an early concept, our workflow adapts to you.<br></br><br></br>  In just three simple steps, integrate Dynamic Life Cycle Assessment (DLCIA) into your design.
            </p>
            
          </div>
        </div>

        <div className="how-right-track">
          <div className="text-spacer-entry"></div>

          <div className="how-text-content">
            
            {/* STEP 1 */}
                <div className="how-feature-block">
                  <div className="how-placeholder-container">
                    <IconStep1 />
                  </div>
                  <p className="how-reveal-text how-reveal-heading">STEP 1 . Choose Your Path</p>
                  <p className="how-reveal-text how-reveal-desc">
                    We offer two flexible starting points: <br />
                    <strong>Path 1:</strong> Have a BIM model? Simply upload your .ifc file, and our system will automatically extract your building components. <br />
                    <strong>Path 2:</strong> Still in the concept phase? Just input your building informations via a quick form to generate an instant calculation.
                  </p>
                </div>

           {/* STEP 2 */}
                  <div className="how-feature-block">
                    <div className="how-placeholder-container">
                      <IconStep2 />
                    </div>
                    <p className="how-reveal-text how-reveal-heading">STEP 2 . Auto-Mapping  or  Custom Setup</p>
                    <p className="how-reveal-text how-reveal-desc">
                      Our smart engine takes over based on your input: <br />
                      <strong>Path 1 :</strong> Scan geometric components within IFC models and map them precisely to our Neo4j database. <br />
                      <strong>Path 2 :</strong> Automatically generates the results based on your form entries. 
                    </p>
                  </div>

            {/* STEP 3 */}
                    <div className="how-feature-block">
                      <div className="how-placeholder-container">
                        <IconStep3 />
                      </div>
                      <p className="how-reveal-text how-reveal-heading">STEP 3 . Real-Time Insights</p>
                      <p className="how-reveal-text how-reveal-desc">
                        Click generate and let our engine handle millions of calculations in seconds. <br />
                        The system visualizes a dynamic carbon trajectory and pinpoints high-emission hotspots, making every low-carbon decision data-driven.
                      </p>
                    </div>

          </div>
          <div className="text-spacer-bottom"></div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;