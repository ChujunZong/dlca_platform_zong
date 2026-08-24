# dlca_service.py
from flask import Blueprint, request, jsonify, send_from_directory, abort
from dlca_wrapper import run_dlca_from_form
import pandas as pd
import numpy as np
import traceback
import os
import glob
import base64
import time
from pathlib import Path
import re
import dlca_core

bp = Blueprint("dlca", __name__)

def to_json_safe(obj):
    if isinstance(obj, pd.Series): return obj.to_dict()
    if isinstance(obj, pd.DataFrame): return obj.to_dict(orient="records")
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, np.generic): return obj.item()
    if isinstance(obj, dict): return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list): return [to_json_safe(v) for v in obj]
    return obj


def extract_chart_data(building_id, building_type, indicator="AGWP"):
    if hasattr(dlca_core, 'PLOTS_DIR'):
        plots_dir = Path(dlca_core.PLOTS_DIR)
    else:
        plots_dir = Path(dlca_core.__file__).parent / "results" / "plots"
        
    target_dir = plots_dir / "with_waste"
    
    topics = {}
    def get_topic(name):
        if name not in topics:
            topics[name] = {"name": name, "total_line": [], "sub_lines": {}, "pdf": None}
        return topics[name]

    total_val = 0.0
    prefix = f"{indicator}_{building_id}_{building_type}_"

    if target_dir.exists():
        parquet_files = glob.glob(str(target_dir / f"*{building_id}*.parquet"))
        pdf_files = glob.glob(str(target_dir / f"*{building_id}*.pdf"))
        
        
        for pf in parquet_files:
            filename = os.path.basename(pf)
            try:
                
                if building_id not in filename: continue
                
                df = pd.read_parquet(pf)
                vals = [float(v) for v in df['value'].fillna(0).iloc[::10].tolist()]
                
                if filename.startswith(prefix):
                    remainder = filename[len(prefix):]
                else:
                    remainder = filename.split(building_id)[-1].lstrip("_")
                    
                name_part = remainder.split("_cumulative")[0]
                
                name_part = name_part.replace("Carbon Neutral_", "").replace("Business As Usual_", "").replace(f"{building_type}_", "", 1)
                
                phase_label = " (Waste Phase)" if "_waste.parquet" in filename.lower() else ""
                
                if "including waste" in name_part or name_part == "including waste":
                    if name_part == f"{building_type} including waste" or name_part == "including waste":
                        get_topic("1. Total Lifecycle (incl. Waste)")["total_line"] = vals
                        total_val = vals[-1] if vals else 0.0
                    else:
                        sub = name_part.replace(f"{building_type} including waste_", "").replace("including waste_", "")
                        get_topic("1. Total Lifecycle (incl. Waste)")["sub_lines"][sub + phase_label] = vals
                        
                elif name_part == f"{building_type} total" or name_part == "total":
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
                pass

       
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            try:
                if building_id not in filename: continue
                
                if filename.startswith(prefix):
                    remainder = filename[len(prefix):]
                else:
                    remainder = filename.split(building_id)[-1].lstrip("_")
                    
                name_part = remainder.split("_cumulative")[0]
                name_part = name_part.replace("Carbon Neutral_", "").replace("Business As Usual_", "").replace(f"{building_type}_", "", 1)
                
                with open(pdf_path, "rb") as f:
                    b64 = f"data:application/pdf;base64,{base64.b64encode(f.read()).decode()}"
                    
                if "subparts" in name_part:
                    base_name = name_part.replace("_subparts", "")
                    if base_name == f"{building_type} including waste" or base_name == "including waste":
                        get_topic("1. Total Lifecycle (incl. Waste)")["pdf"] = b64
                    elif base_name == building_type or base_name == "":
                        get_topic("2. Building Components Summary")["pdf"] = b64
                    else:
                        get_topic(f"3. Breakdown: {base_name}")["pdf"] = b64
                else:
                    if name_part == f"{building_type} including waste" or name_part == "including waste":
                        if not get_topic("1. Total Lifecycle (incl. Waste)")["pdf"]: get_topic("1. Total Lifecycle (incl. Waste)")["pdf"] = b64
                    elif name_part == f"{building_type} total" or name_part == "total":
                        if not get_topic("2. Building Components Summary")["pdf"]: get_topic("2. Building Components Summary")["pdf"] = b64
                    elif name_part.endswith(" total"):
                        comp = name_part.replace(" total", "")
                        if not get_topic(f"3. Breakdown: {comp}")["pdf"]: get_topic(f"3. Breakdown: {comp}")["pdf"] = b64
            except Exception as e:
                pass

    output_groups = [topics[k] for k in sorted(topics.keys()) if topics[k]["total_line"] or topics[k]["sub_lines"] or topics[k]["pdf"]]

    
    if not output_groups:
        all_found = glob.glob(str(target_dir / f"*{building_id}*.*")) if target_dir.exists() else []
        debug_files = [os.path.basename(f) for f in all_found][:5]
        output_groups = [{
            "name": "AI DEBUG MODE: Filename Mismatch",
            "total_line": [0, 10, 20, 30],
            "sub_lines": {
                f"Expected Prefix: {prefix}": [0, 5, 10],
                f"Found Files: {', '.join(debug_files) if debug_files else 'NONE'}": [0, 2, 4]
            },
            "pdf": None
        }]

    return {
        "total_impact": float(total_val),
        "groups": output_groups
    }

