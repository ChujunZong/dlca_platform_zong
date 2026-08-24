
from flask import Blueprint, request, jsonify
import os, json, re, urllib.request, urllib.error

bp = Blueprint("llm", __name__)

# Ollama LLM
OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b").strip()


CYPHER_BLOCK = re.compile(r"```(?:cypher)?\s*(.*?)\s*```", re.I | re.S)

def ollama_chat(system_text: str, user_text: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_text},
            {"role": "user",   "content": user_text},
        ],
        "stream": False,
    }
    req = urllib.request.Request(
        url=f"{OLLAMA_HOST}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return (data.get("message") or {}).get("content", "").strip()

@bp.post("/semantic-search")
def semantic_search():
    """
    Input:
      {"query": "natural language query", "topK": 20, "num": 1}

    Output:
      - when num == 1:
        {"cypher": "...", "raw": "model raw output"}
      - when num > 1:
        {"candidates": [{"title": "Candidate 1", "cypher": "..."}...],
         "raw": "model raw output",
         "cypher": "... (the first candidate)"}

    Note:
      num controls the number of candidate Cypher queries
      (default: 1, maximum: 5).
    """
    data = request.get_json(force=True) or {}
    q = (data.get("query") or "").strip()
    topk = int(data.get("topK") or 20)
    
    try:
        num = int(data.get("num") or 1)
    except Exception:
        num = 1
    num = max(1, min(num, 5))
    if not q:
        return jsonify({"error": "query is empty"}), 400

    system_template = (
        f"You are a Neo4j Cypher expert for a Life Cycle Assessment (LCA) graph.\n"
        f"Output EXACTLY {num} fenced code blocks. Each block must be a complete, runnable Cypher query.\n"
        f"Requirements per block: (1) starts with MATCH, (2) contains RETURN, (3) includes LIMIT {topk}, "
        "and (4) no prose or explanations outside the code blocks.\n\n"
        "SCHEMA NODES:\n"
        "  (:Building), (:Building_component), (:Initial_material_LCIA), (:Initial_rawmaterial_LCIA),\n"
        "  (:Initial_transportgroup_LCIA), (:Initial_transport_LCIA), (:Initial_powermix_LCIA),\n"
        "  (:Initial_heat_LCIA), (:Initial_waste_LCIA), (:Waste_treatment_ratio), (:Initial_wastetreatment_LCIA),\n"
        "  (:Dynamic_factor_b7_elementamount), (:Initial_energysource_LCIA), (:Initial_powermixgroup_LCIA), (:Initial_heatgroup_LCIA)\n\n"
        "EXAMPLES OF VALID QUERY PATHS:\n"
        "```cypher\n"
        "MATCH (b:Building)-[o]-(bc:Building_component)-[d]-(i:Initial_material_LCIA)-[q]-(ir:Initial_rawmaterial_LCIA) RETURN b,o,bc,d,i,q,ir LIMIT {topk}\n"
        "```\n"
        "```cypher\n"
        "MATCH (iw:Initial_waste_LCIA) OPTIONAL MATCH (iw)-[o]-(iwt:Initial_wastetreatment_LCIA)-[p]-(e:Initial_powermix_LCIA) RETURN iw,o,iwt,p,e LIMIT {topk}\n"
        "```\n"
        "```cypher\n"
        "MATCH (i:Initial_material_LCIA) OPTIONAL MATCH (i)-[o]-(ir:Initial_rawmaterial_LCIA)-[p]-(h:Initial_heat_LCIA) RETURN i,o,ir,p,h LIMIT {topk}\n"
        "```\n"
        "```cypher\n"
        "MATCH (wtr:Waste_treatment_ratio)-[m]-(q) OPTIONAL MATCH (q)-[s]-(df_b7_element:Dynamic_factor_b7_elementamount) RETURN wtr,q,df_b7_element LIMIT {topk}\n"
        "```\n"
        "```cypher\n"
        "MATCH (e:Initial_powermix_LCIA)-[t]-(o) OPTIONAL MATCH (o)-[x]-(df_b7_element:Dynamic_factor_b7_elementamount) OPTIONAL MATCH (o)-[y]-(i:Initial_material_LCIA) OPTIONAL MATCH (o)-[z]-(iw:Initial_waste_LCIA) OPTIONAL MATCH (o)-[xx]-(ir:Initial_rawmaterial_LCIA)-[xxx]-(i2:Initial_material_LCIA) RETURN e, t, o, x,df_b7_element,y,i,z,iw,xx,ir,xxx,i2 LIMIT {topk}\n"
        "```"
    ).replace("{topk}", str(topk))
    
    user = f"User intent: {q}\nGenerate the Cypher now."

    try:
        text = ollama_chat(system_template, user) or ""
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        mock = f"MATCH (n) RETURN n LIMIT {topk}"
        return jsonify({"cypher": mock, "raw": f"[MOCK] ollama error: {e}"}), 200
    except Exception as e:
        mock = f"MATCH (n) RETURN n LIMIT {topk}"
        return jsonify({"cypher": mock, "raw": f"[MOCK] unexpected: {e}"}), 200

    
    blocks = [m.group(1).strip() for m in CYPHER_BLOCK.finditer(text)]
    if not blocks:
        blocks = [text.strip()]  
    
    normalized = []
    for c in blocks:
        cc = c.strip()
        if " limit " not in cc.lower():
            cc = cc.rstrip(";") + f" LIMIT {topk}"
        normalized.append(cc)

    if num == 1:
        cypher = normalized[0]
        return jsonify({"cypher": cypher, "raw": text})

    take = normalized[:num]
    candidates = [{"title": f"Candidate {i+1}", "cypher": c} for i, c in enumerate(take)]
    return jsonify({"candidates": candidates, "raw": text, "cypher": take[0]})