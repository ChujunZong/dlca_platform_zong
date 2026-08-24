import React, { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import './Neo4jGraphPanel.css'; 

const RollingNumber = ({ value }) => {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const end = parseInt(value, 10) || 0;
    if (end === 0) { setDisplay(0); return; }
    const duration = 1200; 
    const frameRate = 1000 / 60; 
    const totalFrames = Math.round(duration / frameRate);
    let frame = 0;
    const counter = setInterval(() => {
      frame++;
      const progress = frame / totalFrames;
      const current = Math.round(end * (1 - Math.pow(1 - progress, 4))); 
      setDisplay(current);
      if (frame >= totalFrames) clearInterval(counter);
    }, frameRate);
    return () => clearInterval(counter);
  }, [value]);
  return <span>{display}</span>;
};

// 预设查询字典 
const PRESETS = {
  "Full Material Pipeline (Building → Raw Material)": `MATCH (b:Building)-[o]-(bc: Building_component)-[d]-(i:Initial_material_LCIA)-[q]-(ir: Initial_rawmaterial_LCIA) RETURN b,o,bc,d,i,q,ir LIMIT 50`,
  "Dynamic Power Mix Ecosystem": `MATCH (e:Initial_powermix_LCIA)-[t]-(o) OPTIONAL MATCH (o)-[x]-(df:Dynamic_factor_b7_elementamount) OPTIONAL MATCH (o)-[y]-(i:Initial_material_LCIA) OPTIONAL MATCH (o)-[z]-(iw:Initial_waste_LCIA) OPTIONAL MATCH (o)-[xx]-(ir:Initial_rawmaterial_LCIA)-[xxx]-(i2:Initial_material_LCIA) RETURN e, t, o, x, df, y, i, z, iw, xx, ir, xxx, i2 LIMIT 50`,
  "Waste to Treatment & Power Mix": `MATCH (iw:Initial_waste_LCIA) OPTIONAL MATCH (iw)-[o]-(iwt:Initial_wastetreatment_LCIA)-[p]-(e:Initial_powermix_LCIA) RETURN iw,o,iwt,p,e LIMIT 50`,
  "Raw Material & Waste Ratio": `MATCH (ir:Initial_rawmaterial_LCIA) OPTIONAL MATCH (ir)-[o]-(wtr:Waste_treatment_ratio) RETURN ir,o,wtr LIMIT 50`,
  "Material & Transport Pipeline": `MATCH (i:Initial_material_LCIA) OPTIONAL MATCH (i)-[o]-(it:Initial_transport_LCIA) RETURN i,o,it LIMIT 50`,
  "Energy Source & Heat Distribution": `MATCH (h:Initial_heat_LCIA) OPTIONAL MATCH (h)-[o]-(es:Initial_energysource_LCIA) RETURN h,o,es LIMIT 50`
};

const NODE_COLORS = { 
  Building: "#A2B881", 
  Building_component: "#53A7EA", 
  Dynamic_factor_b1: "#92E692",
  Dynamic_factor_b2: "#92E692",
  Dynamic_factor_b3b4b5: "#6EE6D1",
  Dynamic_factor_b7_elementamount: "#F2B5F2",
  Initial_energysource_LCIA: "#C0C985",
  Initial_heat_LCIA: "#60B6B6",
  Initial_heatgroup_LCIA: "#B28AE6",
  Initial_material_LCIA: "#B8B061",
  Initial_powermix_LCIA: "#EAA1A1",
  Initial_powermixgroup_LCIA: "#6ACCA9",
  Initial_powertransformation_LCIA: "#A4C0D9",
  Initial_powertransmissionnetwork_LCIA: "#BDE2E8",
  Initial_rawmaterial_LCIA: "#FCE464",
  Initial_transport_LCIA: "#DE9F6A",
  Initial_transportgroup_LCIA: "#AAA0EA",
  Initial_waste_LCIA: "#F28EBE",
  Initial_wastetreatment_LCIA: "#F0B58A",
  Waste_treatment_ratio: "#F29C70"
};

