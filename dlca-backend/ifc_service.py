# dlca-backend/ifc_service.py
import os, uuid, json, base64, glob, time, requests, re
from pathlib import Path
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from dlca_core import run_dlca_pipeline

try:
    import ifcopenshell
    import ifcopenshell.util.element
    from ifcopenshell.util.element import get_psets, get_material
except ImportError:
    ifcopenshell = None

try:
    import dlca_core
    if hasattr(dlca_core, 'PLOTS_DIR'):
        PLOTS_OUTPUT_DIR = dlca_core.PLOTS_DIR
    else:
        PLOTS_OUTPUT_DIR = Path(dlca_core.__file__).parent / "results" / "plots"
except ImportError:
    dlca_core = None
    PLOTS_OUTPUT_DIR = Path("./results/plots")

bp = Blueprint("ifc", __name__)
UPLOAD_DIR = Path(os.getenv("IFC_UPLOAD_DIR", "./uploads")).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

import os, requests, re


VALID_CODES = [
    "EWmas_1", "FROmas_1", "IWmas_1", "CW_h_1", "FLmas_1", "BP_h_1", 
    "WINwoodalu_1", "WINalu_1", "PRO_h_1", "FROwood_1", "EWwood_1", "IWwood_1", 
    "FLwood_1", "WINwood_1", "EWmas_improve1", "IWmas_improve1", "FROmas_improve1", 
    "FLmas_improve1", "FROmas_improve2", "FLmas_improve2", "FROmas_improve3", "FLmas_improve3"
]

def query_llm_classification(raw_name):
    prompt = f"""
You are an expert BIM and LCA data mapping assistant.
Your ONLY task is to map a given IFC material name (often in German) to ONE EXACT component ID from the provided list.

=== COMPONENT IDs & MATCHING RULES ===
[Exterior Walls]
- EWmas_1 : clay brick, cement mortar, glass wool. (Keywords: Außenwand Mauerwerk, AW massiv, Ziegelwand, MW+WDVS, Backsteinwand, LHR MW, LHR Dämmung massiv)
- EWwood_1 : timber, cellulose. (Keywords: Außenwand Holz, AW Holzständer, Holzrahmenbau AW, LHR Holzständerwerk)
- CW_h_1 : XPS, bitumen, basement. (Keywords: Kelleraußenwand, Perimeterdämmung, Wand gegen Erdreich, XPS Dämmung Keller, LHR Dämmung Perimeter)

[Interior Walls]
- IWmas_1 : clay brick, plaster. (Keywords: Innenwand Mauerwerk, IW massiv, Trennwand Ziegel, MW innen)
- IWwood_1 : timber, gypsum. (Keywords: Innenwand Holz, Trockenbauwand, Leichtbauwand, Gipskartonwand, IW Holzständer)

[Floors]
- FLmas_1 : concrete, EPS. (Keywords: Geschossdecke Beton, Stahlbetondecke, StB Decke, Fußbodenaufbau massiv, FL massiv)
- FLwood_1 : timber deck. (Keywords: Holzbalkendecke, Decke Holz, Geschossdecke Holz)

[Roofs]
- FROmas_1 : concrete flat roof. (Keywords: Flachdach Beton, Betondach, Foliendach auf Beton)
- FROwood_1 : timber flat roof. (Keywords: Flachdach Holz, Holzbalkendecke Dach)
- PRO_h_1 : pitched roof. (Keywords: Steildach, Dachstuhl, Holzdach, Sparrendach)

[Foundations]
- BP_h_1 : concrete base plate. (Keywords: Bodenplatte, Fundamentplatte, Sohlplatte, Kellerboden, Fundament)

[Windows]
- WINwoodalu_1 : wood-metal frame. (Keywords: Fenster Holz-Alu)
- WINwood_1 : wood frame. (Keywords: Holzfenster)
- WINalu_1 : aluminum frame. (Keywords: Alufenster)

=== EXAMPLES ===
Input: "LHR Dämmung, Perimeter" -> Output: CW_h_1
Input: "Stahlbetondecke 20cm" -> Output: FLmas_1
Input: "Holzständerwerk AW" -> Output: EWwood_1
Input: "Trockenbauwand" -> Output: IWwood_1
Input: "MW nicht tragend" -> Output: IWmas_1

=== YOUR TASK ===
Input: "{raw_name}"
Output ONLY the Component ID. No explanations. No markdown formatting.
"""
    target_model = os.getenv("OLLAMA_MODEL", "mistral")
    try:
        response = requests.post(
            'http://localhost:11434/api/generate', 
            json={"model": target_model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}},
            timeout=45 
        )
        if response.status_code == 200:
            raw_result = response.json().get('response', '').strip()
           
            for code in VALID_CODES:
                if re.search(rf'\b{code}\b', raw_result, re.IGNORECASE): 
                    return code
            
            upper_raw = raw_name.upper()
            for code in VALID_CODES:
                if upper_raw.startswith(code.upper()): 
                    return code
        return None
    except: 
        return None

