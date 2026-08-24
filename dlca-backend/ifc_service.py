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

@bp.post("/calculate_carbon")
def calculate_carbon():
    if dlca_core is None: return jsonify({"error": "dlca_core not found"}), 500
    
    try:
        building_id = "IFC_" + str(uuid.uuid4())[:6]
        
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
            
        comp_names = [c for c, a in aggregated_components.items() if a > 0]
        comp_areas = [a for a in aggregated_components.values() if a > 0]

        building_input = [{
            "building_id": building_id,
            "building_type": "Masonry_improve combined",
            "building_components": comp_names,         
            "building_components_area": comp_areas,    
            "consumption_power": np.zeros(100),
            "consumption_heat": np.full(100, 35.13 * total_floor_area),
            "power_system": "electricity, low voltage",
            "heating_system": "heat production, wood pellet, at furnace 300kW",
            "total_floor_area": total_floor_area
        }]

        
        dlca_core.run_dlca_pipeline(
            building_list=building_input, buildingage_param="nb", geography_param=("CH", "RER", "Europe without Austria", "IAI Area", "GLO", "RoW"), 
            dynamic_factor_param=["B1", "B2"], phase_A4_param=True, phase_B6_param=True, phase_C_param=True, 
            static_comparison_param=False, cumulative_param="cumulative", years_param=100,
            LCIAindicator_param="GWP", LCIAindicator_dynamic_param="AGWP", dynamic_scenario_param="Carbon Neutral"
        )
        
        time.sleep(2.5) 
        
        
        target_dir = PLOTS_OUTPUT_DIR / "with_waste"
        building_type = "Masonry_improve combined"
        prefix = f"AGWP_{building_id}_{building_type}_"
        
        topics = {}
        def get_topic(name):
            if name not in topics:
                topics[name] = {"name": name, "total_line": [], "sub_lines": {}, "pdf": None}
            return topics[name]

        total_val = 0.0

        if target_dir.exists():
            parquet_files = glob.glob(str(target_dir / f"*{building_id}*.parquet"))
            pdf_files = glob.glob(str(target_dir / f"*{building_id}*.pdf"))
            
            
            for pf in parquet_files:
                filename = os.path.basename(pf)
                try:
                    if not filename.startswith(prefix): continue
                    
                    df = pd.read_parquet(pf)
                    vals = [float(v) for v in df['value'].fillna(0).iloc[::10].tolist()]
                    
                    remainder = filename[len(prefix):]
                    name_part = remainder.split("_cumulative")[0]
                    phase_label = " (Waste Phase)" if "_waste.parquet" in filename.lower() else ""
                    
                    
                    if "including waste" in name_part:
                        if name_part == f"{building_type} including waste":
                            get_topic("1. Total Lifecycle (incl. Waste)")["total_line"] = vals
                            total_val = vals[-1] if vals else 0.0
                        else:
                            sub = name_part.replace(f"{building_type} including waste_", "")
                            get_topic("1. Total Lifecycle (incl. Waste)")["sub_lines"][sub + phase_label] = vals
                            
                    elif name_part == f"{building_type} total":
                        get_topic("2. Building Components Summary")["total_line"] = vals
                    elif name_part.startswith(f"{building_type}_"):
                        sub = name_part.replace(f"{building_type}_", "")
                        get_topic("2. Building Components Summary")["sub_lines"][sub + phase_label] = vals
                        
                    elif name_part.endswith(" total"):
                        comp = name_part.replace(" total", "")
                        get_topic(f"3. Breakdown: {comp}")["total_line"] = vals
                    else:
                        if "_" in name_part:
                            comp = name_part.split("_")[0]
                            sub = name_part[len(comp)+1:]
                            get_topic(f"3. Breakdown: {comp}")["sub_lines"][sub + phase_label] = vals
                        else:
                            get_topic(f"4. Other: {name_part}")["total_line"] = vals
                except Exception as e:
                    print(f"Error parsing parquet {filename}: {e}")

            
            for pdf_path in pdf_files:
                filename = os.path.basename(pdf_path)
                try:
                    if not filename.startswith(prefix): continue
                    remainder = filename[len(prefix):]
                    name_part = remainder.split("_cumulative")[0]
                    
                    with open(pdf_path, "rb") as f:
                        b64 = f"data:application/pdf;base64,{base64.b64encode(f.read()).decode()}"
                        
                    
                    if "subparts" in name_part:
                        base_name = name_part.replace("_subparts", "")
                        if base_name == f"{building_type} including waste":
                            get_topic("1. Total Lifecycle (incl. Waste)")["pdf"] = b64
                        elif base_name == building_type:
                            get_topic("2. Building Components Summary")["pdf"] = b64
                        else:
                            get_topic(f"3. Breakdown: {base_name}")["pdf"] = b64
                    else:
                        if name_part == f"{building_type} including waste":
                            if not get_topic("1. Total Lifecycle (incl. Waste)")["pdf"]: get_topic("1. Total Lifecycle (incl. Waste)")["pdf"] = b64
                        elif name_part == f"{building_type} total":
                            if not get_topic("2. Building Components Summary")["pdf"]: get_topic("2. Building Components Summary")["pdf"] = b64
                        elif name_part.endswith(" total"):
                            comp = name_part.replace(" total", "")
                            if not get_topic(f"3. Breakdown: {comp}")["pdf"]: get_topic(f"3. Breakdown: {comp}")["pdf"] = b64
                except Exception as e:
                    print(f"Error parsing PDF {filename}: {e}")

        
        output_groups = [topics[k] for k in sorted(topics.keys()) if topics[k]["total_line"] or topics[k]["sub_lines"] or topics[k]["pdf"]]

        return jsonify({
            "status": "success",
            "total_impact": float(total_val),
            "groups": output_groups
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500