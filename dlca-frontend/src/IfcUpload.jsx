// src/IfcUpload.jsx
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Check, Loader2, Box, FileCode, Layers, Database, 
  Calculator, Upload, X, BarChart2, Download, ChevronDown
} from 'lucide-react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './IfcUpload.css';
import { uploadIfc } from './API';
import Dashboard from './Dashboard';

const COMPONENT_DICTIONARY = {
  "EW": [
    { id: "EWmas_1", materials: "clay brick, cement mortar, glass wool, plaster" },
    { id: "EWmas_improve1", materials: "clay brick, cement mortar, glass wool (thicker)" },
    { id: "EWwood_1", materials: "structural timber, cellulose fibre, gypsum" },
    { id: "CW_h_1", materials: "polystyrene extruded (XPS), clay brick, bitumen, basement" }
  ],
  "IW": [
    { id: "IWmas_1", materials: "clay brick, cement mortar, plaster" },
    { id: "IWmas_improve1", materials: "clay brick, cement mortar, plaster (thicker)" },
    { id: "IWwood_1", materials: "structural timber, cellulose fibre, gypsum" }
  ],
  "FL": [
    { id: "FLmas_1", materials: "concrete, reinforcing steel, polystyrene foam" },
    { id: "FLmas_improve1", materials: "concrete, reinforcing steel, polystyrene foam (thicker)" },
    { id: "FLmas_improve2", materials: "concrete, reinforcing steel, glass wool mat" },
    { id: "FLmas_improve3", materials: "concrete, reinforcing steel, glass wool mat (thicker)" },
    { id: "FLwood_1", materials: "structural timber, autoclaved aerated concrete block" }
  ],
  "FRO": [
    { id: "FROmas_1", materials: "concrete, polystyrene foam slab, bitumen seal, PVC film" },
    { id: "FROmas_improve1", materials: "concrete, polystyrene foam slab, bitumen seal (thicker)" },
    { id: "FROmas_improve2", materials: "concrete, glass wool mat, bitumen seal" },
    { id: "FROmas_improve3", materials: "concrete, glass wool mat, bitumen seal (thicker)" },
    { id: "FROwood_1", materials: "structural timber, OSB, cellulose fibre" }
  ],
  "PRO": [
    { id: "PRO_h_1", materials: "structural timber, cellulose fibre, glass wool, pitched roof" }
  ],
  "BP": [
    { id: "BP_h_1", materials: "concrete, lean concrete, polystyrene extruded (XPS)" }
  ],
  "WIN": [
    { id: "WINwoodalu_1", materials: "window frame wood-metal, triple glazing" },
    { id: "WINwood_1", materials: "window frame wood, triple glazing" },
    { id: "WINalu_1", materials: "window frame aluminium, triple glazing" }
  ]
};

const getComponentDetails = (epd_id) => {
  if (!epd_id) return { category: "EW", materials: "Unknown" };
  for (const [category, options] of Object.entries(COMPONENT_DICTIONARY)) {
    const found = options.find(opt => opt.id === epd_id);
    if (found) return { category, materials: found.materials };
  }
  
  let category = "EW";
  if(epd_id.includes("FL")) category = "FL";
  if(epd_id.includes("IW")) category = "IW";
  if(epd_id.includes("FRO") || epd_id.includes("PRO")) category = "FRO";
  if(epd_id.includes("WIN")) category = "WIN";
  if(epd_id.includes("BP")) category = "BP";
  return { category, materials: "No detailed material info found." };
};

const enforceSpecificComponent = (rawId) => {
  if (!rawId) return "Unmapped";
  const fallbacks = {
    "EW": "EWmas_1",
    "FL": "FLmas_1",
    "IW": "IWmas_1",
    "FRO": "FROmas_1",
    "PRO": "PRO_h_1",
    "BP": "BP_h_1",
    "WIN": "WINwoodalu_1"
  };
  return fallbacks[rawId] || rawId;
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="hud-glass-tooltip">
        <p className="tooltip-year">Year {label}</p>
        <p className="tooltip-value">
          {Number(payload[0].value).toLocaleString()}
          <span className="unit"> kgCO₂e</span>
        </p>
      </div>
    );
  }
  return null;
};