def fallback_classification(material_name):
    """
    A fallback rule triggered when an LLM match fails.
    All return values must be strictly present in the VALID_CODES list.
    """
    mat = material_name.lower()
    
    if "fundament" in mat or "sohl" in mat or mat.startswith("bp"): 
        return "BP_h_1"
        
    
    if "dach" in mat or mat.startswith("fro") or mat.startswith("pro"): 
        return "FROmas_1"
        
    
    if "win" in mat or "fenster" in mat or "glas" in mat or mat.startswith("win"): 
        return "WINalu_1"
        
    
    if "innen" in mat or "interior" in mat or "nicht tragend" in mat: 
        return "IWmas_1"
        
    
    if "floor" in mat or "decke" in mat or "slab" in mat or "stb" in mat or "beton" in mat: 
        return "FLmas_1"
        
    
    return "EWmas_1"

def get_element_area(element):
    try:
        psets = ifcopenshell.util.element.get_psets(element)
        qto = {}
        for k, v in psets.items():
            if any(q_key in k for q_key in ["Qto_", "BaseQuantities"]): qto.update(v or {})
        for key in ["NetSideArea", "GrossSideArea", "NetArea", "GrossArea", "Area", "SurfaceArea"]:
            val = qto.get(key)
            if val is not None:
                actual_val = val.get("value") if isinstance(val, dict) else val
                try:
                    if float(actual_val) > 0: return float(actual_val)
                except: continue
        return 0.0
    except: return 0.0

@bp.post("/upload")
def upload_ifc():
    if ifcopenshell is None: return jsonify({"error": "ifcopenshell missing"}), 500
    if "file" not in request.files: return jsonify({"error": "no file"}), 400
    f = request.files["file"]
    file_id = str(uuid.uuid4())
    path = UPLOAD_DIR / f"{file_id}_{secure_filename(f.filename)}"
    f.save(str(path))
    try:
        model = ifcopenshell.open(str(path))
        parsed_elements = []
        for e in model.by_type("IfcElement"):
            if e.is_a("IfcOpeningElement"): continue
            area_val = get_element_area(e)
            mat_info = get_material(e)
            mat_name = mat_info["material"].get("Name") if isinstance(mat_info, dict) and mat_info.get("material") else getattr(mat_info, "Name", "Unassigned")
            parsed_elements.append({"type": e.is_a(), "material": mat_name, "quantity": area_val if area_val > 0 else 0.1})

        df = pd.DataFrame(parsed_elements)
        type_counts = df["type"].value_counts().to_dict() if not df.empty else {}
        material_list = [{"material_name": r["material"], "quantity": float(r["quantity"]),"unit": "m²"} for _, r in df.groupby("material")["quantity"].sum().reset_index().iterrows()] if not df.empty else []
        return jsonify({"meta": {"project": "IFC Project"}, "counts": {"elements_total": len(parsed_elements), "by_type": type_counts}, "materials": material_list}), 200
    except Exception as e: return jsonify({"error": str(e)}), 400

@bp.post("/suggest_mapping")
def suggest_mapping():
    material_name = request.json.get("material_name", "")
    
    
    llm_result = query_llm_classification(material_name)
    
    
    if llm_result:
        suggested_id = llm_result
        match_type = " [AI Matching]"
    else:
        suggested_id = fallback_classification(material_name)
        match_type = " [Front-end Fallback Rules]"

    
    print("\n" + "="*50)
    print(f"[{match_type}] Analyzing Materials: '{material_name}'")
    print(f"-> Final ID: '{suggested_id}'")
    print("="*50 + "\n")

    return jsonify({"material_name": material_name, "epd_id": suggested_id}), 200

_CODE_TO_BUILDING = None
def _code_to_building():
    """Map each component code to a building type that actually contains it (queried from the DB once)."""
    global _CODE_TO_BUILDING
    if _CODE_TO_BUILDING is None:
        mapping = {}
        try:
            from neo4j_service import driver as _drv
            with _drv.session() as s:
                for rec in s.run("MATCH (b:Building)--(bc:Building_component) RETURN bc.Name AS c, collect(b.Name) AS bs"):
                    mapping[rec["c"]] = sorted(rec["bs"])[0]
        except Exception as e:
            print("[ifc] building-map query failed, using fallback:", e)
            mapping = {"PRO_h_1": "Masonry_2", "WINwood_1": "Timber_3"}
        _CODE_TO_BUILDING = mapping
    return _CODE_TO_BUILDING


