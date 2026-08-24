// Dashboard.jsx
import React, { useState, useEffect, useRef, useMemo } from 'react';
import * as echarts from 'echarts';
import { X, Download, TrendingUp, Layers, AlertCircle, FileText, List } from 'lucide-react';
import './Dashboard.css'; 

const formatNumber = (val) => {
  if (val === 0 || !val) return "0";
  const num = Number(val);
  if (Math.abs(num) < 0.01) return num.toExponential(2);
  return num.toLocaleString('en-US', { maximumFractionDigits: 2 });
};

const BASE_COLORS = ['#3B82F6', '#F59E0B', '#10B981', '#8B5CF6', '#EC4899', '#6366F1', '#F97316', '#14B8A6'];

const Dashboard = ({ calcResult, onReset }) => {
  const chartRef = useRef(null);
  
  const hasData = calcResult && calcResult.groups && calcResult.groups.length > 0;
  const [selectedGroup, setSelectedGroup] = useState(hasData ? calcResult.groups[0].name : '');

  useEffect(() => {
    if (hasData && selectedGroup === '') {
        setSelectedGroup(calcResult.groups[0].name);
    }
  }, [calcResult, hasData, selectedGroup]);

  const activeData = useMemo(() => {
    if (!hasData) return null;
    return calcResult.groups.find(g => g.name === selectedGroup) || calcResult.groups[0];
  }, [calcResult, selectedGroup, hasData]);

  const legendItems = useMemo(() => {
    if (!activeData) return [];
    const hasSubLines = activeData.sub_lines && Object.keys(activeData.sub_lines).length > 0;
    
    if (hasSubLines) {
        return Object.keys(activeData.sub_lines).map((name, idx) => ({
            name: name,
            color: BASE_COLORS[idx % BASE_COLORS.length]
        }));
    } else if (activeData.total_line && activeData.total_line.length > 0) {
        return [{
            name: `${selectedGroup.split(':')[1] || selectedGroup} (Cumulative)`,
            color: '#3B82F6'
        }];
    }
    return [];
  }, [activeData, selectedGroup]);

  const globalTotal = useMemo(() => calcResult?.total_impact || 0, [calcResult]);

  useEffect(() => {
    const myChart = echarts.init(chartRef.current);
    if (!activeData) {
        myChart.clear(); 
        return;
    }

    const startYear = new Date().getFullYear(); 
    const refArray = activeData.total_line?.length > 0 ? activeData.total_line : Object.values(activeData.sub_lines || {})[0];
    if (!refArray) { myChart.clear(); return; }
    
    const years = refArray.map((_, i) => startYear + i);
    const seriesData = [];

    const premiumEmphasis = {
        focus: 'series',
        itemStyle: {
            borderColor: '#ffffff',
            borderWidth: 2,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
            shadowBlur: 4
        }
    };

    const hasSubLines = activeData.sub_lines && Object.keys(activeData.sub_lines).length > 0;

    if (hasSubLines) {
        let colorIdx = 0;
        Object.entries(activeData.sub_lines).forEach(([lineName, dataArr]) => {
            seriesData.push({
                name: lineName,
                type: 'line',
                data: dataArr,
                smooth: 0.3,
                showSymbol: false, 
                symbol: 'circle',
                symbolSize: 8,
                emphasis: premiumEmphasis,
                lineStyle: { width: 1.5, type: 'solid' }, 
                itemStyle: { color: BASE_COLORS[colorIdx % BASE_COLORS.length] },
                areaStyle: { color: BASE_COLORS[colorIdx % BASE_COLORS.length], opacity: 0.08 }
            });
            colorIdx++;
        });
    } else if (activeData.total_line && activeData.total_line.length > 0) {
        seriesData.push({
            name: `${selectedGroup.split(':')[1] || selectedGroup} (Cumulative)`,
            type: 'line',
            data: activeData.total_line,
            smooth: 0.3,
            showSymbol: false,
            symbol: 'circle',
            symbolSize: 8,
            emphasis: premiumEmphasis,
            itemStyle: { color: '#3B82F6' },
            lineStyle: { width: 2, type: 'solid' },
            areaStyle: { color: '#3B82F6', opacity: 0.08 } 
        });
    }

    const option = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'transparent',
        textStyle: { color: '#F8FAFC' },
        axisPointer: { type: 'line', lineStyle: { color: '#94A3B8', type: 'dashed' } },
        formatter: (params) => {
          params.sort((a, b) => b.value - a.value);
          let html = `<div style="padding: 4px 8px; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 8px;">Year: ${params[0].name}</div>`;
          params.forEach(p => {
             html += `<div style="display:flex; justify-content:space-between; gap: 24px; font-size: 13px; padding: 0 8px; align-items: center;">
                        <span><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${p.color}; margin-right:6px;"></span><span style="color:#cbd5e1">${p.seriesName}</span></span>
                        <span style="font-family: ui-monospace, monospace; font-weight: 600; color: ${p.color}">${formatNumber(p.value)}</span>
                      </div>`;
          });
          return html;
        }
      },
      grid: { left: '8%', right: '5%', bottom: '22%', top: '18%', containLabel: true },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 }, 
        { type: 'slider', bottom: 12, height: 20, borderColor: 'transparent', backgroundColor: 'rgba(255,255,255,0.3)', fillerColor: 'rgba(148, 163, 184, 0.2)' }
      ],
      xAxis: {
        type: 'category', 
        boundaryGap: false, 
        data: years,
        name: 'Year',
        nameLocation: 'middle',
        nameGap: 35, 
        nameTextStyle: { color: '#64748B', fontWeight: 700, fontSize: 14 },
        axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } }, 
        axisTick: { show: false },
        axisLabel: { color: '#64748B', margin: 12, fontFamily: 'ui-sans-serif, system-ui', showMaxLabel: true }
      },
      yAxis: {
        type: 'value', min: 0, 
        name: 'Absolute Global Warming Potential\n(AGWP) [W m⁻² yr]', 
        
        nameTextStyle: { 
            color: '#64748B', 
            padding: [0, 0, 15, -60], 
            fontWeight: 600, 
            lineHeight: 18, 
            align: 'left' 
        },
        splitLine: { lineStyle: { type: 'dashed', color: 'rgba(0,0,0,0.05)' } },
        axisLabel: { color: '#64748B', formatter: (value) => formatNumber(value), fontFamily: 'ui-monospace, monospace' }
      },
      series: seriesData
    };

    myChart.setOption(option, true);
    const handleResize = () => myChart.resize();
    window.addEventListener('resize', handleResize);
    return () => { window.removeEventListener('resize', handleResize); myChart.dispose(); };
  }, [activeData, selectedGroup]);

  if (!calcResult) return null;

  const glassCardStyle = {
    background: 'rgba(255, 255, 255, 0.75)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.9)',
    boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.05)',
    borderRadius: '24px'
  };

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 999, display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(255, 255, 255, 0.2)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' }}>
      
      <button onClick={onReset} style={{ ...glassCardStyle, position: 'absolute', top: '24px', right: '32px', width: '48px', height: '48px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', zIndex: 1000, transition: 'transform 0.2s' }} onMouseOver={(e)=>e.currentTarget.style.transform='scale(1.05)'} onMouseOut={(e)=>e.currentTarget.style.transform='scale(1)'}>
        <X size={24} color="#475569" />
      </button>

      <div style={{ display: 'flex', gap: '24px', width: '95%', maxWidth: '1440px', height: '85vh' }}>
        
        <div style={{ width: '380px', display: 'flex', flexDirection: 'column', gap: '24px', flexShrink: 0 }}>
          <div style={{ ...glassCardStyle, padding: '24px', flexShrink: 0, maxHeight: '35%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <List size={16} color="#3B82F6"/>
                Chart Annotations
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto', paddingRight: '4px' }}>
              {legendItems.map((item, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                  <div style={{ width: '18px', height: '4px', backgroundColor: item.color, borderRadius: '2px', marginTop: '8px', flexShrink: 0 }}></div>
                  <span style={{ fontSize: '13px', color: '#334155', fontWeight: 600, lineHeight: 1.4 }}>{item.name}</span>
                </div>
              ))}
              {legendItems.length === 0 && (
                <span style={{ fontSize: '13px', color: '#94A3B8' }}>Select a report to view legends.</span>
              )}
            </div>
          </div>

          <div style={{ ...glassCardStyle, padding: '24px', display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
               <Layers size={16} color="#10B981"/> Generated PDF Reports
            </div>
            
            {!hasData ? (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#94A3B8', textAlign: 'center', gap: '12px' }}>
                    <AlertCircle size={32} />
                    <span>Processing LCA Reports...</span>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto', paddingRight: '4px', flex: 1 }}>
                  {calcResult.groups.map((group, idx) => {
                      const isActive = selectedGroup === group.name;
                      const isTotal = group.name.startsWith("1.");
                      const isOverview = group.name.startsWith("2.");
                      
                      return (
                          <div 
                              key={idx} onClick={() => setSelectedGroup(group.name)}
                              style={{
                                  padding: '14px 16px', borderRadius: '16px', border: '1px solid', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px', transition: 'all 0.2s',
                                  background: isActive ? (isTotal ? 'rgba(16, 185, 129, 0.15)' : 'rgba(59, 130, 246, 0.15)') : 'rgba(255, 255, 255, 0.4)',
                                  borderColor: isActive ? (isTotal ? 'rgba(16, 185, 129, 0.4)' : 'rgba(59, 130, 246, 0.4)') : 'rgba(255, 255, 255, 0.6)',
                                  color: isActive ? (isTotal ? '#047857' : '#1D4ED8') : '#475569'
                              }}
                          >
                              {isTotal ? <TrendingUp size={18} color={isActive ? '#10B981' : '#94A3B8'} /> 
                                       : (isOverview ? <Layers size={18} color={isActive ? '#3B82F6' : '#94A3B8'} />
                                                     : <FileText size={18} color={isActive ? '#3B82F6' : '#94A3B8'} />)}
                              <span style={{ fontWeight: isActive ? 700 : 500, fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                  {group.name}
                              </span>
                          </div>
                      );
                  })}
                </div>
            )}
          </div>
        </div>

        <div style={{ ...glassCardStyle, flex: 1, padding: '32px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
            <div style={{ flex: 1, paddingRight: '20px' }}>
                <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#0F172A', margin: 0, letterSpacing: '-0.02em', wordBreak: 'break-word' }}>
                    {hasData ? selectedGroup.split('. ')[1] || selectedGroup : 'Awaiting Data...'}
                </h2>
            </div>
            
            {activeData?.pdf && (
                <a 
                    href={activeData.pdf} download={`${selectedGroup.replace(/[\/\\?%*:|"<>]/g, '-')}.pdf`}
                    style={{
                        display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', 
                        background: 'rgba(15, 23, 42, 0.85)', backdropFilter: 'blur(10px)', color: 'white', 
                        borderRadius: '14px', fontSize: '13px', fontWeight: 600, textDecoration: 'none', 
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)', flexShrink: 0, transition: 'transform 0.1s'
                    }}
                    onMouseOver={(e)=>e.currentTarget.style.transform='translateY(-2px)'} 
                    onMouseOut={(e)=>e.currentTarget.style.transform='translateY(0)'}
                >
                    <Download size={16} /> Download Original PDF
                </a>
            )}
          </div>
          
          <div style={{ flex: 1, position: 'relative', minHeight: 0, width: '100%' }}>
              <div ref={chartRef} style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;