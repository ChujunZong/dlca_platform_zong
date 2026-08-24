import numpy as np
import dlca_core
from dlca_core import run_dlca_pipeline
import os

print("dlca_core loaded from:", dlca_core.__file__)

def run_dlca_from_form(form: dict) -> dict:
    """
    form: JSON submitted by the frontend BuildingForm (the dictionary obtained via `request.get_json()` in Flask)
    Returns: A dictionary containing the DLCA results for a single building (which can be directly serialized to JSON for the frontend)
    """

    # -------- 1) 基本参数 --------
   
    buildingage = form.get("buildingage", "nb")
    DEFAULT_GEOGRAPHY = [
        "EUROPE_GROUP"
    ]

    geo_raw = form.get("geography", DEFAULT_GEOGRAPHY)

    if isinstance(geo_raw, str):
        geo = geo_raw.strip()
        geography = [geo] if geo else DEFAULT_GEOGRAPHY
    elif isinstance(geo_raw, (list, tuple)):
        cleaned = [str(x).strip() for x in geo_raw if str(x).strip()]
        geography = cleaned if cleaned else DEFAULT_GEOGRAPHY
    else:
        geography = DEFAULT_GEOGRAPHY

    # 研究周期 rsp / years
    rsp = int(form.get("rsp", 100))
    years = rsp

    # 动态因子（例如 ["B1"], ["B2", "B4"]，或者前端传 "B1,B4"）
    dyn = form.get("dynamic_factor", ["B1"])
    if isinstance(dyn, str):
        dynamic_factor = [s.strip() for s in dyn.split(",") if s.strip()]
    else:
        dynamic_factor = dyn or []

    # 动态情景
    dynamic_scenario = form.get("dynamic_scenario", "Carbon Neutral")

    # LCIA 指标
    LCIAindicator = form.get("LCIAindicator", "GWP")
    LCIAindicator_dynamic = form.get("LCIAindicator_dynamic", "AGWP")

    # cumulative / non-cumulative
    cumulative_flag = form.get("cumulative", "cumulative")
    cumulative_bool = cumulative_flag == "cumulative"  # 目前没用到，可以先留着

    # C 阶段、B6 阶段开关
    phase_A4 = bool(form.get("phase_A4", True))
    phase_C = bool(form.get("phase_C", True))
    phase_B6 = bool(form.get("phase_B6", True))

    # 是否做静态比较
    static_comparison = bool(form.get("static_comparison", False))

    # 计算层级：我们这里默认用 Building
    level = form.get("level", "Building")

    # -------- 2) Building 构件信息 --------
    building_type = form.get("building_type", "Masonry_3")
    building_id = form.get("building_id", "frontend_building_1")

    
    components = form.get("components", [])

    
    if not components:
        components = [
            {"type": "BP", "area": 100.0},
            {"type": "EW", "area": 200.0},
        ]

    # 构件名称列表
    all_components = [c["type"] for c in components]

    
    all_components_area = [float(c.get("area", 0.0)) for c in components]

    
    total_floor_area = float(
        form.get("total_floor_area", sum(all_components_area))
    )

    # -------- 3) B6 能耗 --------
    
    energy_usage_power = float(form.get("energy_usage_power", 0.0))
    energy_usage_heat = float(form.get("energy_usage_heat", 35.13))

    consumption_power = np.full(
        years, energy_usage_power * total_floor_area, dtype=float
    )
    consumption_heat = np.full(
        years, energy_usage_heat * total_floor_area, dtype=float
    )

    # -------- 4) B6 能源系统类型 --------
    power_type = form.get("type_power", "electricity, low voltage")
    heat_type = form.get(
        "type_heat",
        "heat production, wood pellet, at furnace 300kW",
    )

    # -------- 5) 把“情景设置”写回 dlca_core 模块的全局变量 --------

    dlca_core.buildingage = buildingage
    dlca_core.rsp = rsp
    dlca_core.geography = tuple(geography)
    dlca_core.dynamic_factor = dynamic_factor
    dlca_core.dynamic_scenario = dynamic_scenario

    dlca_core.LCIAindicator = LCIAindicator
    dlca_core.LCIAindicator_dynamic = LCIAindicator_dynamic

    
    dlca_core.cumulative = cumulative_flag

    dlca_core.years = years
    dlca_core.phase_A4 = phase_A4
    dlca_core.phase_C = phase_C
    dlca_core.phase_B6 = phase_B6
    dlca_core.static_comparison = static_comparison
    dlca_core.level = level
    dlca_core.show_plots = False
    dlca_core.building_list_api = True

    # -------- 6) 组装 building_list --------
    building_list = [
        {
            "building_id": building_id,
            "building_type": building_type,
            "building_components": all_components,
            "building_components_area": all_components_area,  
            "consumption_power": consumption_power,
            "consumption_heat": consumption_heat,
            "power_system": power_type,
            "heating_system": heat_type,
            "total_floor_area": total_floor_area,
        }
    ]

    # -------- 7) 调用核心计算函数 --------
    result_building_list = run_dlca_pipeline(
        building_list=building_list,
        buildingage_param=buildingage,
        geography_param=geography,
        dynamic_factor_param=dynamic_factor,
        phase_A4_param=phase_A4,
        phase_C_param=phase_C,
        phase_B6_param=phase_B6,
        static_comparison_param=static_comparison,
        cumulative_param=cumulative_flag,  
        years_param=years,
        LCIAindicator_param=LCIAindicator,
        LCIAindicator_dynamic_param=LCIAindicator_dynamic,
        dynamic_scenario_param=dynamic_scenario,
    )

   
    if result_building_list:
        return result_building_list[0]

    return {"error": "No building results."}