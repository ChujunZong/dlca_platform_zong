import React, { useState,useEffect } from 'react';
import { 
  Check, Map, Globe2, Building, Trees, Home, Sparkles, Building2, 
  Clock, BarChart3, Activity, Layers, Bot, Maximize, Settings2
} from 'lucide-react';
import './form.css';
import Dashboard from './Dashboard';

const BuildingForm = () => {
  const [step, setStep] = useState(1); 
  const [hoveredField, setHoveredField] = useState('welcome1');
  const [calcResult, setCalcResult] = useState(null);

  const INITIAL_COMPONENTS = [
    { type: 'BP', label: 'Bottom Plate', area: 100 },
    { type: 'FL', label: 'Floor', area: 100 },
    { type: 'EW', label: 'Exterior Wall', area: 200 },
    { type: 'IW', label: 'Interior Wall', area: 150 },
    { type: 'WIN', label: 'Window', area: 50 },
    { type: 'FRO', label: 'Flat Roof', area: 0 },
    { type: 'PRO', label: 'Pitched Roof', area: 0 },
  ];

  const [formData, setFormData] = useState({
    building_id: 'frontend_building_1',
    building_type: 'Masonry_3',
    buildingage: 'nb',
    geography: ['EUROPE_GROUP'],
    rsp: 100,
    total_floor_area: 1000,
    dynamic_factor: ['B1'], 
    dynamic_scenario: 'Carbon Neutral',
    LCIAindicator: 'GWP',
    LCIAindicator_dynamic: 'AGWP',
    cumulative: 'cumulative',
    phase_C: true,
    phase_B6: true,
    phase_A4: true,
    static_comparison: false,
    energy_usage_power: 0.0,
    energy_usage_heat: 35.13,
    type_power: 'electricity, low voltage',
    type_heat: 'heat production, wood pellet, at furnace 300kW',
    components: INITIAL_COMPONENTS
  });
  
  const [loading, setLoading] = useState(false);
  const [activeComponent, setActiveComponent] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const setDirectValue = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const toggleDynamicFactor = (selectedValue) => {
    setFormData(prev => {
      const current = prev.dynamic_factor;
      const isExclusiveOption = selectedValue === '-' || selectedValue === 'power-2024';
      if (isExclusiveOption) return { ...prev, dynamic_factor: [selectedValue] };
      const hasExclusiveActive = current.includes('-') || current.includes('power-2024');
      if (hasExclusiveActive) return { ...prev, dynamic_factor: [selectedValue] };
      if (current.includes(selectedValue)) {
        const newFactors = current.filter(f => f !== selectedValue);
        return { ...prev, dynamic_factor: newFactors.length ? newFactors : ['-'] };
      } else {
        return { ...prev, dynamic_factor: [...current, selectedValue] };
      }
    });
  };
  
  const handleComponentAreaChange = (index, value) => {
    const newComponents = [...formData.components];
    newComponents[index].area = value === '' ? '' : parseFloat(value);
    setFormData({ ...formData, components: newComponents });
  };

  const nextStep = () => {
    setStep(prev => prev + 1);
    setHoveredField(step === 1 ? 'welcome2' : 'welcome1'); 
  };
  
  useEffect(() => {
    const scrollContainer = document.querySelector('.left-pane');
    if (scrollContainer) {
      scrollContainer.scrollTo({
        top: 0,
        behavior: 'smooth' 
      });
    }
  }, [step]);
  const prevStep = () => {
    setStep(prev => prev - 1);
    setHoveredField('welcome1');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const cleanComponents = formData.components.map(c => ({
        type: c.type,
        area: c.area === '' ? 0 : c.area
    }));

    const payload = {
      ...formData,
      components: cleanComponents,
      rsp: parseInt(formData.rsp),
      total_floor_area: parseFloat(formData.total_floor_area),
      energy_usage_power: parseFloat(formData.energy_usage_power),
      energy_usage_heat: parseFloat(formData.energy_usage_heat),
    };

    try {
      const response = await fetch('/api/dlca/run_from_form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (data.ok) {
        try {
          let finalData = JSON.parse(JSON.stringify(data.result));
          let groups = finalData.groups || [];
          let extractedSubLines = {};

          groups.forEach(g => {
            const name = g.name || "";
            let lineData = null;
            if (g.total_line && g.total_line.length > 0) {
              lineData = g.total_line;
            } else if (g.sub_lines && Object.keys(g.sub_lines).length > 0) {
              lineData = Object.values(g.sub_lines)[0];
            }

            if (!lineData) return;

            if (name.includes('_BP')) extractedSubLines['Bottom Plate (BP)'] = lineData;
            else if (name.includes('_EW')) extractedSubLines['Exterior Wall (EW)'] = lineData;
            else if (name.includes('_FL')) extractedSubLines['Floor (FL)'] = lineData;
            else if (name.includes('_FRO')) extractedSubLines['Flat Roof (FRO)'] = lineData;
            else if (name.includes('_PRO')) extractedSubLines['Pitched Roof (PRO)'] = lineData;
            else if (name.includes('_IW')) extractedSubLines['Interior Wall (IW)'] = lineData;
            else if (name.includes('_WIN')) extractedSubLines['Window (WIN)'] = lineData;
          });

          let standardLength = 0;
          for (let key in extractedSubLines) {
            if (Array.isArray(extractedSubLines[key]) && extractedSubLines[key].length > standardLength) {
              standardLength = extractedSubLines[key].length;
            }
          }

          if (standardLength > 0) {
            const allStandardComponents = [
              'Bottom Plate (BP)', 'Exterior Wall (EW)', 'Floor (FL)', 
              'Flat Roof (FRO)', 'Pitched Roof (PRO)', 'Interior Wall (IW)', 'Window (WIN)'
            ];
            
            allStandardComponents.forEach(compName => {
              if (!extractedSubLines[compName]) {
                extractedSubLines[compName] = new Array(standardLength).fill(0);
              }
            });
          }

          if (Object.keys(extractedSubLines).length > 0) {
            const componentSummaryNode = {
              name: "2. Building Components Summary",
              pdf: null,
              sub_lines: extractedSubLines, 
              total_line: [] 
            };
            groups.splice(1, 0, componentSummaryNode);
          }

          setCalcResult(finalData); 

        } catch (err) {
          console.error("An unexpected error occurred while merging data on the front end:", err);
          setCalcResult(data.result);
        }
      } else {
        alert("Error: " + data.error);
      }

      
    } catch (error) {
      console.error("Submission error:", error);
      alert("Network Error");
    } finally {
      setLoading(false);
    }
  };

  const DYNAMIC_FACTOR_OPTIONS = [
    { value: 'B1', label: 'B1 ' }, { value: 'B2', label: 'B2 ' }, { value: 'B3', label: 'B3 ' },
    { value: 'B4', label: 'B4 ' }, { value: 'B5', label: 'B5 ' }, { value: '-', label: 'None' }, 
    { value: 'power-2024', label: 'Power 2024' } 
  ];
  
  const HEAT_OPTIONS = [
    "heat production, wood pellet, at furnace 300kW",
    "heat and power co-generation, natural gas, 1MW electrical, lean burn",
    "heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014, renewable energy products",
    "heat and power co-generation, biogas, gas engine, renewable energy products"
  ];

  const POWER_OPTIONS = [
    "electricity, low voltage", "electricity, medium voltage", "electricity, high voltage"
  ];

  const INDICATOR_OPTIONS = ["GWP", "GWP_fossil", "GWP_bio", "GTP", "GTP_fossil", "GTP_bio"];
  const DYNAMIC_IND_OPTIONS = ["AGWP", "AGWP_fossil", "AGWP_bio", "AGTP", "AGTP_fossil", "AGTP_bio"];
  
  const COMPONENT_COLORS = {
    BP: '#7C6CF6', FL: '#3B82F6', EW: '#2FBF71', IW: '#9BBF2C', 
    WIN: '#F59E0B', FRO: '#F43F5E', PRO: '#C084FC'   
  };

  const totalArea = formData.components.reduce((sum, comp) => sum + (Number(comp.area) || 0), 0);
  const maxArea = Math.max(1, ...formData.components.map(c => Number(c.area) || 0));
  const activeCompIndex = formData.components.findIndex(c => c.type === activeComponent);
  const activeCompData = activeCompIndex >= 0 ? formData.components[activeCompIndex] : null;

  let centerSize = 160; 
  let centerBg = COMPONENT_COLORS[activeComponent];
  let centerColor = '#111827';
  let displayName = 'TOTAL AREA';
  let displayValue = totalArea;
  let displayUnit = 'm²';
  let showAbsoluteArea = false;

  if (activeCompData) {
    const radius = 100 + activeCompIndex * 28; 
    centerSize = (radius - 28) * 2;
    const percentage = totalArea > 0 ? ((Number(activeCompData.area) || 0) / totalArea * 100).toFixed(1) : 0;
    
    centerBg = COMPONENT_COLORS[activeComponent];
    centerColor = '#ffffff'; 
    displayName = activeCompData.label.toUpperCase();
    displayValue = percentage;
    displayUnit = '%';
    showAbsoluteArea = true; 
  }

 
  const glossaryDict = {
    welcome1: { 
      icon: Bot, color: '#8B5CF6', title: "LCA Assistant", 
      desc: "Hover over the fields on the left. The relevant card will flip to the front to explain your options." 
    },
    buildingId: { 
      icon: Building2, color: '#8B5CF6', title: "Project Identity", 
      desc: "A custom label for your PDF reports. This doesn't affect calculations, but helps you manage version history." 
    },
    geography: { 
      icon: Globe2, color: '#8B5CF6', title: "LCI Region Options", 
      desc: (
        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div><strong style={{color: '#111827'}}>• Europe Regions:</strong> Uses high-precision ecoinvent data (CH, RER) for precise European grid impacts.</div>
          <div><strong style={{color: '#111827'}}>• Rest of World:</strong> Falls back to generic global dataset averages (GLO).</div>
        </div>
      )
    },
    buildingType: { 
      icon: Building, color: '#8B5CF6', title: "Typology Options", 
      desc: (
        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div><strong style={{color: '#111827'}}>• Masonry:</strong> Standard heavy brick/concrete structure. High embodied carbon.</div>
          <div><strong style={{color: '#111827'}}>• Timber:</strong> Wood structure. Stores biogenic carbon, lowering initial impact.</div>
          <div><strong style={{color: '#111827'}}>• Adv. Masonry:</strong> Optimized masonry with superior thermal mass properties.</div>
        </div>
      )
    },
    area: { 
      icon: Maximize, color: '#8B5CF6', title: "Floor Area", 
      desc: "The functional unit. All material quantities and Phase B6 energy requirements are scaled by this total area." 
    },
    rsp: { 
      icon: Clock, color: '#8B5CF6', title: "Study Period", 
      desc: "Standard is 50-100 years. A longer lifespan calculation will automatically trigger more material replacement cycles (Phase B4)." 
    },
    age: { 
      icon: Sparkles, color: '#8B5CF6', title: "Building Lifecycle", 
      desc: (
        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div><strong style={{color: '#111827'}}>• New Building:</strong> Full LCA, including the heavy carbon footprint of initial construction materials (A1-A3).</div>
          <div><strong style={{color: '#111827'}}>• Existing Building:</strong> Skips construction. Focuses strictly on renovation and daily operations.</div>
        </div>
      )
    },
    
    welcome2: { 
      icon: Bot, color: '#10B981', title: "Settings Assistant", 
      desc: "Hover over the parameters below. I'll explain what these advanced LCA options mean." 
    },
    indicator: { 
      icon: BarChart3, color: '#10B981', title: "Indicator Settings", 
      desc: (
        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div><strong style={{color: '#111827'}}>• Static (GWP):</strong> Calculates a fixed scalar value based on traditional LCA frameworks.</div>
          <div><strong style={{color: '#111827'}}>• Dynamic (AGWP):</strong> Advanced time-series metrics that track cumulative radiative forcing (AGWP) or absolute temperature change (AGTP).</div>
        </div>
      )
    },
    scenario: { 
      icon: Settings2, color: '#10B981', title: "Future Scenarios", 
      desc: (
        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div><strong style={{color: '#111827'}}>• Carbon Neutral:</strong> Assumes the power grid decarbonizes aggressively by 2050.</div>
          <div><strong style={{color: '#111827'}}>• Business As Usual:</strong> Assumes the current energy grid emission factors persist forever.</div>
        </div>
      )
    },
    factors: { 
          icon: Activity, color: '#10B981', title: "Dynamic Factors", 
          desc: (
            <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div>
                <strong style={{color: '#111827'}}>• B1 :</strong> 
                Models shifts in import ratios for raw materials.
              </div>
              <div>
                <strong style={{color: '#111827'}}>• B2 :</strong> 
                Simulates progress in recycling and waste treatment tech.
              </div>
              <div>
                <strong style={{color: '#111827'}}>• B3–B5 :</strong> 
                Tracks decarbonization across High, Mid, and Low voltage levels.
              </div>
              <div>
                <strong style={{color: '#111827'}}>• Power 2024:</strong> 
                Freezes the energy structure at the current baseline year.
              </div>
            </div>
          )
        },
    calcMode: { 
      icon: Layers, color: '#10B981', title: "Calculation Mode", 
      desc: (
        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div><strong style={{color: '#111827'}}>• Cumulative:</strong> Stacks carbon year by year to show the total debt accumulated.</div>
          <div><strong style={{color: '#111827'}}>• Non-Cumulative:</strong> Shows the isolated carbon impact generated in each specific year.</div>
        </div>
      )
    },
    phases: { 
      icon: Layers, color: '#10B981', title: "LCA Boundaries", 
      desc: (
        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div><strong style={{color: '#111827'}}>• Phase A4:</strong> Transporting materials to site.</div>
          <div><strong style={{color: '#111827'}}>• Phase B6:</strong> Operational energy (Heating/Power).</div>
          <div><strong style={{color: '#111827'}}>• Phase C:</strong> End-of-life demolition & recycling.</div>
        </div>
      )
    }
  };

  const step1Keys = ['welcome1', 'buildingId', 'geography', 'buildingType', 'area', 'rsp', 'age'];
  const step2Keys = ['welcome2', 'indicator', 'scenario', 'factors', 'calcMode', 'phases'];

  const chaoticTransforms = [
    { rotate: 0, x: 0 },         
    { rotate: -6, x: -25 },      
    { rotate: 4, x: 20 },        
    { rotate: -3, x: 10 },       
    { rotate: 5, x: -15 },       
    { rotate: -2, x: 5 },        
    { rotate: 2, x: -5 }
  ];

  const renderStackedCards = () => {
    const currentKeys = step === 1 ? step1Keys : step2Keys;
    const validHovered = currentKeys.includes(hoveredField) ? hoveredField : currentKeys[0];
    const activeIdx = currentKeys.indexOf(validHovered);

    const orderedKeys = [
      ...currentKeys.slice(activeIdx),
      ...currentKeys.slice(0, activeIdx)
    ];

    return (
      <div className="card-stack-wrapper fade-in">
         {orderedKeys.map((key, index) => {
           const item = glossaryDict[key];
           const Icon = item.icon;
           const isFront = index === 0;
           
           const chaotic = chaoticTransforms[index] || { rotate: 0, x: 0 };
           const translateY = index * 26; 
           const scale = 1 - index * 0.05;      
           const opacity = index < 5 ? 1 - index * 0.15 : 0; 
           const zIndex = 20 - index;
           const shadowColor = step === 1 ? 'rgba(139, 92, 246, 0.2)' : 'rgba(16, 185, 129, 0.2)';

           return (
             <div 
               key={key} 
               className={`stack-card ${isFront ? 'is-front' : ''}`}
               style={{
                 transform: `translateX(${chaotic.x}px) translateY(${translateY}px) scale(${scale}) rotate(${chaotic.rotate}deg)`,
                 opacity: opacity,
                 zIndex: zIndex,
                 pointerEvents: isFront ? 'auto' : 'none',
                 boxShadow: isFront ? `0 35px 60px -15px ${shadowColor}` : '0 10px 30px rgba(0,0,0,0.05)'
               }}
             >
               <div className="helper-badge">{isFront ? 'Option Guide' : 'In Deck'}</div>
               <div className="stack-icon-ring" style={{ color: item.color, backgroundColor: `${item.color}15` }}>
                 <Icon size={40} strokeWidth={1.5} />
               </div>
               <h3>{item.title}</h3>
               <div style={{ fontSize: '0.95rem', color: '#4B5563', lineHeight: '1.6' }}>
                  {item.desc}
               </div>
             </div>
           );
         })}
      </div>
    );
  };

  return (
    <div id="dlca-form-wrapper">
      <div className="split-container">
        
        {/* === left side === */}
        <div className="left-pane">
          <div className="glow-blob-purple"></div>
          <div className="glow-blob-green"></div>
          
          <div className="step-indicator">STEP {step} / 3</div>

          <form className="form-content-container" onSubmit={(e) => e.preventDefault()}>
            
            {/* --- STEP 1 --- */}
            {step === 1 && (
              <div className="form-step-content fade-in">
                <div className="form-header-text">
                  <h2>Building Basics</h2>
                  <p>Start by defining the core parameters of your project.</p>
                </div>

                <div className="form-group" onMouseEnter={() => setHoveredField('buildingId')}>
                  <label>Building ID</label>
                  <input type="text" name="building_id" className="form-input" value={formData.building_id} onChange={handleChange} />
                </div>

                <div className="form-group" onMouseEnter={() => setHoveredField('geography')}>
                  <label>Geography</label>
                  <div className="radio-grid">
                    <div className={`radio-card ${formData.geography[0] === 'EUROPE_GROUP' ? 'active' : ''}`} onClick={() => setFormData(prev => ({...prev, geography: ['EUROPE_GROUP']}))}>
                      <div className="radio-check"><Check size={12} color="white" strokeWidth={3}/></div>
                      <Map size={24} className="radio-icon" />
                      <div>
                        <div className="radio-title" style={{ fontSize: '0.85rem' }}>Target Europe Regions</div>
                        <div className="radio-desc">(CH, RER, EU27, etc.)</div>
                      </div>
                    </div>
                    <div className={`radio-card ${formData.geography[0] === 'ROW' ? 'active' : ''}`} onClick={() => setFormData(prev => ({...prev, geography: ['ROW']}))}>
                      <div className="radio-check"><Check size={12} color="white" strokeWidth={3}/></div>
                      <Globe2 size={24} className="radio-icon" />
                      <div>
                        <div className="radio-title" style={{ fontSize: '0.85rem' }}>Rest of the World</div>
                        <div className="radio-desc">(RoW / GLO)</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="form-group" onMouseEnter={() => setHoveredField('buildingType')}>
                  <label>Building Type</label>
                  <div className="radio-grid">
                    {[
                      { id: 'Masonry_1', icon: Building, title: 'Masonry 1', desc: 'Flat roof · wood-alu windows' },
                      { id: 'Masonry_2', icon: Building, title: 'Masonry 2', desc: 'Pitched roof (PRO)' },
                      { id: 'Masonry_3', icon: Building, title: 'Masonry 3', desc: 'Flat roof · alu windows' },
                      { id: 'Masonry_improve1', icon: Home, title: 'Masonry Improve 1', desc: 'Improved walls, floors, roof' },
                      { id: 'Masonry_improve2', icon: Home, title: 'Masonry Improve 2', desc: 'Improved floors and roof' },
                      { id: 'Masonry_improve3', icon: Home, title: 'Masonry Improve 3', desc: 'Improved variant 3' },
                      { id: 'Masonry_improve combined', icon: Home, title: 'Masonry Improve Combined', desc: 'All improvements combined' },
                      { id: 'Timber_1', icon: Trees, title: 'Timber 1', desc: 'Flat roof · wood-alu windows' },
                      { id: 'Timber_2', icon: Trees, title: 'Timber 2', desc: 'Pitched roof (PRO)' },
                      { id: 'Timber_3', icon: Trees, title: 'Timber 3', desc: 'Flat roof · wood windows' },
                    ].map(bt => (
                      <div key={bt.id} className={`radio-card ${formData.building_type === bt.id ? 'active' : ''}`} onClick={() => setDirectValue('building_type', bt.id)}>
                        <div className="radio-check"><Check size={12} color="white" strokeWidth={3}/></div>
                        <bt.icon size={24} className="radio-icon" />
                        <div>
                          <div className="radio-title" style={{ fontSize: '0.85rem' }}>{bt.title}</div>
                          <div className="radio-desc">{bt.desc}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="form-group" onMouseEnter={() => setHoveredField('area')}>
                  <label>Total Floor Area (m²)</label>
                  <input type="number" name="total_floor_area" className="form-input" value={formData.total_floor_area} onChange={handleChange} />
                </div>
                
                <div className="form-group" onMouseEnter={() => setHoveredField('rsp')}>
                  <div className="range-header">
                    <label style={{marginBottom:0}}>Study Period (Years)</label>
                    <span className="range-value">{formData.rsp}</span>
                  </div>
                  <div className="range-slider-container">
                    <input type="range" min="20" max="200" step="10" name="rsp" value={formData.rsp} onChange={handleChange} />
                  </div>
                </div>

                <div className="form-group" onMouseEnter={() => setHoveredField('age')}>
                  <label>Building Age</label>
                  <div className="radio-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                    <div className={`radio-card ${formData.buildingage === 'nb' ? 'active' : ''}`} onClick={() => setDirectValue('buildingage', 'nb')}>
                      <div className="radio-check"><Check size={12} color="white" strokeWidth={3}/></div>
                      <Sparkles size={24} className="radio-icon" />
                      <div>
                        <div className="radio-title">New Building</div>
                        <div className="radio-desc">Construction & Operation</div>
                      </div>
                    </div>
                    <div className={`radio-card ${formData.buildingage === 'eb' ? 'active' : ''}`} onClick={() => setDirectValue('buildingage', 'eb')}>
                      <div className="radio-check"><Check size={12} color="white" strokeWidth={3}/></div>
                      <Building2 size={24} className="radio-icon" />
                      <div>
                        <div className="radio-title">Existing Building</div>
                        <div className="radio-desc">Renovation & Operation</div>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            )}

            {/* --- STEP 2 --- */}
            {step === 2 && (
              <div className="form-step-content fade-in">
                <div className="form-header-text">
                  <h2>Configuration</h2>
                  <p>Adjust the assessment scenarios and dynamic factors.</p>
                </div>

                <div className="form-group" onMouseEnter={() => setHoveredField('indicator')}>
                  <label>Static Indicator</label>
                  <select name="LCIAindicator" className="form-select" value={formData.LCIAindicator} onChange={handleChange}>
                    {INDICATOR_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                </div>
                
                <div className="form-group" onMouseEnter={() => setHoveredField('indicator')}>
                  <label>Dynamic Indicator</label>
                  <select name="LCIAindicator_dynamic" className="form-select" value={formData.LCIAindicator_dynamic} onChange={handleChange}>
                    {DYNAMIC_IND_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                </div>

                <div className="form-group" onMouseEnter={() => setHoveredField('scenario')}>
                  <label>Dynamic Scenario</label>
                  <div className="segmented-control">
                    <div className={`segment-option ${formData.dynamic_scenario === 'Carbon Neutral' ? 'active' : ''}`} onClick={() => setDirectValue('dynamic_scenario', 'Carbon Neutral')}>Carbon Neutral</div>
                    <div className={`segment-option ${formData.dynamic_scenario === 'Business As Usual' ? 'active' : ''}`} onClick={() => setDirectValue('dynamic_scenario', 'Business As Usual')}>Business As Usual</div>
                  </div>
                </div>
                
                <div className="form-group" onMouseEnter={() => setHoveredField('factors')}>
                  <label>Dynamic Factors</label>
                  <div className="chip-group">
                    {DYNAMIC_FACTOR_OPTIONS.map((opt) => (
                      <div key={opt.value} className={`chip-option ${formData.dynamic_factor.includes(opt.value) ? 'active' : ''}`} onClick={() => toggleDynamicFactor(opt.value)}>{opt.label}</div>
                    ))}
                  </div>
                </div>

                <div className="form-group" onMouseEnter={() => setHoveredField('calcMode')}>
                    <label>Calculation Mode</label>
                    <div className="segmented-control">
                        <div className={`segment-option ${formData.cumulative === 'cumulative' ? 'active' : ''}`} onClick={() => setDirectValue('cumulative', 'cumulative')}>Cumulative</div>
                        <div className={`segment-option ${formData.cumulative === 'non-cumulative' ? 'active' : ''}`} onClick={() => setDirectValue('cumulative', 'non-cumulative')}>Non-Cumulative</div>
                    </div>
                </div>

                <div className="toggle-wrapper" onMouseEnter={() => setHoveredField('phases')}>
                  <label>Include Phase A4 (Transport)</label>
                  <label className="toggle-switch">
                    <input type="checkbox" name="phase_A4" checked={formData.phase_A4} onChange={handleChange} />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="toggle-wrapper" onMouseEnter={() => setHoveredField('phases')}>
                  <label>Include Phase C</label>
                  <label className="toggle-switch">
                    <input type="checkbox" name="phase_C" checked={formData.phase_C} onChange={handleChange} />
                    <span className="slider"></span>
                  </label>
                </div>
                <div className="toggle-wrapper" onMouseEnter={() => setHoveredField('phases')}>
                  <label>Include Phase B6</label>
                   <label className="toggle-switch">
                    <input type="checkbox" name="phase_B6" checked={formData.phase_B6} onChange={handleChange} />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>
            )}

            {/* --- STEP 3 --- */}
            {step === 3 && (
              <div className="form-step-content fade-in">
                <div className="form-header-text">
                  <h2>Details & Energy</h2>
                  <p>Specify energy usage and building components.</p>
                </div>

                <div className="form-section-title">Energy (Phase B6)</div>
                
                <div className="form-group">
                    <label>Heat Source</label>
                    <select name="type_heat" className="form-select" value={formData.type_heat} onChange={handleChange}>
                        {HEAT_OPTIONS.map((opt, i) => <option key={i} value={opt}>{opt}</option>)}
                    </select>
                </div>

                <div className="form-group">
                    <label>Power Source</label>
                    <select name="type_power" className="form-select" value={formData.type_power} onChange={handleChange}>
                        {POWER_OPTIONS.map((opt, i) => <option key={i} value={opt}>{opt}</option>)}
                    </select>
                </div>

                <div className="form-group">
                  <label>Power Usage (kWh/m²a)</label>
                  <input type="number" step="0.01" name="energy_usage_power" className="form-input" value={formData.energy_usage_power} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Heat Usage (kWh/m²a)</label>
                  <input type="number" step="0.01" name="energy_usage_heat" className="form-input" value={formData.energy_usage_heat} onChange={handleChange} />
                </div>

                <div className="form-section-title">Components</div>
                
                <div className="components-grid">
                  {formData.components.map((comp, index) => (
                    <div 
                      key={index} 
                      className={`component-item ${activeComponent === comp.type ? 'active-item' : ''}`}
                      onMouseEnter={() => setActiveComponent(comp.type)}
                      onMouseLeave={() => setActiveComponent(null)}
                      onFocus={() => setActiveComponent(comp.type)}
                      onBlur={() => setActiveComponent(null)}
                    >
                      <div className="component-header">
                        <span className="comp-code">{comp.type}</span>
                        <span className="comp-label">{comp.label}</span>
                      </div>
                      <div className="comp-inner-group">
                        <label>Area (m²)</label>
                        <input type="number" placeholder="0" className="form-input area-input" value={comp.area} onChange={(e) => handleComponentAreaChange(index, e.target.value)} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* --- Actions --- */}
            <div className="form-actions">
              {step > 1 && <button type="button" className="nav-btn prev-btn" onClick={prevStep}>Back</button>}
              {step < 3 ? (
                <button type="button" className="nav-btn next-btn" onClick={nextStep}>Next</button>
              ) : (
                <button type="button" className="submit-btn" onClick={handleSubmit} disabled={loading}>
                  {loading ? 'Running...' : 'Run Analysis'}
                </button>
              )}
            </div>

          </form>
        </div>

        {/* === right side === */}
        <div className="right-pane">
          
          {/* flash cards */}
          {(step === 1 || step === 2) && renderStackedCards()}

          {step === 3 && (
            <div className="data-ring-container concentric-mode fade-in">
              <div className="ring-ambient-glow"></div> 

              <svg viewBox="0 0 600 600" className="data-ring-svg">
                <defs>
                  <filter id="premium-drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="6" stdDeviation="8" floodColor="#000000" floodOpacity="0.15" />
                  </filter>
                </defs>

                {formData.components.map((comp, index) => {
                  const area = Number(comp.area) || 0;
                  const radius = 100 + index * 28; 
                  const circumference = 2 * Math.PI * radius;
                  const fillRatio = (area / maxArea) * 0.75; 
                  const strokeLength = fillRatio * circumference;
                  const isActive = activeComponent === comp.type;

                  return (
                    <g key={comp.type} className={`concentric-group ${isActive ? 'active' : ''}`}>
                      <circle 
                        cx="300" cy="300" r={radius} 
                        fill="none" stroke="rgba(0,0,0,0.03)" strokeWidth="20" 
                      />
                      <circle 
                        cx="300" cy="300" r={radius} 
                        fill="none" 
                        stroke={COMPONENT_COLORS[comp.type]} 
                        strokeWidth={isActive ? 24 : 20} 
                        strokeLinecap="round"
                        className="concentric-segment"
                        filter={isActive ? "url(#premium-drop-shadow)" : "none"}
                        style={{
                          strokeDasharray: `${circumference} ${circumference}`,
                          strokeDashoffset: circumference - strokeLength,
                          opacity: area === 0 ? 0 : 1,
                          transition: 'stroke-dashoffset 0.8s cubic-bezier(0.16, 1, 0.3, 1), stroke-width 0.4s ease, opacity 0.3s ease'
                        }}
                      />
                    </g>
                  );
                })}
              </svg>
              
              <div 
                className={`ring-center-info ${activeComponent ? 'has-active' : ''}`}
                style={{
                  width: `${centerSize}px`,
                  height: `${centerSize}px`,
                  background: centerBg,
                }}
              >
                <div className="glass-lens-inner" style={{ opacity: activeComponent ? 0 : 0.6 }}></div>
                
                <div className="ring-center-content" style={{ color: centerColor }}>
                  <span className="ring-total-label" style={{ color: activeComponent ? 'rgba(255,255,255,0.8)' : '#9CA3AF' }}>
                    {displayName}
                  </span>
                  
                  <div className="ring-value-group">
                    <span className="ring-total-value">
                      {displayValue}
                    </span>
                    <span className="ring-unit">{displayUnit}</span>
                  </div>

                  {showAbsoluteArea && (
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, opacity: 0.9, marginTop: '4px' }}>
                      {activeCompData.area} m²
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
        </div>
      </div>

      {calcResult && (
        <Dashboard 
          calcResult={calcResult} 
          onReset={() => setCalcResult(null)} 
        />
      )}
    </div>
  );
};

export default BuildingForm;