# =========================================================================
# Routing Processing Interface       
# =========================================================================
@bp.post("/run_from_form")
def dlca_run_from_form():
    payload = request.get_json(force=True) or {}
    try:
        raw_result = run_dlca_from_form(payload)
        time.sleep(4.0)

        building_id = payload.get("building_id", "frontend_building_1")
        building_type = payload.get("building_type", "Masonry_3")
        indicator_dynamic = payload.get("LCIAindicator_dynamic", "AGWP")

        chart_data = extract_chart_data(building_id, building_type, indicator_dynamic)

        return jsonify({
            "ok": True, 
            "result": chart_data 
        })
       
    except Exception as e:
        print("DLCA error in /run_from_form:", e)
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 400


@bp.get("/pdf/<path:subdir>/<path:filename>")
def dlca_get_pdf(subdir, filename):
    plots_dir = Path(dlca_core.PLOTS_DIR)  
    target_dir = plots_dir / subdir        
    if not target_dir.exists():
        abort(404)
    return send_from_directory(target_dir, filename, mimetype="application/pdf")

@bp.get("/pdfs")
def dlca_list_pdfs():
    return jsonify({"ok": True, "items": list_all_pdfs()})


COMPONENT_KEYS = {"bp","fl","cfl","cw","ew","iw","fro","pro","scw","tfl","win","energy"}

def _parse_pdf_name(stem: str):
    s = re.sub(r"\s+", "_", stem)
    s = re.sub(r"_+", "_", s).strip("_")
    parts = s.split("_")
    indicator = parts[0] if parts else ""
    cumulative = "cumulative" if "cumulative" in parts else ("non-cumulative" if "non-cumulative" in parts else "")
    scope = "subparts" if "subparts" in parts else "total"
    building_id = ""
    if "building" in parts:
        i = parts.index("building")
        if i + 1 < len(parts) and parts[i+1].isdigit():
            building_id = parts[i+1]
    component = ""
    for p in parts:
        if p.lower() in COMPONENT_KEYS:
            component = p.upper()
            break
    building_type = ""
    for i in range(len(parts) - 1):
        if parts[i].isalpha() and parts[i+1].isdigit():
            building_type = f"{parts[i]}_{parts[i+1]}"
            break
    material = ""
    if parts and parts[-1].lower() == "waste":
        material = "waste"
    return {
        "indicator": indicator, "building_id": building_id, "building_type": building_type,
        "component": component, "material": material, "cumulative": cumulative, "scope": scope,
    }

def list_all_pdfs():
    plots_dir = Path(dlca_core.PLOTS_DIR)
    if not plots_dir.exists(): return []
    items = []
    for pdf_path in plots_dir.rglob("*.pdf"):
        try: rel = pdf_path.relative_to(plots_dir).as_posix()
        except Exception: rel = pdf_path.name
        meta = _parse_pdf_name(pdf_path.stem)
        parts = rel.split("/")
        if len(parts) >= 2:
            subdir, filename = parts[0], parts[-1]
        else:
            subdir, filename = "", pdf_path.name
        items.append({
            "name": pdf_path.name, "rel": rel, "subdir": subdir,
            "url": f"/api/dlca/pdf/{subdir}/{filename}", "mtime": pdf_path.stat().st_mtime, **meta,
        })
    items.sort(key=lambda x: x.get("mtime", 0), reverse=True)
    return items