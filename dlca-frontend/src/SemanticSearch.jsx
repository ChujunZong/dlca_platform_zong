import React, { useState, useRef } from 'react';
import axios from 'axios';
import NeoVis from 'neovis.js';
import './SemanticSearch.css';

const SemanticSearch = () => {
  const [query, setQuery] = useState('');
  const [cypher, setCypher] = useState('');
  const [loading, setLoading] = useState(false);
  const [candidates, setCandidates] = useState([]);
  const [execLoading, setExecLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const NUM_CANDIDATES = 5;       
  const visRef = useRef(null);

  const renderGraph = (cypherQuery) => {
    const config = {
      containerId: 'viz',
      neo4j: {
        serverUrl: 'bolt://localhost:7687',
        serverUser: 'neo4j',
        serverPassword: 'your_password', 
      },
      labels: {
        Research: { caption: 'name', size: 'pagerank', community: 'field' },
        Topic: { caption: 'name' },
      },
      relationships: {
        RELATED_TO: { caption: true, thickness: 'weight' },
      },
      initialCypher: cypherQuery,
    };

    const viz = new NeoVis(config);
    viz.render();
    visRef.current = viz;
  };

  
const handleGenerate = async () => {
  const q = query.trim();
  if (!q) return;

  setLoading(true);
  setError(null);
  setCypher('');
  setCandidates([]);

  try {
    const resp = await axios.post('/api/llm/semantic-search', {
      query: q,
      topK: 20,
      num: NUM_CANDIDATES,       
    });

    const cs = Array.isArray(resp?.data?.candidates) ? resp.data.candidates : [];
    if (cs.length) {
      setCandidates(cs);
      setCypher(resp.data.cypher || cs[0].cypher || '');
    } else {
      setCypher(resp?.data?.cypher || '');
    }
  } catch (e) {
    const status = e?.response?.status;
    const url    = e?.response?.config?.url;
    const method = e?.response?.config?.method?.toUpperCase();
    const body   = typeof e?.response?.data === 'object'
      ? JSON.stringify(e.response.data)
      : (e?.response?.data || '');
    console.error('Axios error:', status, method, url, body);
    setError(status ? `HTTP ${status} ${method} ${url}\n${body}` : (e.message || '请求失败'));
  } finally {
    setLoading(false);
  }
};

  const handleExecute = async () => {
    const c = (cypher || '').trim();
    if (!c) return;

    setExecLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await axios.post('/api/query', { cypher: c });
      setResult(resp.data);
    } catch (e) {
      setError(e?.response?.data?.error || e.message || 'Query failed');
    } finally {
      setExecLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Intelligent Semantic Search</h2>

      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Please enter natural language，Exaple：Find steel plants built after 1990 in Germany"
          style={{ flex: 1, padding: '10px', fontSize: '16px' }}
          onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
        />
        <button onClick={handleGenerate} disabled={loading} style={{ padding: '10px 14px' }}>
          {loading ? 'Generating…' : 'Generate Cypher'}
        </button>
      </div>

      {error && (
        <div style={{ marginTop: 12, color: '#b71c1c', whiteSpace: 'pre-wrap' }}>
          ❌ {error}
        </div>
      )}
 
      {candidates.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h4 style={{ margin: '6px 0' }}>Candidate Cypher queries：</h4>
           {candidates.map((item, idx) => (
            <div key={idx} style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 'bold' }}>{item.title}</div>
              <pre style={{ background: '#f0f0f0', padding: 10, borderRadius: 6, fontFamily: 'monospace' }}>
                 {item.cypher}
              </pre>
              <button
                 onClick={() => setCypher(item.cypher)}
                 style={{ padding: '6px 10px', marginTop: 4 }}
              >
                Use this query
              </button>
            </div>
            ))}
        </div>
      )}



      {cypher && (
        <div style={{ marginTop: 16 }}>
          <h4 style={{ margin: '6px 0' }}>Generated Cypher：</h4>
          <textarea
            value={cypher}
            onChange={(e) => setCypher(e.target.value)}
            style={{ width: '100%', height: 140, padding: 10, borderRadius: 8, border: '1px solid #ccc', fontFamily: 'monospace' }}
          />
          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <button onClick={handleExecute} disabled={execLoading} style={{ padding: '8px 12px' }}>
              {execLoading ? 'Running…' : 'Execute via Backend'}
            </button>
            <button onClick={() => renderGraph(cypher)} style={{ padding: '8px 12px' }}>
              Render with NeoVis (local)
            </button>
          </div>
        </div>
      )}

      {result && (
        <div style={{ marginTop: 16 }}>
          <h4 style={{ margin: '6px 0' }}>Query Results（JSON）：</h4>
          <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 10, overflowX: 'auto' }}>
{JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      <div id="viz" style={{ height: '600px', marginTop: '30px', border: '1px solid #ccc' }}></div>
    </div>
  );
};

export default SemanticSearch;