@bp.post("/calculate_carbon")
def calculate_carbon():
    if dlca_core is None: return jsonify({"error": "dlca_core not found"}), 500

    try:
        base_id = "IFC_" + str(uuid.uuid4())[:6]
        code_map = _code_to_building()

        aggregated_components = {code: 0.0 for code in VALID_CODES}
        total_floor_area = 0.0

        for item in request.json:
            raw_id = item.get("epd_id", "EWmas_1")
            std_code = next(
               (c for c in VALID_CODES if raw_id.upper().startswith(c.upper())),
                "EWmas_1"
            )
            area = float(item.get('quantity', 0))
            aggregated_components[std_code] += area
            total_floor_area += area

        active = [(c, a) for c, a in aggregated_components.items() if a > 0]
        skipped = [c for c, a in active if c not in code_map]
        active = [(c, a) for c, a in active if c in code_map]

        # Per-component calculation: each component runs with the building type
        # that actually contains it in the database. Component material data is
        # independent of the building type, so results are exact per component.
        # Operational energy (B6) is excluded: an IFC material take-off defines
        # embodied + replacement + end-of-life scope, not operation.
        run_ids = []
        for code, area in active:
            bid = f"{base_id}-{code}"
            building_input = [{
                "building_id": bid,
                "building_type": code_map[code],
                "building_components": [code],
                "building_components_area": [area],
                "consumption_power": np.zeros(100),
                "consumption_heat": np.zeros(100),
                "power_system": "electricity, low voltage",
                "heating_system": "heat production, wood pellet, at furnace 300kW",
                "total_floor_area": total_floor_area
            }]
            print(f"[ifc] computing {code} ({area:.1f} m2) as {code_map[code]}")
            dlca_core.run_dlca_pipeline(
                building_list=building_input, buildingage_param="nb",
                geography_param=("EUROPE_GROUP",),
                dynamic_factor_param=["B1", "B2"], phase_A4_param=True,
                phase_B6_param=False, phase_C_param=True,
                static_comparison_param=False, cumulative_param="cumulative", years_param=100,
                LCIAindicator_param="GWP", LCIAindicator_dynamic_param="AGWP",
                dynamic_scenario_param="Carbon Neutral"
            )
            run_ids.append((code, bid))

        # Collect results per component
        target_dir = PLOTS_OUTPUT_DIR / "with_waste"
        comp_groups = []
        for code, bid in run_ids:
            g = {"name": f"3. Breakdown: {code}", "total_line": [], "sub_lines": {}, "pdf": None}
            for pf in sorted(glob.glob(str(target_dir / f"*{bid}_*.parquet"))):
                fn = os.path.basename(pf)
                if "_subparts" in fn: continue
                try:
                    df = pd.read_parquet(pf)
                    vals = [float(v) for v in df['value'].fillna(0).iloc[::10].tolist()]
                except Exception as e:
                    print(f"[ifc] parquet read failed {fn}: {e}"); continue
                if " including waste_Waste_cumulative" in fn:
                    g["sub_lines"]["waste phase (end-of-life)"] = vals
                elif " including waste_Without Waste_cumulative" in fn:
                    g["sub_lines"]["production + replacement phase"] = vals
                elif " including waste_cumulative" in fn and f"{code} including waste" not in fn:
                    g["total_line"] = vals                      # building-level total incl. waste
                elif f"{code} including waste" in fn or " total_cumulative" in fn:
                    continue                                    # redundant duplicates in a 1-component run
                else:
                    # material-level file: split at the LAST occurrence of the component code,
                    # because the run id itself also contains the code
                    tail = fn.rsplit(f"_{code}_", 1)
                    if len(tail) < 2 or tail[1].startswith("cumulative"):
                        continue                                # component-level duplicate curve
                    label = tail[1].split("_cumulative")[0]
                    if fn.lower().endswith("_waste.parquet"): label += " (waste)"
                    g["sub_lines"][label] = vals
            pdfs = sorted(glob.glob(str(target_dir / f"*{bid}_*subparts*.pdf")))
            if pdfs:
                with open(pdfs[0], "rb") as fh:
                    g["pdf"] = f"data:application/pdf;base64,{base64.b64encode(fh.read()).decode()}"
            comp_groups.append(g)

        # Overall group, in the same style as the manual-input dashboard:
        # summed curve as total, per-component curves as legend lines
        n_pts = max((len(g["total_line"]) for g in comp_groups), default=0)
        summed = [0.0] * n_pts
        for g in comp_groups:
            for i, v in enumerate(g["total_line"]):
                summed[i] += v
        total_val = summed[-1] if summed else 0.0
        overall = {
            "name": "1. Total Lifecycle (incl. Waste)",
            "total_line": summed,
            "sub_lines": {g["name"].replace("3. Breakdown: ", ""): g["total_line"]
                          for g in comp_groups if g["total_line"]},
            "pdf": None,
        }
        groups = [overall] + comp_groups

        return jsonify({
            "status": "success",
            "total_impact": float(total_val),
            "groups": groups,
            "note": "Per-component calculation. B6 operational energy excluded."
                    + (f" Skipped (not in database): {skipped}" if skipped else "")
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