const IfcUpload = () => {
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [fileName, setFileName] = useState('');
  const [fullData, setFullData] = useState(null); 
  const [mappings, setMappings] = useState({}); 
  const [calcResult, setCalcResult] = useState(null); 
  const [hoverYear, setHoverYear] = useState(100);
  const [isCalculating, setIsCalculating] = useState(false);
  
  const fileInputRef = useRef(null);

  const chartData = useMemo(() => {
    if (!calcResult?.yearly_data) return [];
    return calcResult.yearly_data.map((val, index) => ({
      year: index,
      impact: Number(val.toFixed(2))
    }));
  }, [calcResult]);

  useEffect(() => {
    if (status === 'done' && fullData?.materials) {
      const getSuggestions = async () => {
        const newMappings = {};
        for (const mat of fullData.materials) {
          try {
            const res = await axios.post('http://localhost:5001/api/ifc/suggest_mapping', { material_name: mat.material_name });
            
            newMappings[mat.material_name] = res.data;
          } catch (e) { console.error("Mapping error", e); }
        }
        setMappings(newMappings);
      };
      getSuggestions();
    }
  }, [status, fullData]);

  useEffect(() => {
    if (chartData.length > 0) setHoverYear(chartData.length - 1);
  }, [chartData]);

  const processFile = async (file) => {
    if (!file) return;
    setFileName(file.name); setStatus('processing'); setProgress(10);
    try {
      const data = await uploadIfc(file, (p) => setProgress(p));
      setFullData(data); setProgress(100); setTimeout(() => setStatus('done'), 500);
    } catch (error) {
      alert(`Analysis failed: ${error.message}`); setStatus('idle');
    }
  };

  const handleMappingChange = (materialName, newTargetId) => {
    setMappings(prev => ({
      ...prev,
      [materialName]: newTargetId
    }));
  };

  const handleRunCalculation = async () => {
    setIsCalculating(true); setCalcResult(null);
    const payload = fullData.materials.map(mat => {
      const mapVal = mappings[mat.material_name];
      const targetId = typeof mapVal === 'string' ? mapVal : (mapVal?.epd_id || "EWmas_1");
      return {
        material_name: mat.material_name,
        quantity: mat.quantity,
        epd_id: targetId
      };
    });
    try {
      const res = await axios.post('http://localhost:5001/api/ifc/calculate_carbon', payload);
      if (res.data) setCalcResult(res.data);
    } catch (e) { alert("Calculation failed"); } finally { setIsCalculating(false); }
  };

  const resetUpload = () => {
    setStatus('idle'); setProgress(0); setFileName(''); setFullData(null); setCalcResult(null);
  };

  return (
    <div className="liquid-container">
      <input type="file" ref={fileInputRef} onChange={(e) => processFile(e.target.files[0])} style={{ display: 'none' }} />
      
      <div className="ambient-canvas">
        <div className="liquid-ball ball-1"></div>
        <div className="liquid-ball ball-2"></div>
        <div className="liquid-ball ball-3"></div>
        <div className="liquid-ball ball-4"></div>
        <div className="liquid-ball ball-5"></div>
      </div>

      {!calcResult ? (
        <div className="main-stage">
          {status !== 'done' && (
            <div className="upload-stage fade-in">
              <div className={`liquid-drop ${status}`} onClick={() => status === 'idle' && fileInputRef.current.click()}>
                <div className="drop-content">
                  {status === 'idle' && (
                    <div className="idle-content">
                      <Upload size={32} className="drop-icon-svg" />
                      <h2 className="liquid-title">Upload IFC</h2>
                    </div>
                  )}
                  {status === 'processing' && (
                    <div className="processing-content">
                      <Loader2 className="spin-icon" size={32} />
                      <span className="liquid-percent">{progress}%</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {status === 'done' && fullData && (
            <div className="dashboard-stage fade-in-up">
              <div className="bento-dashboard-wrapper">
                
                <div className="bento-header" style={{ marginBottom: '1.5rem' }}>
                  <div>
                    <h2 className="dashboard-title">Model Insights</h2>
                    <p className="dashboard-subtitle">Analysis complete. Ready for Carbon Evaluation.</p>
                  </div>
                </div>

                <div className="bento-grid">
                  
                  <div className="bento-card col-span-2 highlight-card">
                    <span className="bento-label"><Layers size={14} /> Total Floor Area</span>
                    <div className="bento-value-group">
                      <span className="bento-value">
                        {fullData.materials.reduce((sum, m) => sum + m.quantity, 0).toLocaleString(undefined, {maximumFractionDigits: 1})}
                      </span>
                      <span className="bento-unit">m²</span>
                    </div>
                    <span className="bento-subtext">↑ 100% Geometry extracted</span>
                    <div className="mini-progress-bg">
                      <div className="mini-progress-fill" style={{width: '85%'}}></div>
                    </div>
                  </div>

                  <div className="bento-card center-content">
                     <span className="bento-label" style={{marginBottom: 'auto'}}>Success Rate</span>
                     <div className="gauge-circle">
                        <span className="gauge-value">100<span className="gauge-unit">%</span></span>
                     </div>
                  </div>

                  <div className="bento-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div style={{ marginBottom: '1rem' }}>
                      <span className="bento-label"><FileCode size={14} /> Source File</span>
                      <div className="bento-value text-multiline" style={{ fontSize: '1.05rem', marginTop: '4px' }} title={fileName}>
                        {fileName}
                      </div>
                    </div>
                    <div>
                      <span className="bento-label"><Database size={14} /> Auto-Mapped</span>
                      <div style={{ marginTop: '4px' }}>
                        <span className="bento-value" style={{ fontSize: '1.8rem' }}>{fullData.materials.length}</span>
                        <span className="bento-unit" style={{marginLeft: '4px'}}>materials</span>
                      </div>
                    </div>
                  </div>

                  <div className="bento-card col-span-2 highlight-card">
                    <span className="bento-label"><Box size={14} /> Elements Breakdown</span>
                    <div className="bento-value-group" style={{ marginTop: '4px', marginBottom: '10px' }}>
                      <span className="bento-value">{fullData.counts.elements_total}</span>
                      <span className="bento-unit" style={{ marginBottom: '6px' }}>total</span>
                    </div>
                    <div className="elements-breakdown-list-wide">
                      {fullData.counts.by_type && Object.entries(fullData.counts.by_type)
                        .sort(([, a], [, b]) => b - a)
                        .map(([type, count], idx) => (
                          <div key={idx} className="breakdown-row">
                            <span className="breakdown-name" title={type}>
                              {type.replace(/^Ifc/i, '')}
                            </span>
                            <span className="breakdown-dots"></span>
                            <span className="breakdown-count">{count}</span>
                          </div>
                      ))}
                    </div>
                  </div>

                  <div className="bento-card col-span-3 list-card">
                    <div className="stream-header">
                      <span className="bento-label"><Database size={14} /> Material Stream</span>
                      <span className="stream-header-right">Mapping Target</span>
                    </div>
                    
                    
                    <div className="stream-list">
                      {fullData.materials.map((mat, i) => {
                        const rawTarget = typeof mappings[mat.material_name] === 'string' 
                            ? mappings[mat.material_name] 
                            : (mappings[mat.material_name]?.epd_id || "Unmapped");
                        
                        const mappedTarget = enforceSpecificComponent(rawTarget);
                        
                        let badgeClass = "status-badge default";
                        if (mappedTarget.includes("FL")) badgeClass = "status-badge green";
                        else if (mappedTarget.includes("EW") || mappedTarget.includes("CW")) badgeClass = "status-badge blue";
                        else if (mappedTarget.includes("IW")) badgeClass = "status-badge orange";
                        
                        const details = getComponentDetails(mappedTarget);
                        const availableOptions = COMPONENT_DICTIONARY[details.category] || [];

                        return (
                          <div key={i} className="stream-row">
                            
                            <span className="stream-name" title={mat.material_name}>{mat.material_name}</span>
                            
                            <span className="stream-qty">{mat.quantity.toFixed(1)} <span className="stream-qty-unit">m²</span></span>
                            
                            <div className="mapping-dropdown-wrapper custom-tooltip-container">
                              <div className="select-icon-wrapper">
                                <select 
                                  value={mappedTarget}
                                  onChange={(e) => handleMappingChange(mat.material_name, e.target.value)}
                                  className={`custom-mapping-select ${badgeClass}`}
                                  disabled={mappedTarget === "Unmapped"}
                                >
                                  {mappedTarget === "Unmapped" && <option value="Unmapped">Pending...</option>}
                                  {availableOptions.map(opt => (
                                    <option key={opt.id} value={opt.id}>
                                      {opt.id}
                                    </option>
                                  ))}
                                  {!availableOptions.find(o => o.id === mappedTarget) && mappedTarget !== "Unmapped" && (
                                    <option value={mappedTarget}>{mappedTarget}</option>
                                  )}
                                </select>
                                
                                {mappedTarget !== "Unmapped" && (
                                  <ChevronDown size={14} className="dropdown-caret" />
                                )}
                              </div>

                              <div className="custom-material-tooltip">
                                <div className="tooltip-title">Core Materials</div>
                                <div className="tooltip-content">{details.materials}</div>
                              </div>
                            </div>

                          </div>
                        )
                      })}
                    </div>
                  </div>

                </div>
                
                <div className="bento-footer-large">
                  <button className="bento-run-btn-large" onClick={handleRunCalculation} disabled={isCalculating}>
                    {isCalculating ? <Loader2 className="spin-icon" size={20}/> : <Calculator size={20}/>}
                    {isCalculating ? "Calculating..." : "Generate Analysis Report"}
                  </button>
                  <button className="reset-link" onClick={resetUpload}>Start New Model</button>
                </div>

              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="hud-overlay-container fade-in">
           <Dashboard calcResult={calcResult} onReset={resetUpload} />
        </div>
      )}
    </div>
  );
};

export default IfcUpload;