export default function Neo4jGraphPanel() {
  const graphRef = useRef();
  const rightPanelRef = useRef(); 
  const chatContainerRef = useRef(null); 
  
  const [splashState, setSplashState] = useState('visible'); 
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredLink, setHoveredLink] = useState(null);

  const [manualCypher, setManualCypher] = useState(PRESETS["Full Material Pipeline (Building → Raw Material)"]);
  const [manualLoading, setManualLoading] = useState(false);

  const [isChatExpanded, setIsChatExpanded] = useState(false);

  const [chatInput, setChatInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  
  
  const [messages, setMessages] = useState([
    { 
      role: 'bot', 
      text: 'Hello! I am your AI Data Topology Assistant. You can type naturally or click an example below to get started:',
      examples: [
        "Query the full pipeline from building to raw materials",
        "Show the relationship between waste, treatment, and power mix",
        "Explore the connection between raw materials and power mix",
        "View the distribution of energy sources and heat"
      ]
    }
  ]);

  const getNodeColor = (node) => NODE_COLORS[node.label] || "#94a3b8";
  const activeLabels = Array.from(new Set(graphData.nodes.map(n => n.label)));

  const getDisplayName = (node) => {
    if (typeof node.name === 'string') return node.name;
    if (typeof node.NAME === 'string') return node.NAME; 
    if (typeof node.title === 'string') return node.title;
    return node.label; 
  };

  
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages]);

  useEffect(() => {
    if (graphRef.current && graphData.nodes.length > 0) {
      graphRef.current.d3Force('charge').strength(-400); 
      graphRef.current.d3Force('link').distance(80);    
    }
  }, [graphData]);

  useEffect(() => {
    const updateDimensions = () => {
      if (rightPanelRef.current) {
        setDimensions({ width: rightPanelRef.current.offsetWidth, height: rightPanelRef.current.offsetHeight });
      }
    };
    window.addEventListener('resize', updateDimensions);
    updateDimensions();
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const runManualQuery = async () => {
    setManualLoading(true);
    setSelectedNode(null); 
    try {
      const response = await fetch("http://localhost:5001/api/neo4j/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cypher: manualCypher })
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setGraphData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setManualLoading(false);
    }
  };

  const handleChatSubmit = async (e, directText = null) => {
    if (e) e.preventDefault();
    const userText = directText || chatInput.trim();
    if (!userText || isProcessing) return;

    setChatInput("");
    setIsProcessing(true);
    setSelectedNode(null);

    setMessages(prev => [
      ...prev, 
      { role: 'user', text: userText },
      { role: 'bot', text: 'Summoning AI to write the query...', isLoading: true }
    ]);

    try {
      const llmRes = await fetch("http://localhost:5001/api/llm/semantic-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userText, topK: 50 })
      });
      const llmData = await llmRes.json();
      
      
      if (llmData.raw && llmData.raw.includes("[MOCK]")) {
        throw new Error(`Local LLM service is not connected: ${llmData.raw}`);
      }

      if (!llmRes.ok || !llmData.cypher) throw new Error(llmData.error || "The model did not return a valid query.");

      const generatedCypher = llmData.cypher;

      setMessages(prev => {
        const newMsg = [...prev];
        newMsg[newMsg.length - 1] = { 
          role: 'bot', text: 'Query generated! Fetching topology data...', cypher: generatedCypher, isLoading: true 
        };
        return newMsg;
      });

      const dbRes = await fetch("http://localhost:5001/api/neo4j/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cypher: generatedCypher })
      });
      const dbData = await dbRes.json();

      if (!dbRes.ok || dbData.error) throw new Error(dbData.error || "Database query failed.");

      setGraphData(dbData);

     setMessages(prev => {
        const newMsg = [...prev];
        newMsg[newMsg.length - 1] = { 
          role: 'bot', 
          text: `✅ Query successful! Found ${dbData.nodes.length} nodes and ${dbData.links.length} relations.`, 
          nodes: dbData.nodes, 
          isLoading: false 
        };
        return newMsg;
      });

    } catch (err) {
      setMessages(prev => {
        const newMsg = [...prev];
        newMsg[newMsg.length - 1] = { role: 'error', text: `❌ Sorry, an error occurred: ${err.message}`, isLoading: false };
        return newMsg;
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExplore = () => {
    setSplashState('fading'); 
    setTimeout(() => { setSplashState('hidden'); }, 600);
  };

  return (
    <div className="neo4j-page-container">
      <div className="immersive-graph-wrapper">
        
        <div className="graph-left-panel">
          
          <div className="bento-box bento-header">
            <h2 className="hud-title">Data Topology</h2>
            <p className="hud-subtitle">AI-Driven Graph Explorer</p>
          </div>

          {!isChatExpanded ? (
            <>
              <div className="bento-box bento-stats">
                <div className="hud-stats">
                  <div className="stat-pill">Nodes <span><RollingNumber value={graphData.nodes.length} /></span></div>
                  <div className="stat-pill">Relations <span><RollingNumber value={graphData.links.length} /></span></div>
                </div>
                <div className="legend-section">
                  {activeLabels.length > 0 ? (
                    <>
                      <h4 className="legend-title">Entity Types</h4>
                      <div className="legend-grid">
                        {activeLabels.map(label => (
                          <div key={label} className="legend-item">
                            <div className="legend-color" style={{ backgroundColor: NODE_COLORS[label] || "#94a3b8" }}></div>
                            <span className="legend-text">{label}</span>
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <div className="empty-legend">Waiting for data...</div>
                  )}
                </div>
              </div>

              <div className="bento-box bento-control">
                <span className="control-label">Select Query Pattern</span>
                <select className="dock-select" onChange={(e) => setManualCypher(PRESETS[e.target.value])} defaultValue="Full Material Pipeline (Building → Raw Material)">
                  {Object.keys(PRESETS).map(k => <option key={k} value={k}>{k}</option>)}
                </select>
                <button className={`dock-btn ${manualLoading ? 'loading' : ''}`} onClick={runManualQuery} disabled={manualLoading}>
                  <span className="btn-text">{manualLoading ? "Simulating..." : "Visualize"}</span>
                </button>
              </div>

              <div className="bento-ai-trigger" onClick={() => setIsChatExpanded(true)}>
                <div className="robot-icon">🤖</div>
                <p className="trigger-text">Activate AI Assistant</p>
              </div>
            </>
          ) : (
            <div className="bento-box bento-chat expanded">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' }}>
                <span className="control-label">🤖 AI ASSISTANT</span>
                <button 
                  onClick={() => setIsChatExpanded(false)} 
                  style={{ background: '#f1f5f9', border: 'none', color: '#64748b', cursor: 'pointer', fontWeight: 'bold', padding: '4px 10px', borderRadius: '8px' }}
                >
                  Exit Chat ↧
                </button>
              </div>


              <div className="chat-history" ref={chatContainerRef}>
                {messages.map((m, idx) => (
                  <div key={idx} className={`chat-bubble ${m.role}`}>
                    <div className="chat-text">{m.text}</div>
                    
                    {m.examples && (
                      <div className="chat-examples">
                        {m.examples.map((ex, i) => (
                          <button key={i} className="example-chip" onClick={() => handleChatSubmit(null, ex)} disabled={isProcessing}>
                            {ex}
                          </button>
                        ))}
                      </div>
                    )}


                    {m.nodes && m.nodes.length > 0 && (
                      <div style={{ marginTop: '12px', background: '#ffffff', padding: '12px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                        <h4 style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px', marginTop: 0 }}>
                          Entity Types
                        </h4>
                        <div style={{ display: 'grid', gridTemplateColumns: 'column', gap: '10px' }}>
                          
                          {Array.from(new Set(m.nodes.map(n => n.label))).map(label => (
                            <div key={label} style={{ display: 'flex', alignItems: 'center' }}>
                              <div style={{ 
                                width: '12px', height: '12px', borderRadius: '4px', marginRight: '8px', flexShrink: 0,
                                backgroundColor: getNodeColor({ label }) 
                              }}></div>
                              <span style={{ fontSize: '0.75rem', fontWeight: '600', color: '#475569', wordBreak: 'break-all' }}>
                                {label}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}


                  </div>
                ))}
              </div>

              <form className="chat-input-area" onSubmit={(e) => handleChatSubmit(e)}>
                <input 
                  type="text" 
                  className="chat-input"
                  placeholder={isProcessing ? "AI is thinking..." : "Type to explore..."}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  disabled={isProcessing}
                />
                <button type="submit" className="chat-send-btn" disabled={isProcessing || !chatInput.trim()}>
                  Visualize
                </button>
              </form>
            </div>
          )}
        </div>

        <div className="graph-right-panel" ref={rightPanelRef}>
          {graphData.nodes.length > 0 && dimensions.width > 0 ? (
            <ForceGraph2D
              ref={graphRef} graphData={graphData} width={dimensions.width} height={dimensions.height}
              nodeRelSize={16} nodeColor={getNodeColor} onNodeClick={(node) => setSelectedNode(node)}
              onBackgroundClick={() => setSelectedNode(null)} onLinkHover={setHoveredLink} linkHoverPrecision={6}
              
              nodeCanvasObjectMode={() => 'after'}
              nodeCanvasObject={(node, ctx, globalScale) => {
                if (globalScale < 0.8) return; 
                let labelText = getDisplayName(node);
                if (labelText.length > 9) labelText = labelText.substring(0, 8) + '..';
                const fontSize = 12 / globalScale; 
                ctx.font = `500 ${fontSize}px Inter, sans-serif`;
                ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#ffffff'; ctx.fillText(labelText, node.x, node.y);
              }}

              linkColor={() => "#cbd5e1"} linkWidth={1.5} linkDirectionalArrowLength={4} linkDirectionalArrowRelPos={1}

              linkCanvasObjectMode={() => 'after'}
              linkCanvasObject={(link, ctx, globalScale) => {
                if (globalScale < 1.2) return;
                const start = link.source; const end = link.target;
                if (typeof start !== 'object' || typeof end !== 'object') return;
                const textPos = { x: start.x + (end.x - start.x) / 2, y: start.y + (end.y - start.y) / 2 };
                const relLink = { x: end.x - start.x, y: end.y - start.y };
                let textAngle = Math.atan2(relLink.y, relLink.x);
                if (textAngle > Math.PI / 2) textAngle = -(Math.PI - textAngle);
                if (textAngle < -Math.PI / 2) textAngle = -(-Math.PI - textAngle);
                const fontSize = 10 / globalScale;
                ctx.font = `600 ${fontSize}px Inter, sans-serif`;
                ctx.save(); ctx.translate(textPos.x, textPos.y); ctx.rotate(textAngle);
                ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
                ctx.fillStyle = link === hoveredLink ? '#ef4444' : '#64748b'; 
                ctx.fillText(link.type, 0, -(fontSize / 2)); ctx.restore();
              }}
            />
          ) : (
             <div style={{ color: '#94a3b8', fontSize: '1.2rem', opacity: isChatExpanded ? 0.4 : 1, transition: '0.3s' }}>
                {isProcessing || manualLoading ? "🔍 Fetching topology network..." : "👋 Try sending a message or selecting a preset on the left to explore the topology!"}
             </div>
          )}

          {selectedNode && (
            <div className="node-detail-panel bento-box">
              <div className="detail-header">
                <h3 className="detail-title">{getDisplayName(selectedNode)}</h3>
                <button className="detail-close" onClick={() => setSelectedNode(null)}>×</button>
              </div>
              <div className="detail-content">
                <div className="prop-card">
                  <span className="prop-key">Category Type</span>
                  <span className="prop-val" style={{ color: getNodeColor(selectedNode) }}>{selectedNode.label}</span>
                </div>
                {Object.keys(selectedNode).map(key => {
                  const hiddenKeys = ['id', 'x', 'y', 'vx', 'vy', 'index', 'color', 'label', 'element_id'];
                  if (hiddenKeys.includes(key)) return null;
                  const value = typeof selectedNode[key] === 'object' ? JSON.stringify(selectedNode[key]) : String(selectedNode[key]);
                  return (
                    <div className="prop-card" key={key}>
                      <span className="prop-key">{key}</span><span className="prop-val">{value}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {splashState !== 'hidden' && (
        <div className={`graph-splash-screen ${splashState === 'fading' ? 'fading' : ''}`}>
          <div className="splash-content">
            <span className="splash-eyebrow">DEEP DIVE</span><h2 className="splash-title">Data Topology Explorer</h2>
            <p className="splash-desc">Interact with the our database using natural language. Let the AI write the queries.</p>
            <button className="splash-btn dock-btn" onClick={handleExplore}><span className="btn-text">Initialize Explorer</span></button>
          </div>
        </div>
      )}
    </div>
  );
}