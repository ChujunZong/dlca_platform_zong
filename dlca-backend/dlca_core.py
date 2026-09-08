
from neo4j import GraphDatabase
import pandas as pd
import numpy as np
import ast
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import math
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp
import re
from pathlib import Path
B7_INPUT_DIR = Path(__file__).resolve().parent / "InputResearch"

# =========================
# RESULT OUTPUT DIRECTORIES
# =========================
BASE_DIR = Path(__file__).resolve().parent  
RESULTS_DIR = BASE_DIR / "results"
PLOTS_DIR = RESULTS_DIR / "plots"  # results/plots/{with_waste|without_waste}



import pickle
import pyarrow.parquet as pq
import pyarrow as pa

#important: the ecoinvent version is 3.11!

#------------------------Defining the LCIA method information
LCIAindicator="GWP"
LCIAindicator_dynamic="AGWP"
years=100
cumulative="cumulative"
static_comparison=False


#print option for np to avoid displaying np.float64()
np.set_printoptions(legacy='1.21')
plt.rcParams["font.family"] = "Arial"

from typing import Optional, Any, Dict
import pandas as pd
from pathlib import Path

PDF_CHART_DATA = {}
# =========================
# Pylance helpers (globals)
# =========================

B7_INPUT_DIR: Path = Path(__file__).resolve().parent / "InputResearch"


df_query_result: Optional[pd.DataFrame] = None
df_query_result_heat: Optional[pd.DataFrame] = None
df_query_result_powermix: Optional[pd.DataFrame] = None
df_query_result_waste: Optional[pd.DataFrame] = None


indicators: Optional[Dict[str, Any]] = None
halogen_indicators: Optional[Dict[str, Any]] = None
process_element: Optional[Any] = None

df_dynamicfactor_b7_dagwp_co2: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagwp_ch4_bio: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagwp_ch4_fossil: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagwp_n2o: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagwp_halogen: Optional[pd.DataFrame] = None

df_dynamicfactor_b7_dagtp_co2: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagtp_ch4_bio: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagtp_ch4_fossil: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagtp_n2o: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagtp_halogen: Optional[pd.DataFrame] = None

df_dynamicfactor_b7_dagwp_co2_noncumulative: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagwp_ch4_bio_noncumulative: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagwp_ch4_fossil_noncumulative: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagwp_n2o_noncumulative: Optional[pd.DataFrame] = None
df_dynamicfactor_b7_dagwp_halogen_noncumulative: Optional[pd.DataFrame] = None

# B1/B2
df_query_result_b1: Optional[list] = None  
df_query_result_b2_further: Optional[pd.DataFrame] = None
df_query_result_b2_influence = None
df_query_result_b2_base = None
# B3/B4/B5 (material + waste + ratios + energysource) 
df_query_result_b5_final_waste: Optional[list] = None
df_query_result_b4_final_waste: Optional[list] = None
df_query_result_b3_final_waste: Optional[list] = None

df_query_result_b5_dynamic_ratio: Optional[pd.DataFrame] = None
df_query_result_b4_dynamic_ratio: Optional[pd.DataFrame] = None
df_query_result_b3_dynamic_ratio: Optional[pd.DataFrame] = None

df_query_result_b5_energysource_amount: Optional[pd.DataFrame] = None
df_query_result_b4_energysource_amount: Optional[pd.DataFrame] = None
df_query_result_b3_energysource_amount: Optional[pd.DataFrame] = None

df_query_result_b5_final_material = None
df_query_result_b4_final_material = None
df_query_result_b3_final_material = None

df_query_result_b5_final_heat = None
df_query_result_b4_final_heat = None
df_query_result_b3_final_heat = None

df_query_result_b5_final_power = None
df_query_result_b4_final_power = None
df_query_result_b3_final_power = None

medium_ratio_static: Optional[pd.DataFrame] = None
high_ratio_static: Optional[pd.DataFrame] = None

#connect to the database

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "neo4j")

#Authentication
driver = GraphDatabase.driver(URI, auth=AUTH)

# %%
"""
VARIABLE! 
"""

#------------------------Defining the foreground information
buildingage="nb"
rsp=100 #years
starting_time=2025 #the starting time of calculating LCIA
phase_C=True #if including the waste treatment
phase_B6=True #if including the operational energy consumption
phase_A4=True #if including the default transport distance in A4
geography=("CH", "RER", "Europe without Austria", "IAI Area, EU27 & EFTA")
#default_geography=True #if using default GLO or excluding all activies that are not CH or RER (this condition is valid only for the current version)
#NEED TO COMPUTE IN THE CALCULATION!
#
#

#------------------------Defining dynamic factors
dynamic_factor = ["B1"] # "-" or "Bx" (or "Fx"), "power-2024" for power mix comparison
dynamic_scenario = "Carbon Neutral" #Carbon Neutral or Business As Usual



#------------------------Defining levels
level="Building" #Building, Building_Component, Building_Material
building_list_api = False

#For the building material level, building material name and the rough component group should be defined!
material_name="fleece, polyethylene"
component_group="PRO"

#For the building component level, area needs to be defined extra
#Either the exact component name should be given or the building construction type and component group should be given
component_area=1
component_name="PRO_h_1"
#building_type="Timber_3"
#component_group="PRO"

if level=="Building" and building_list_api != True:
    #For the building level, building type and area of all components needs to be defined
    building_type="Masonry_improve combined"

    """
    all_components=["BP","FL","CFL","CW","EW","IW","FRO","PRO","SCW","TFL","WIN"] #todo: the names should be adjusted!
    all_components_area=[4699,15611,0,0,3865,0,4699,0,0,0,3104] #DEBY_LOD2_4959460
    """
    all_components=["BP","FL","EW","FRO","PRO","WIN","IW"] #todo: the names should be adjusted! TO MAKE IT EASY: CFL, SCW and TFL are taken out here!
    #removed components that are not relevant here (CW)
    all_components_area=[4699,15611,3865,0,4699,3104,0] #DEBY_LOD2_4959460
    #FL: BGF-BP

    building_id="default" 

    #------------------------Defining b6
    #For phase b6, end/final energy consumption for heating and electricity is needed!
    #consumption_power = np.append(0,np.random.uniform(low=1500, high=3000, size=(years,)))
    #consumption_heat = np.append(0,np.random.uniform(low=2000, high=4000, size=(years,)))

    consumption_power = np.full(rsp, 0)
    consumption_heat = np.full(rsp, 35.13*1.2*17915) 
    total_floor_area = 17915
    #existing:92.54 district heating, Heated area: NGF
    #new:29.86 district heating, 35.13 pellets, Heated area: NGF

    #And it is needed to determine the voltage of the powermix and the type of the heating source
    power_type = "electricity, low voltage"
    #heat_type = "heat and power co-generation, natural gas, 1MW electrical, lean burn" #*0.7
    #heat_type = "heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014, renewable energy products" #*0.7
    #heat_type = "heat and power co-generation, biogas, gas engine, renewable energy products" #*0.7

    heat_type = "heat production, wood pellet, at furnace 300kW" #*1.2


    building_list = [{"building_id": building_id,
                     "building_type": building_type,
                     "building_components": all_components,
                     "building_components_area": all_components_area,
                     "consumption_power": consumption_power,
                     "consumption_heat": consumption_heat,
                     "power_system": power_type,
                     "heating_system": heat_type,
                     "total_floor_area": total_floor_area}]

show_plots = False

#%%
##############################################################################################################################################################
#Part 1: read the information from the database, including the dynamic factors

#Select the correct amount/value
def select_amount(df):
    # Optimized: parse each stringified dict once, collect rows in a list,
    # build the DataFrame in one shot (was: repeated literal_eval + concat per row).
    # Output verified bit-identical to the previous implementation.
    cast_cols = ["Material_Density", "Material_Thickness", "Material_Lambda", "Material_RSL"]
    rows = []
    for i in df.index:
        densities   = ast.literal_eval(df.loc[i, "Material_Density"])
        thicknesses = ast.literal_eval(df.loc[i, "Material_Thickness"])
        lambdas     = ast.literal_eval(df.loc[i, "Material_Lambda"])
        rsls        = ast.literal_eval(df.loc[i, "Material_RSL"])
        bm = df.loc[i, "Building_Material"]
        for key in densities.keys():
            if bm in key:
                rec = df.loc[i].to_dict()
                rec["Material_Density"]   = densities[key]
                rec["Material_Thickness"] = thicknesses[key]
                rec["Material_Lambda"]    = lambdas[key]
                rec["Material_RSL"]       = rsls[key]
                rec["Building_Material"]  = key
                rows.append(rec)
    df_temp = pd.DataFrame(rows, columns=list(df.columns)).reset_index(drop=True)
    for c in cast_cols:
        df_temp[c] = pd.to_numeric(df_temp[c], errors='coerce')
    return df_temp

def read_db_basic (driver,URI,AUTH):
    #Building level (for all material, building componetn and building level) -- static or with DF B7
    #Connection with material first
    records, summary, keys = driver.execute_query("""
        
        MATCH 
        (b:Building)-[m]-(bc:Building_component)-[n]-(i)-[o]-(df_b7_element: Dynamic_factor_b7_elementamount)
            
        WHERE
        bc.BuildingAge = $buildingage
        
        RETURN 
        b.Name, bc.Name, bc.Density, bc.Thickness, bc.LambdaValue, bc.RSL, i.Name, i.GWP, df_b7_element.ElementAmount, i.Unit
        """,
        
        buildingage=buildingage,
        
        database_="neo4j",
    )

   
    # Loop through results and do something with them
    #for record in records:  
    #    print(record.data())  # obtain record as dict

    # Summary information  
    
    print("The query returned {records_count} records in {time} ms.".format(
        records_count=len(records),
        time=summary.result_available_after
    ))    

    df_query_result = pd.DataFrame(records, columns = ["Building_Construction_Type",
                                                       "Building_Component",
                                                       "Material_Density",
                                                       "Material_Thickness",
                                                       "Material_Lambda",
                                                       "Material_RSL",
                                                       "Building_Material",
                                                       "Material_GWP",
                                                       "Element_Amount",
                                                       "Material_Unit"
                                                       ])

    df_query_result = select_amount(df_query_result)
    
    return df_query_result

def read_db_waste(driver,URI,AUTH):
    #Adding waste to the cycle (C phases) HERE THE WASTE TREATMENT ONLY CONSIDERED ONCE FOR THE MAUNALLY CREATED MATERIAL COMBINATION TO AVOID DOUBLE COUNTING
    driver.verify_connectivity()
    records, summary, keys = driver.execute_query("""
        
        MATCH 
        
        (df_b7_element: Dynamic_factor_b7_elementamount) OPTIONAL MATCH (df_b7_element)-[p]-(iw:Initial_waste_LCIA)-[m]-(wtr:Waste_treatment_ratio)-[o]-(i:Initial_material_LCIA)-[n]-(bc:Building_component)-[s]-(b:Building)
        
        WHERE
        bc.BuildingAge = $buildingage
        
       RETURN 
        b.Name, bc.Name, bc.Density, bc.Thickness, bc.LambdaValue, bc.RSL, i.Name, wtr.Disposal, wtr.Recycling, wtr.CircularRecycling, wtr.Reuse, iw.Name, iw.GWP, iw.Unit, df_b7_element.ElementAmount, TYPE(m)
        """,
        
        buildingage=buildingage,
        
        database_="neo4j",
    )
    
    
    # Loop through results and do something with them
    #for record in records:  
    #    print(record.data())  # obtain record as dict

    # Summary information  
    print("The query returned {records_count} records in {time} ms.".format(
        records_count=len(records),
        time=summary.result_available_after
    ))

    df_query_result_waste = pd.DataFrame(records, columns = ["Building_Construction_Type",
                                                             "Building_Component",
                                                             "Material_Density",
                                                             "Material_Thickness",
                                                             "Material_Lambda",
                                                             "Material_RSL",
                                                             "Building_Material",
                                                             "Waste_Ratio_Disposal",
                                                             "Waste_Ratio_Recycling",
                                                             "Waste_Ratio_CircularRecycling",
                                                             "Waste_Ratio_Reuse",
                                                             "Waste_Name",
                                                             "Waste_GWP",
                                                             "Material_Unit",
                                                             "Element_Amount",
                                                             "Connection_Type"
                                                             ])

    df_query_result_waste=df_query_result_waste[df_query_result_waste["Building_Material"].isnull()==False].reset_index(drop=True)

    #Select the correct amount/value
    df_query_result_waste = select_amount(df_query_result_waste)

    #delete other unnecessary waste treatment, which should only appear in furthertreatment in b2
    df_query_result_waste = df_query_result_waste.loc[(df_query_result_waste["Connection_Type"]!="DEFINES_THE_FURTHER_TREATMENT_QUANTITY_OF")].reset_index(drop=True)
    
    return df_query_result_waste

def read_db_heat_power(driver,URI,AUTH):
    #-------------------------------------------------
    #Adding operational energy (heating and electricity) (B6 phase)
    #FOR HEATING: energy source is the different heating source, the "heat" is not directly used
    
    # Query 1: Traditional heating systems (connected to Initial_heat_LCIA)
    records, summary, keys = driver.execute_query("""
        
        MATCH 
        (h:Initial_heat_LCIA) OPTIONAL MATCH (h)-[m]-(es:Initial_energysource_LCIA)-[o]-(df_b7_element: Dynamic_factor_b7_elementamount)
        
        RETURN 
        h.Name, es.Name, es.GWP, df_b7_element.ElementAmount, es.Unit, es.PowerMix
        """,
        
        database_="neo4j",
    )

    # Summary information  
    print("The query returned {records_count} records in {time} ms.".format(
        records_count=len(records),
        time=summary.result_available_after
    ))

    df_query_result_heat = pd.DataFrame(records, columns = ["Heat",
                                                            "Energysource",
                                                            "Energysource_GWP",
                                                            "Element_Amount",
                                                            "Unit",
                                                            "Power_Mix"
                                                            ])
    
    #-------------------------------------------------
    # Query 2: Heat pumps (directly from Initial_energysource_LCIA, not under Initial_heat_LCIA)
    # These are energy sources that contain "heat pump" or "heat exchanger" in their name
    records_heatpump, summary_heatpump, keys_heatpump = driver.execute_query("""
        
        MATCH 
        (es:Initial_energysource_LCIA)-[o]-(df_b7_element: Dynamic_factor_b7_elementamount)
        
        WHERE 
        es.Name CONTAINS 'heat pump' OR es.Name CONTAINS 'heat exchanger'
        
        RETURN 
        'heat, from heat pump' AS Heat, es.Name, es.GWP, df_b7_element.ElementAmount, es.Unit, es.PowerMix
        """,
        
        database_="neo4j",
    )

    df_query_result_heatpump = pd.DataFrame(records_heatpump, columns = ["Heat",
                                                                          "Energysource",
                                                                          "Energysource_GWP",
                                                                          "Element_Amount",
                                                                          "Unit",
                                                                          "Power_Mix"
                                                                          ])
    
    # Combine traditional heating and heat pumps
    df_query_result_heat = pd.concat([df_query_result_heat, df_query_result_heatpump], ignore_index=True)
    
    #-------------------------------------------------
    #Adding operational energy (heating and electricity) (B6 phase)
    #FOR POWERMIX: the powermixes are the most important here, the different energy sources in the mix is at this stage not yet important.
    records, summary, keys = driver.execute_query("""
        
        MATCH 
        (e:Initial_powermix_LCIA) OPTIONAL MATCH (e)-[o]-(df_b7_element: Dynamic_factor_b7_elementamount)
        
        RETURN 
        e.Name, e.GWP, df_b7_element.ElementAmount, e.Unit
        """,
        
        database_="neo4j",
    )

    
    df_query_result_powermix = pd.DataFrame(records, columns = ["Powermix",
                                                                "Powermix_GWP",
                                                                "Element_Amount",
                                                                "Unit"
                                                                ])
    
    return df_query_result_heat, df_query_result_powermix

#%%
#-------------------------------------------------
#Query with dynamic factors
#Select the correct amount/value, specifically for dynamic factors

def process_amounts_DF2(df, target):
    df = df.copy()  # Avoid modifying original dataframe
    
    # Process Further_Treatment amounts
    for i in df.index:
        if 'Further_Treatment' in df.columns:
            further_treatments = ast.literal_eval(df.loc[i, "Further_Treatment"])
            name = df.loc[i, "Name"]
            
            for key in further_treatments.keys():
                if name in key:
                    # Skip if name doesn't contain "recycled" but key does 
                    if "recycled" not in name and "recycled" in key: #(this is for the case of "polystyrene foam slab, polystyrene foam slab production, 100 % recycled")
                        continue
                    
                    df.loc[i, "Amount"] = further_treatments[key]
                    break
    
    # Apply target-specific calculations
    for j in df.index:
        
        if target == "further":
            circular_change = float(df.loc[j, "Circular_Recycling_Change"])
            df.loc[j, "Amount"] = circular_change * float(df.loc[j, "Amount"])
            
        elif target == "influence":
            replacement_rate = float(df.loc[j, "Replacement_Rate"])
            df.loc[j, "Amount"] = replacement_rate * float(df.loc[j, "Amount"])
            df.loc[j, "Reduction_Reference"] = df.loc[j, "Amount"]
     
    
    # Process waste reduction reference for "further" target
    if target == "further":
        for o in df.index:
            for t in df.index:
                if (df.loc[o, "Building_Construction_Type"] == df.loc[t, "Building_Construction_Type"] and
                    df.loc[o, "Building_Component"] == df.loc[t, "Building_Component"] and
                    df.loc[o, "Building_Material"] == df.loc[t, "Building_Material"] and
                    df.loc[t, "Amount"] < 0 and "waste" in df.loc[t, "Name"]):
                    
                    df.loc[o, "Reduction_Reference_Waste"] = df.loc[t, "Amount"]
                    break
        
        df["Reduction_Reference_Waste"] = df["Reduction_Reference_Waste"].fillna(0)
    
    # Process material reduction max
    if 'Reduction_In_Material_Max' in df.columns:
        for i in df.index:
            reduction_data = df.loc[i, "Reduction_In_Material_Max"]
            if len(str(reduction_data)) > 3:
                reductions = ast.literal_eval(reduction_data)
                
                #This is the min, for finding the splitting point later (one reaches 0 then the other one is 100%)
                #This one is currently not needed, because the distribution of the recycled part is proportionally accordingly to the partial %
                if len(reductions)>1: #this min. is only needed if there are more than 1 elements
                    df.loc[i, "Reduction_In_Material_Max_Smaller"] = min(reductions.values())
                else:
                    df.loc[i, "Reduction_In_Material_Max_Smaller"] = None
                
                #This is the sum, for comparison later
                df.loc[i, "Reduction_In_Material_Max"] = sum(reductions.values())
                                
                #Specific amount for influenced materials, for further calculation
                #Should use partial % of all influenced materials
                for key in reductions.keys():
                    if df.loc[i, "Name"] in key:
                        df.loc[i, "Amount_Specific"] = df.loc[i, "Amount"] * (reductions[key]/sum(reductions.values()))
                
            # If length <= 3, keep original value (no change needed)  
    
    # Process waste reduction max
    if 'Waste_Reduction_Max' in df.columns:
        for i in df.index:
            waste_data = df.loc[i, "Waste_Reduction_Max"]
            if len(str(waste_data)) > 3:
                waste_reductions = ast.literal_eval(waste_data)
                
                #This is the min, for finding the splitting point later (one reaches 0 then the other one is 100%)
                #This one is currently not needed, because the distribution of the recycled part is proportionally accordingly to the partial %
                if len(waste_reductions)>1: #this min. is only needed if there are more than 1 elements
                    df.loc[i, "Waste_Reduction_Max_Smaller"] = min(waste_reductions.values())
                else:
                    df.loc[i, "Waste_Reduction_Max_Smaller"] = None
                
                #This is the sum, for comparison later
                df.loc[i, "Waste_Reduction_Max"] = sum(waste_reductions.values())

                
                #Specific amount for influenced waste treatments, for further calculation
                for key in waste_reductions.keys():
                    if df.loc[i, "Name"] in key:
                        df.loc[i, "Amount_Specific"] = df.loc[i, "Amount"] * (waste_reductions[key]/sum(waste_reductions.values()))
                        
            else:
                df.loc[i, "Waste_Reduction_Max"] = 1
    
    for i in df.index: #normally when only one material is there
        if pd.isna(df.loc[i, "Amount_Specific"]):
            df.loc[i, "Amount_Specific"] = df.loc[i, "Amount"]
                
    # Process additional conversion factor
    if 'Additional_Conversion_Factor' in df.columns:
        for i in df.index:
            conversion_data = df.loc[i, "Additional_Conversion_Factor"]
            if len(str(conversion_data)) > 3:
                conversions = ast.literal_eval(conversion_data)
                name = df.loc[i, "Name"]
                
                # Find matching conversion factor
                conversion_value = 1  # Default value
                for key, value in conversions.items():
                    if name in key:
                        if isinstance(value, (float, int)):
                            conversion_value = value
                        else:
                            conversion_value = value[0]
                        break
                
                #not used later, but good to have it
                df.loc[i, "Additional_Conversion_Factor_Specific"] = conversion_value
                
                conversion_value_sum = sum(conversions.values())
                df.loc[i, "Additional_Conversion_Factor"] = conversion_value_sum
                
            else:
                df.loc[i, "Additional_Conversion_Factor_Specific"] = 1
                df.loc[i, "Additional_Conversion_Factor"] = 1
    
    return df


def select_amount_DF1(df):    #CHECK!
    df_temp=df.copy()

    # Pandas 2.x PyArrow-backed 'str' dtype rejects float/int assignments to string columns.
    # Raw_Material holds a stringified dict and will be overwritten with a numeric value below.
    if "Raw_Material" in df_temp.columns:
        _casted = df_temp["Raw_Material"].astype(object)
        # Normalize NaN/<NA> to real None so any `is not None` checks downstream still work.
        df_temp["Raw_Material"] = _casted.where(_casted.notna(), None)

    for i in df.index:
        # Guard against NaN/None values from pyarrow-backed columns — literal_eval
        # only works on strings.
        if not isinstance(df.loc[i,"Raw_Material"], str):
            continue
        rawmaterials = ast.literal_eval(df.loc[i,"Raw_Material"])
        for key in rawmaterials.keys():
            if df.loc[i,"Name"] in key and df.loc[i,"Region"] in key:
                if isinstance(rawmaterials[key], float) or isinstance(rawmaterials[key], int):
                    df_temp.loc[i,"Raw_Material"] = rawmaterials[key]
                else:
                    df_temp.loc[i,"Raw_Material"] = rawmaterials[key][0]

    return df_temp

def select_amount_DF345(df):
    # Pandas 2.x defaults to PyArrow-backed 'str' dtype for string columns.
    # Several columns below hold stringified dicts that will later be replaced
    # with float/int values from ast.literal_eval(...). PyArrow string columns
    # reject non-string assignments (TypeError: Invalid value 'X.Y' for dtype 'str').
    # Cast these columns to object up front so mixed-type writes keep working.
    _object_cast_cols = [
        "Material_Density", "Material_Thickness", "Material_Lambda", "Material_RSL",
        "Material_Density2", "Material_Thickness2", "Material_Lambda2", "Material_RSL2",
        "Material_Density3", "Material_Thickness3", "Material_Lambda3", "Material_RSL3",
        "Power_Mix_Percentage", "Power_Mix_Group_Percentage_Raw_Material",
        "Energy_Source", "Power_Transformation", "Power_Transmission_Network",
        "Raw_Material", "Waste_Treatment", "Loss",
    ]
    for _col in _object_cast_cols:
        if _col in df.columns:
            _casted = df[_col].astype(object)
            # Normalize pyarrow <NA>/np.nan to real None so existing
            # `is not None` checks behave as before (ast.literal_eval(nan) -> ValueError).
            df[_col] = _casted.where(_casted.notna(), None)

    # Also normalize Name2/Waste_Name which are compared with `is not None` below.
    for _col in ("Name2", "Waste_Name"):
        if _col in df.columns:
            _casted = df[_col].astype(object)
            df[_col] = _casted.where(_casted.notna(), None)

    for i in df.index:
        if "group for electricity" in df.loc[i,"Name"]: #power mix group
            df.loc[i,"Material_Density"] = df.loc[i,"Material_Density2"]
            df.loc[i,"Material_Thickness"] = df.loc[i,"Material_Thickness2"]
            df.loc[i,"Material_Lambda"] = df.loc[i,"Material_Lambda2"]
            df.loc[i,"Material_RSL"] = df.loc[i,"Material_RSL2"]
            df.loc[i,"Raw_Material"] = df.loc[i,"Raw_Material2"]
            df.loc[i,"Building_Material"] = df.loc[i,"Building_Material2"]
            df.loc[i,"Building_Component"] = df.loc[i,"Building_Component2"]
            df.loc[i,"Building_Construction_Type"] = df.loc[i,"Building_Construction_Type2"]
            df.loc[i,"Material_Unit"] = df.loc[i,"Material_Unit2"]
            
        if "group for electricity" not in df.loc[i,"Name"] and isinstance(df.loc[i,"Name2"], str): #materials at the same query level as power mix group
            df.loc[i,"Name"] = df.loc[i,"Name2"]
            df.loc[i,"Name2"] = None
            df.loc[i,"Material_Density"] = df.loc[i,"Material_Density2"]
            df.loc[i,"Material_Thickness"] = df.loc[i,"Material_Thickness2"]
            df.loc[i,"Material_Lambda"] = df.loc[i,"Material_Lambda2"]
            df.loc[i,"Material_RSL"] = df.loc[i,"Material_RSL2"]
            df.loc[i,"Raw_Material"] = df.loc[i,"Raw_Material2"]
            df.loc[i,"Building_Material"] = df.loc[i,"Building_Material2"]
            df.loc[i,"Building_Component"] = df.loc[i,"Building_Component2"]
            df.loc[i,"Building_Construction_Type"] = df.loc[i,"Building_Construction_Type2"]
            df.loc[i,"Material_Unit"] = df.loc[i,"Material_Unit2"]

        if isinstance(df.loc[i,"Waste_Name"], str):
            df.loc[i,"Material_Density"] = df.loc[i,"Material_Density3"]
            df.loc[i,"Material_Thickness"] = df.loc[i,"Material_Thickness3"]
            df.loc[i,"Material_Lambda"] = df.loc[i,"Material_Lambda3"]
            df.loc[i,"Material_RSL"] = df.loc[i,"Material_RSL3"]
            df.loc[i,"Raw_Material"] = df.loc[i,"Raw_Material3"]
            df.loc[i,"Building_Material"] = df.loc[i,"Building_Material3"]
            df.loc[i,"Building_Component"] = df.loc[i,"Building_Component3"]
            df.loc[i,"Building_Construction_Type"] = df.loc[i,"Building_Construction_Type3"]
            df.loc[i,"Material_Unit"] = df.loc[i,"Material_Unit3"]
    
    df_temp=pd.DataFrame()

    for i in df.index:
        # Use isinstance(..., str) rather than `is not None` because pyarrow-backed
        # columns may hold pd.NA / np.nan that compare != None but are not strings.
        if isinstance(df.loc[i,"Material_Density"], str):
            for key in ast.literal_eval(df.loc[i,"Material_Density"]).keys():
                if df.loc[i,"Building_Material"] in key:
                    temp = pd.DataFrame(df.loc[i,:]).T
                    
                    temp.loc[i,"Material_Density"] = ast.literal_eval(df.loc[i,"Material_Density"])[key]
                    temp.loc[i,"Material_Thickness"] = ast.literal_eval(df.loc[i,"Material_Thickness"])[key]
                    temp.loc[i,"Material_Lambda"] = ast.literal_eval(df.loc[i,"Material_Lambda"])[key]
                    temp.loc[i,"Material_RSL"] = ast.literal_eval(df.loc[i,"Material_RSL"])[key]
                    
                    temp.loc[i,"Building_Material"] = key
                    
                    df_temp=pd.concat([df_temp,temp])
                    df_temp=df_temp.reset_index(drop=True)
        else:
            temp = pd.DataFrame(df.loc[i,:]).T
            df_temp=pd.concat([df_temp,temp])
            df_temp=df_temp.reset_index(drop=True)
    
    # pd.concat above can promote None back to NaN on object columns; re-normalize
    # so the `is not None` guards around ast.literal_eval below still work correctly.
    for _col in (
        "Power_Mix_Percentage", "Power_Mix_Group_Percentage_Raw_Material",
        "Energy_Source", "Power_Transformation", "Power_Transmission_Network",
        "Raw_Material", "Waste_Treatment", "Name2",
    ):
        if _col in df_temp.columns:
            _casted = df_temp[_col].astype(object)
            df_temp[_col] = _casted.where(_casted.notna(), None)

    df_copy=df_temp.copy()

    for i in df_copy.index:
        # isinstance(..., str) is the correct guard for `ast.literal_eval` — pyarrow
        # string columns carry pd.NA/np.nan which pass `is not None` but crash literal_eval.
        if isinstance(df_copy.loc[i,"Power_Mix_Percentage"], str):
            powermixes = ast.literal_eval(df_copy.loc[i,"Power_Mix_Percentage"])
            for key in powermixes.keys():
                if df_copy.loc[i,"Power_Mix"] in key:
                    if isinstance(powermixes[key], float) or isinstance(powermixes[key], int):
                        df_temp.loc[i,"Power_Mix_Percentage"] = powermixes[key]
                    else:
                        df_temp.loc[i,"Power_Mix_Percentage"] = powermixes[key][0]

        if isinstance(df_copy.loc[i,"Power_Mix_Group_Percentage_Raw_Material"], str):
            powermixgroups = ast.literal_eval(df_copy.loc[i,"Power_Mix_Group_Percentage_Raw_Material"])
            for key in powermixgroups.keys():
                if df_copy.loc[i,"Name"] in key:
                    if isinstance(powermixgroups[key], float) or isinstance(powermixgroups[key], int):
                        df_temp.loc[i,"Power_Mix_Group_Percentage_Raw_Material"] = powermixgroups[key]
                    else:
                        df_temp.loc[i,"Power_Mix_Group_Percentage_Raw_Material"] = powermixgroups[key][0]

        if isinstance(df_copy.loc[i,"Energy_Source"], str):
            energysources = ast.literal_eval(df_copy.loc[i,"Energy_Source"])
            for key in energysources.keys():
                if df_copy.loc[i,"Name"] in key:
                    if isinstance(energysources[key], float) or isinstance(energysources[key], int):
                        df_temp.loc[i,"Energy_Source"] = energysources[key]
                    else:
                        df_temp.loc[i,"Energy_Source"] = energysources[key][0]

        if isinstance(df_copy.loc[i,"Power_Transformation"], str):
            powertransformations = ast.literal_eval(df_copy.loc[i,"Power_Transformation"])
            for key in powertransformations.keys():
                if df_copy.loc[i,"Name"] in key:
                    if isinstance(powertransformations[key], float) or isinstance(powertransformations[key], int):
                        df_temp.loc[i,"Power_Transformation"] = powertransformations[key]
                    else:
                        df_temp.loc[i,"Power_Transformation"] = powertransformations[key][0]

        if isinstance(df_copy.loc[i,"Power_Transmission_Network"], str):
            powertransmissions = ast.literal_eval(df_copy.loc[i,"Power_Transmission_Network"])
            for key in powertransmissions.keys():
                if df_copy.loc[i,"Name"] in key and "network" in df_copy.loc[i,"Name"]:
                    if isinstance(powertransmissions[key], float) or isinstance(powertransmissions[key], int):
                        df_temp.loc[i,"Power_Transmission_Network"] = powertransmissions[key]
                    else:
                        df_temp.loc[i,"Power_Transmission_Network"] = powertransmissions[key][0]

        if isinstance(df_copy.loc[i,"Raw_Material"], str):
            rawmaterials = ast.literal_eval(df_copy.loc[i,"Raw_Material"])
            for key in rawmaterials.keys():
                if df_copy.loc[i,"Name"] in key or (isinstance(df_copy.loc[i,"Name2"], str) and df_copy.loc[i,"Name2"] in key):
                    if any(keyword in key for keyword in geography):
                    #if "CH" in key or "RER" in key or "Europe without Austria" in key:
                        if isinstance(rawmaterials[key], float) or isinstance(rawmaterials[key], int):
                            df_temp.loc[i,"Raw_Material"] = rawmaterials[key]
                        else:
                            df_temp.loc[i,"Raw_Material"] = rawmaterials[key][0]

        if isinstance(df_copy.loc[i,"Waste_Treatment"], str):
            wastetreatments = ast.literal_eval(df_copy.loc[i,"Waste_Treatment"])
            for key in wastetreatments.keys():
                if df_copy.loc[i,"Name"] in key:
                    if isinstance(wastetreatments[key], float) or isinstance(wastetreatments[key], int):
                        df_temp.loc[i,"Waste_Treatment"] = 0-wastetreatments[key] #because waste in ecoinvent is negative
                    else:
                        df_temp.loc[i,"Waste_Treatment"] = 0-wastetreatments[key][0] #because waste in ecoinvent is negative
    
        if isinstance(df_copy.loc[i,"Loss"], float) or isinstance(df_copy.loc[i,"Loss"], int):
            df_temp.loc[i,"Loss"] = df_copy.loc[i,"Loss"]
        else:
            df_temp.loc[i,"Loss"] = ast.literal_eval(df_copy.loc[i,"Loss"])[0] 
        
    #df_temp=df_temp[((df_temp.Element_Amount_Energy_Source != '{}'))].reset_index(drop=True)
                        
    return df_temp.drop(["Material_Density2", "Material_Thickness2", "Material_Lambda2", "Material_RSL2", "Raw_Material2", "Building_Material2","Building_Component2","Building_Construction_Type2",
                         "Material_Density3", "Material_Thickness3", "Material_Lambda3", "Material_RSL3", "Raw_Material3", "Building_Material3","Building_Component3","Building_Construction_Type3",
                                              ], axis=1)


def read_db_b2(dynamic_factor, driver, URI, AUTH):
    """
    Reads building data from Neo4j database and processes it for B2 dynamic factors.
    
    Args:
        dynamic_factor: str, dynamic factor identifier
        buildingage: building age parameter NOT YET
        dynamic_scenario: scenario identifier NOT YET
        driver: Neo4j driver
        URI: database URI
        AUTH: authentication credentials
    
    Returns:
        tuple: (df_query_result_b2_further, df_query_result_b2_influence, df_query_result_b2_base)
    """
    if "B2" not in dynamic_factor:
        return None, None, None
    
    # Execute Neo4j query
    records, summary, keys = driver.execute_query("""
        MATCH 
        (b:Building)-[m]-(bc:Building_component)-[n]-(i:Initial_material_LCIA)-[o]-(wtr:Waste_treatment_ratio)-[t]-(q)
        OPTIONAL MATCH (q)-[s]-(df_b7_element: Dynamic_factor_b7_elementamount)
        
        WHERE
        bc.BuildingAge = $buildingage
        
        RETURN 
        b.Name, bc.Name, bc.Density, bc.Thickness, bc.LambdaValue, bc.RSL, i.Name, wtr.Name, wtr.FurtherTreatment, 
        q.Name, q.Scenario, q.DisposalChange, q.RecyclingChange, q.ReuseChange, q.CircularRecyclingChange, 
        q.ReplacemenRateCircularRecyclingChange, q.Unit, df_b7_element.ElementAmount, TYPE(t), 
        wtr.ReductionInMaterial, wtr.AdditionalConversionFactor, wtr.Disposal, wtr.Recycling, 
        wtr.CircularRecycling, wtr.Reuse, wtr.WasteReductionMax
        """,
        buildingage=buildingage,
        database_="neo4j",
    )    
    
    print(f"The query returned {len(records)} records in {summary.result_available_after} ms.")
    
    # Create base dataframe
    columns = [
        "Building_Construction_Type", "Building_Component", "Material_Density", "Material_Thickness",
        "Material_Lambda", "Material_RSL", "Building_Material", "Waste_Treatment_Ratio", 
        "Further_Treatment", "Name", "Dynamic_Scenario", "Disposal_Change", "Recycling_Change",
        "Reuse_Change", "Circular_Recycling_Change", "Replacement_Rate", "Unit", "Element_Amount",
        "Link", "Reduction_In_Material_Max", "Additional_Conversion_Factor", "Disposal_Current",
        "Recycling_Current", "Circular_Recycling_Current", "Reuse_Current", "Waste_Reduction_Max"
    ]
    
    df_query_result_b2_base = pd.DataFrame(records, columns=columns)
    df_query_result_b2_base = select_amount(df_query_result_b2_base).drop_duplicates(keep="first")
    
    # Filter dataframes based on conditions
    conditions = {
        'has_further_treatment': df_query_result_b2_base["Further_Treatment"].str.len() > 3,
        'correct_scenario': df_query_result_b2_base["Dynamic_Scenario"] == dynamic_scenario
    }
    
    df_scenario = df_query_result_b2_base.loc[
        conditions['correct_scenario'] & conditions['has_further_treatment'] & 
        (df_query_result_b2_base["Link"] == "IS_DYNAMIC_FACTOR_B2_OF")
    ].reset_index(drop=True)
    
    df_further = df_query_result_b2_base.loc[
        conditions['has_further_treatment'] & 
        (df_query_result_b2_base["Link"] == "DEFINES_THE_FURTHER_TREATMENT_QUANTITY_OF")
    ].reset_index(drop=True)
    
    df_influence = df_query_result_b2_base.loc[
        conditions['has_further_treatment'] & 
        (df_query_result_b2_base["Link"] == "INFLUENCES_THE_QUANTITY_OF")
    ].reset_index(drop=True)
    
    # Match scenario information to respective materials
    building_match_cols = ["Building_Construction_Type", "Building_Component", "Building_Material"]
    
    for i in df_scenario.index:
        scenario_match = df_scenario.loc[i, building_match_cols]
        
        # Update further treatment dataframe
        further_mask = (df_further[building_match_cols] == scenario_match).all(axis=1)
        for col in ["Disposal_Change", "Recycling_Change", "Reuse_Change", "Circular_Recycling_Change"]:
            df_further.loc[further_mask, col] = df_scenario.loc[i, col]
        
        # Update influence dataframe
        influence_mask = (df_influence[building_match_cols] == scenario_match).all(axis=1)
        df_influence.loc[influence_mask, "Replacement_Rate"] = df_scenario.loc[i, "Replacement_Rate"]
    
    # Process dataframes with combined function
    df_further = process_amounts_DF2(df_further, "further")
    df_influence = process_amounts_DF2(df_influence, "influence")
    
    # Fill missing values
    df_influence["Reduction_Reference"] = df_influence["Reduction_Reference"].fillna(0)
    
    for i in df_further.index:
        further_match = df_further.loc[i, building_match_cols]
        influence_mask = (df_influence[building_match_cols] == further_match).all(axis=1)
        
        if influence_mask.any():
            matching_indices = df_influence[influence_mask].index #go through all rows
            
            for influence_idx in matching_indices:
                # Copy values from influence to further
                copy_cols = [
                    "Reduction_In_Material_Max", "Additional_Conversion_Factor", 
                    "Disposal_Current", "Recycling_Current", "Circular_Recycling_Current", 
                    "Reuse_Current"
                ]
                for col in copy_cols:
                    df_further.loc[i, col] = df_influence.loc[influence_idx, col]
                
                df_further.loc[i, "Reduction_Reference"] = df_influence.loc[influence_idx, "Amount"]
                
                # Copy values from further to influence
                df_influence.loc[influence_idx, "Reduction_Reference_Waste"] = df_further.loc[i, "Reduction_Reference_Waste"]
                df_influence.loc[influence_idx, "Waste_Reduction_Max"] = df_further.loc[i, "Waste_Reduction_Max"]

    # Final cleanup
    df_influence["Reduction_Reference_Waste"] = df_influence["Reduction_Reference_Waste"].fillna(0)
    df_influence["Waste_Reduction_Max"] = np.where(
        df_influence["Waste_Reduction_Max"] == "{-}", 
        1, 
        df_influence["Waste_Reduction_Max"]
    )
    
    return df_further, df_influence, df_query_result_b2_base


def read_db_b1(dynamic_factor, driver, URI, AUTH, df_query_result):
    #Transport influence not yet considered in this state of the study, production like polymer foaming, extrusion plastic film is not affected thus also excluded
    if "B1" not in dynamic_factor:
        df_query_result_b1=None
        df_query_result_b1_prep=None
    if "B1" in dynamic_factor:
        records, summary, keys = driver.execute_query("""
            
            MATCH (b:Building)-[m]-(bc:Building_component)-[n]-(i)-[o:FORMS_RAW_MATERIAL_OF|IS_DYNAMIC_FACTOR_B1_OF|CONTAINS_ELEMENT_AMOUNT_OF]-(x) 
            OPTIONAL MATCH (x)-[q]-(df_b7_element:Dynamic_factor_b7_elementamount)
            
            WHERE
            bc.BuildingAge = $buildingage
            
            RETURN 
            b.Name, bc.Name, bc.Density, bc.Thickness, bc.LambdaValue, bc.RSL, i.Name, i.RawMaterial,
            x.ImportRatioChange, x.LowerOutlier, x.LowerOutlierF, x.UpperOutlier, x.UpperOutlierF, x.Name, x.Unit, x.Region, x.Scenario,
            df_b7_element.ElementAmount,TYPE(o)
            
            """,
            
            buildingage=buildingage,
            
            database_="neo4j",
        )

        # Summary information  
        print("The query returned {records_count} records in {time} ms.".format(
            records_count=len(records),
            time=summary.result_available_after
        ))
                    
        df_query_result_b1_base = pd.DataFrame(records, columns = ["Building_Construction_Type",
                                                                   "Building_Component",
                                                                   "Material_Density",
                                                                   "Material_Thickness",
                                                                   "Material_Lambda",
                                                                   "Material_RSL",
                                                                   "Building_Material",
                                                                   "Raw_Material",
                                                                   "Import_Ratio_Change",
                                                                   "Lower_Outlier",
                                                                   "Lower_Outlier_F",
                                                                   "Upper_Outlier",
                                                                   "Upper_Outlier_F",
                                                                   "Name",
                                                                   "Unit",
                                                                   "Region",
                                                                   "Dynamic_Scenario",
                                                                   "Element_Amount",
                                                                   "Link"
                                                                   ])

        df_query_result_b1_base = select_amount(df_query_result_b1_base)
        #df_query_result_b1_original=df_query_result_b1_base.loc[(df_query_result_b1_base["Link"]=="CONTAINS_ELEMENT_AMOUNT_OF")].reset_index(drop=True) #for check: size should be the same as the df_query_result
        
        df_query_result_b1_factor=df_query_result_b1_base.loc[(df_query_result_b1_base["Dynamic_Scenario"]==dynamic_scenario) & (df_query_result_b1_base["Link"]=="IS_DYNAMIC_FACTOR_B1_OF")].reset_index(drop=True).drop(["Unit", "Element_Amount","Raw_Material","Material_Density","Material_Thickness","Material_Lambda","Material_RSL"], axis=1)
        df_query_result_b1_rawmaterial=df_query_result_b1_base.loc[(df_query_result_b1_base["Link"]=="FORMS_RAW_MATERIAL_OF")].reset_index(drop=True)
        
        df_query_result_b1_rawmaterial = select_amount_DF1(df_query_result_b1_rawmaterial).drop_duplicates(keep="first").drop(["Import_Ratio_Change", "Lower_Outlier", "Lower_Outlier_F", "Upper_Outlier", "Upper_Outlier_F", "Dynamic_Scenario"], axis=1) 
        df_query_result_b1_prep=pd.merge(df_query_result_b1_rawmaterial, df_query_result_b1_factor, on=['Building_Construction_Type',"Building_Component","Building_Material"], how='inner')
        #after the above step, there are region_x and region_y. For import, region_x is relevant.
        
                
        # Optimized: group prep rows by (construction type, component, material) once,
        # then assemble per-row entries by dict lookup (was: O(N*M) double loop with
        # scalar .loc comparisons). Output verified bit-identical.
        df_query_result_b1_prep["Amount"] = [float(v) for v in df_query_result_b1_prep["Import_Ratio_Change"]]
        _b1_groups = {}
        for j in df_query_result_b1_prep.index:
            _key = (df_query_result_b1_prep.loc[j,"Building_Construction_Type"],
                    df_query_result_b1_prep.loc[j,"Building_Component"],
                    df_query_result_b1_prep.loc[j,"Building_Material"])
            _b1_groups.setdefault(_key, []).append(df_query_result_b1_prep.iloc[[j]].reset_index(drop=True))

        df_query_result_b1=[]
        for i in df_query_result.index:
            _key = (df_query_result.loc[i,"Building_Construction_Type"],
                    df_query_result.loc[i,"Building_Component"],
                    df_query_result.loc[i,"Building_Material"])
            df_query_result_b1.append([_key[0], _key[1], _key[2],
                                       [d.copy() for d in _b1_groups.get(_key, [])]])

    return df_query_result_b1, df_query_result_b1_prep
             
def read_db_b345(dynamic_factor, driver, URI, AUTH):
    
    df_query_result_b5_final_material=None
    df_query_result_b5_final_waste=None
    df_query_result_b5_dynamic_ratio=None 
    df_query_result_b5_energysource_amount=None
    df_query_result_b4_final_material=None
    df_query_result_b4_final_waste=None
    df_query_result_b4_dynamic_ratio=None
    df_query_result_b4_energysource_amount=None
    medium2low=None
    medium_ratio_static=None
    df_query_result_b3_final_material=None
    df_query_result_b3_final_waste=None
    df_query_result_b3_dynamic_ratio=None
    df_query_result_b3_energysource_amount=None
    high2medium=None
    high_ratio_static=None
    
    df_query_result_b5_final_heat=None
    df_query_result_b5_final_power=None
    df_query_result_b4_final_heat=None
    df_query_result_b4_final_power=None
    df_query_result_b3_final_heat=None
    df_query_result_b3_final_power=None
    
    if "B3" in dynamic_factor or "B4" in dynamic_factor or "B5" in dynamic_factor or "power-2024" in dynamic_factor:
        records, summary, keys = driver.execute_query("""
            
            MATCH (e:Initial_powermix_LCIA)-[t]-(o)
            
            OPTIONAL MATCH (o)-[x]-(df_b7_element:Dynamic_factor_b7_elementamount) 
            OPTIONAL MATCH (o)-[y]-(i:Initial_material_LCIA)-[u]-(bc:Building_component)-[d]-(b:Building)
            OPTIONAL MATCH (o)-[z]-(iw:Initial_waste_LCIA)-[zz]-(wr:Waste_treatment_ratio)-[zzz]-(i3:Initial_material_LCIA)-[u3]-(bc3:Building_component)-[d3]-(b3:Building)
            OPTIONAL MATCH (o)-[xx]-(ir:Initial_rawmaterial_LCIA)-[xxx]-(i2:Initial_material_LCIA)-[u2]-(bc2:Building_component)-[d2]-(b2:Building)
            
            RETURN e.Name, e.Loss, e.EnergySource, e.PowerTransformation, e.PowerTransmissionNetwork, o.Name, ir.Name, o.PowerMix, o.EnergySource, 
            o.Year, b.Name,b2.Name,b3.Name, bc.Name, bc2.Name, bc3.Name, bc.Density, bc2.Density, bc3.Density, bc.Thickness, bc2.Thickness, bc3.Thickness, 
            bc.LambdaValue, bc2.LambdaValue, bc3.LambdaValue, bc.RSL, bc2.RSL, bc3.RSL, i.Name, i2.Name, i3.Name, i.RawMaterial,i2.RawMaterial, 
            i3.RawMaterial, o.ElementAmount, df_b7_element.ElementAmount, e.Unit, iw.Name, iw.Treatment, ir.PowerMixGroup, wr.Name, o.Scenario,
            i.Unit, i2.Unit, i3.Unit
            

            """,
            
            buildingage=buildingage,
            
            database_="neo4j",
        )

        # Summary information  
        print("The query returned {records_count} records in {time} ms.".format(
            records_count=len(records),
            time=summary.result_available_after
        ))

        df_query_result_b345_base = pd.DataFrame(records, columns = ["Power_Mix",
                                                                   "Loss",
                                                                   "Energy_Source",
                                                                   "Power_Transformation",
                                                                   "Power_Transmission_Network",
                                                                   "Name",
                                                                   "Name2",
                                                                   "Power_Mix_Percentage",
                                                                   "Energy_Source_Percentage_Dynamic",
                                                                   "Year",
                                                                   "Building_Construction_Type",
                                                                   "Building_Construction_Type2",
                                                                   "Building_Construction_Type3",
                                                                   "Building_Component",
                                                                   "Building_Component2",
                                                                   "Building_Component3",
                                                                   "Material_Density",
                                                                   "Material_Density2",
                                                                   "Material_Density3",
                                                                   "Material_Thickness",
                                                                   "Material_Thickness2",
                                                                   "Material_Thickness3",
                                                                   "Material_Lambda",
                                                                   "Material_Lambda2",
                                                                   "Material_Lambda3",
                                                                   "Material_RSL",
                                                                   "Material_RSL2",
                                                                   "Material_RSL3",
                                                                   "Building_Material",
                                                                   "Building_Material2",
                                                                   "Building_Material3",
                                                                   "Raw_Material",
                                                                   "Raw_Material2",
                                                                   "Raw_Material3",
                                                                   "Element_Amount_Power_Mix",
                                                                   "Element_Amount_Energy_Source",
                                                                   "Unit",
                                                                   "Waste_Name",
                                                                   "Waste_Treatment",
                                                                   "Power_Mix_Group_Percentage_Raw_Material",
                                                                   "Waste_Treatment_Ratio",
                                                                   "Dynamic_Scenario",
                                                                   "Material_Unit",
                                                                   "Material_Unit2",
                                                                   "Material_Unit3"

                                                                   ])
        
        df_query_result_b345_base=select_amount_DF345(df_query_result_b345_base)


    #low voltage
    if "B5" in dynamic_factor or "B4" in dynamic_factor or "B3" in dynamic_factor or "power-2024" in dynamic_factor:
        
        df_query_result_b5_base=df_query_result_b345_base.loc[(df_query_result_b345_base["Power_Mix"]=="electricity, low voltage")].reset_index(drop=True)
        
        df_query_result_b5_rawmaterial=df_query_result_b5_base.loc[(df_query_result_b5_base["Raw_Material"].notna()) 
                                                                   & (df_query_result_b5_base["Name2"].isna()) 
                                                                   & (df_query_result_b5_base["Waste_Name"].isna())
                                                                   #below: at the same level as power mix group
                                                                   | (df_query_result_b5_base["Power_Mix_Group_Percentage_Raw_Material"].notna()) 
                                                                   & (df_query_result_b5_base["Name"].str.contains("group for electricity" )==False)
                                                                   ].reset_index(drop=True)
        
        #NOT IN USE YET!
        df_query_result_b5_rawmaterial_extra=df_query_result_b5_base.loc[#below: Production without building material context (relevant to B2)                                                               
                                                                   (df_query_result_b5_base["Name2"].isna()) 
                                                                   & (df_query_result_b5_base["Raw_Material"].isna())
                                                                   & (df_query_result_b5_base["Name"].str.contains("electricity" )==False)
                                                                   & (df_query_result_b5_base["Name"].str.contains("heat production" )==False)
                                                                   & (df_query_result_b5_base["Name"].str.contains("operation" )==False)
                                                                   & (df_query_result_b5_base["Name"].str.contains("treatment of waste" )==False)
                                                                   & (df_query_result_b5_base["Power_Mix_Percentage"]!="{}")
                                                                   ].reset_index(drop=True)
        
        df_query_result_b5_powermixgroup=df_query_result_b5_base.loc[(df_query_result_b5_base["Power_Mix_Group_Percentage_Raw_Material"].notna())& (df_query_result_b5_base["Name"].str.contains("group for electricity" ))].reset_index(drop=True)
        df_query_result_b5_wastetreatment=df_query_result_b5_base.loc[(df_query_result_b5_base["Waste_Treatment"].notna())].reset_index(drop=True)
        df_query_result_b5_powermix_amount=df_query_result_b5_base.loc[(df_query_result_b5_base["Element_Amount_Power_Mix"].notna())].reset_index(drop=True)
        
        #transformation and distribution included in energysource, it just does not need to be dynamic
        df_query_result_b5_energysource_amount=df_query_result_b5_base.loc[(df_query_result_b5_base["Element_Amount_Energy_Source"].notna()) 
                                                                           & (df_query_result_b5_base["Raw_Material"].isna()) 
                                                                           & (df_query_result_b5_base["Waste_Name"].isna()) 
                                                                           & (df_query_result_b5_base["Power_Mix_Percentage"]=="{}") 
                                                                           | (df_query_result_b5_base["Name"].str.contains("transformation" )) 
                                                                           & (df_query_result_b5_base["Power_Transformation"].apply(lambda x: isinstance(x, float)))
                                                                           | (df_query_result_b5_base["Name"].str.contains("distribution"))].reset_index(drop=True)
        
        df_query_result_b5_dynamic_ratio=df_query_result_b5_base.loc[(df_query_result_b5_base["Energy_Source_Percentage_Dynamic"].notna() & (df_query_result_b5_base["Dynamic_Scenario"]==dynamic_scenario))].reset_index(drop=True)
            
        #material
        df_query_result_b5_final_material=[]
        
        for i in df_query_result.index:
            df_query_result_b5_final_material.append([df_query_result.loc[i,"Building_Construction_Type"],df_query_result.loc[i,"Building_Component"],df_query_result.loc[i,"Building_Material"],[],[]])
            
        for i in df_query_result_b5_final_material:
            for j in df_query_result_b5_rawmaterial.index:
                if df_query_result_b5_rawmaterial.loc[j,"Building_Construction_Type"] == i[0]\
                and df_query_result_b5_rawmaterial.loc[j,"Building_Component"] == i[1]\
                and df_query_result_b5_rawmaterial.loc[j,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b5_rawmaterial.iloc[[j]].reset_index(drop=True))
                    i[4]=[df_query_result_b5_powermix_amount,df_query_result_b5_energysource_amount,df_query_result_b5_dynamic_ratio]
            
            for d in df_query_result_b5_powermixgroup.index:
                if df_query_result_b5_powermixgroup.loc[d,"Building_Construction_Type"] == i[0]\
                and df_query_result_b5_powermixgroup.loc[d,"Building_Component"] == i[1]\
                and df_query_result_b5_powermixgroup.loc[d,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b5_powermixgroup.iloc[[d]].reset_index(drop=True))
                    i[4]=[df_query_result_b5_powermix_amount,df_query_result_b5_energysource_amount,df_query_result_b5_dynamic_ratio]

        #waste
        df_query_result_b5_final_waste=[]
        
        for i in df_query_result.index:
            df_query_result_b5_final_waste.append([df_query_result.loc[i,"Building_Construction_Type"],df_query_result.loc[i,"Building_Component"],df_query_result.loc[i,"Building_Material"],[],[]])
            
        for i in df_query_result_b5_final_waste:
            for j in df_query_result_b5_wastetreatment.index:
                if df_query_result_b5_wastetreatment.loc[j,"Building_Construction_Type"] == i[0]\
                and df_query_result_b5_wastetreatment.loc[j,"Building_Component"] == i[1]\
                and df_query_result_b5_wastetreatment.loc[j,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b5_wastetreatment.iloc[[j]].reset_index(drop=True))
                    i[4]=[df_query_result_b5_powermix_amount,df_query_result_b5_energysource_amount,df_query_result_b5_dynamic_ratio]
        
        
        #heat
        df_query_result_b5_final_heat=[]
        
        for i in df_query_result_heat.index:
            df_query_result_b5_final_heat.append([df_query_result_heat.loc[i,"Heat"],
                                                  df_query_result_heat.loc[i,"Energysource"],
                                                  df_query_result_heat.loc[i,"Power_Mix"],
                                                  [df_query_result_b5_powermix_amount,df_query_result_b5_energysource_amount,df_query_result_b5_dynamic_ratio]])
        
        df_query_result_b5_final_power = [[[],[],[],[df_query_result_b5_powermix_amount,df_query_result_b5_energysource_amount,df_query_result_b5_dynamic_ratio]]]
        
    #medium voltage
    if "B4" in dynamic_factor or "B3" in dynamic_factor or "power-2024" in dynamic_factor:
        
        df_query_result_b4_base=df_query_result_b345_base.loc[(df_query_result_b345_base["Power_Mix"]=="electricity, medium voltage")].reset_index(drop=True)
        
        df_query_result_b4_rawmaterial=df_query_result_b4_base.loc[(df_query_result_b4_base["Raw_Material"].notna()) 
                                                                   & (df_query_result_b4_base["Name2"].isna()) 
                                                                   & (df_query_result_b4_base["Waste_Name"].isna()) 
                                                                   #below: at the same level as power mix group
                                                                   | (df_query_result_b4_base["Power_Mix_Group_Percentage_Raw_Material"].notna()) 
                                                                   & (df_query_result_b4_base["Name"].str.contains("group for electricity" )==False)
                                                                   ].reset_index(drop=True)
        #NOT IN USE YET!
        df_query_result_b4_rawmaterial_extra=df_query_result_b4_base.loc[#below: Production without building material context (relevant to B2)                                                               
                                                                   (df_query_result_b4_base["Name2"].isna()) 
                                                                   & (df_query_result_b4_base["Raw_Material"].isna())
                                                                   & (df_query_result_b4_base["Name"].str.contains("electricity" )==False)
                                                                   & (df_query_result_b4_base["Name"].str.contains("heat production" )==False)
                                                                   & (df_query_result_b4_base["Name"].str.contains("operation" )==False)
                                                                   & (df_query_result_b4_base["Name"].str.contains("treatment of waste" )==False)
                                                                   & (df_query_result_b4_base["Power_Mix_Percentage"]!="{}")
                                                                   ].reset_index(drop=True)
        
        df_query_result_b4_wastetreatment=df_query_result_b4_base.loc[(df_query_result_b4_base["Waste_Treatment"].notna())].reset_index(drop=True)
        df_query_result_b4_powermix_amount=df_query_result_b4_base.loc[(df_query_result_b4_base["Element_Amount_Power_Mix"].notna())].reset_index(drop=True)
        df_query_result_b4_powermixgroup=df_query_result_b4_base.loc[(df_query_result_b4_base["Power_Mix_Group_Percentage_Raw_Material"].notna()) & (df_query_result_b4_base["Name"].str.contains("group for electricity" ))].reset_index(drop=True)

        #transformation and transmission included in energysource, it just does not need to be dynamic
        #for medium and high voltages it is transmission, for low voltage it is distribution
        df_query_result_b4_energysource_amount=df_query_result_b4_base.loc[(df_query_result_b4_base["Element_Amount_Energy_Source"].notna()) 
                                                                           & (df_query_result_b4_base["Raw_Material"].isna()) 
                                                                           & (df_query_result_b4_base["Waste_Name"].isna()) 
                                                                           & (df_query_result_b4_base["Power_Mix_Percentage"]=="{}") 
                                                                           | (df_query_result_b4_base["Name"].str.contains("transformation" )) 
                                                                           & (df_query_result_b4_base["Power_Transformation"].apply(lambda x: isinstance(x, float)))
                                                                           | (df_query_result_b4_base["Name"].str.contains("transmission"))].reset_index(drop=True)
        
        df_query_result_b4_energysource_amount_tolower=df_query_result_b4_base.loc[(df_query_result_b4_base["Name"].str.contains("transformation" )) 
                                                                                   & df_query_result_b4_base["Power_Transformation"].apply(lambda x: isinstance(x, str))
                                                                                   ].reset_index(drop=True)
        
        df_query_result_b4_dynamic_ratio=df_query_result_b4_base.loc[(df_query_result_b4_base["Energy_Source_Percentage_Dynamic"].notna() & (df_query_result_b4_base["Dynamic_Scenario"]==dynamic_scenario))].reset_index(drop=True)
        
           
        #material
        df_query_result_b4_final_material=[]
        
        for i in df_query_result.index:
            df_query_result_b4_final_material.append([df_query_result.loc[i,"Building_Construction_Type"],df_query_result.loc[i,"Building_Component"],df_query_result.loc[i,"Building_Material"],[],[]])
            
        for i in df_query_result_b4_final_material:
            for j in df_query_result_b4_rawmaterial.index:
                if df_query_result_b4_rawmaterial.loc[j,"Building_Construction_Type"] == i[0]\
                and df_query_result_b4_rawmaterial.loc[j,"Building_Component"] == i[1]\
                and df_query_result_b4_rawmaterial.loc[j,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b4_rawmaterial.iloc[[j]].reset_index(drop=True))
                    i[4]=[df_query_result_b4_powermix_amount,df_query_result_b4_energysource_amount,df_query_result_b4_dynamic_ratio]
            
            for d in df_query_result_b4_powermixgroup.index:
                if df_query_result_b4_powermixgroup.loc[d,"Building_Construction_Type"] == i[0]\
                and df_query_result_b4_powermixgroup.loc[d,"Building_Component"] == i[1]\
                and df_query_result_b4_powermixgroup.loc[d,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b4_powermixgroup.iloc[[d]].reset_index(drop=True))
                    i[4]=[df_query_result_b4_powermix_amount,df_query_result_b4_energysource_amount,df_query_result_b4_dynamic_ratio]

        #waste
        #NOT IN USE YET!
        df_query_result_b4_final_waste=[]
        
        for i in df_query_result.index:
            df_query_result_b4_final_waste.append([df_query_result.loc[i,"Building_Construction_Type"],df_query_result.loc[i,"Building_Component"],df_query_result.loc[i,"Building_Material"],[],[]])
            
        for i in df_query_result_b4_final_waste:
            for j in df_query_result_b4_wastetreatment.index:
                if df_query_result_b4_wastetreatment.loc[j,"Building_Construction_Type"] == i[0]\
                and df_query_result_b4_wastetreatment.loc[j,"Building_Component"] == i[1]\
                and df_query_result_b4_wastetreatment.loc[j,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b4_wastetreatment.iloc[[j]].reset_index(drop=True))
                    i[4]=[df_query_result_b4_powermix_amount,df_query_result_b4_energysource_amount,df_query_result_b4_dynamic_ratio]
        
        
        #heat
        df_query_result_b4_final_heat=[]
        
        for i in df_query_result_heat.index:
            df_query_result_b4_final_heat.append([df_query_result_heat.loc[i,"Heat"],
                                                  df_query_result_heat.loc[i,"Energysource"],
                                                  df_query_result_heat.loc[i,"Power_Mix"],
                                                  [df_query_result_b4_powermix_amount,df_query_result_b4_energysource_amount,df_query_result_b4_dynamic_ratio]])
        
        df_query_result_b4_final_power=[[[],[],[],[df_query_result_b4_powermix_amount,df_query_result_b4_energysource_amount,df_query_result_b4_dynamic_ratio]]]
        
        #influence on low voltage
        medium2low = df_query_result_b4_energysource_amount_tolower.loc[0,"Power_Mix_Percentage"]
        medium_ratio_static = df_query_result_b5_energysource_amount.loc[(df_query_result_b5_energysource_amount["Power_Transformation"].apply(lambda x: isinstance(x, float)))].reset_index(drop=True)
        
       
    #high voltage
    if "B3" in dynamic_factor or "power-2024" in dynamic_factor:
        
        df_query_result_b3_base=df_query_result_b345_base.loc[(df_query_result_b345_base["Power_Mix"]=="electricity, high voltage")].reset_index(drop=True)
        
        #NOT IN USE YET!
        df_query_result_b3_rawmaterial=df_query_result_b3_base.loc[(df_query_result_b3_base["Raw_Material"].notna()) 
                                                                   & (df_query_result_b3_base["Name2"].isna()) 
                                                                   & (df_query_result_b3_base["Waste_Name"].isna()) 
                                                                   #below: at the same level as power mix group
                                                                   | (df_query_result_b3_base["Power_Mix_Group_Percentage_Raw_Material"].notna()) 
                                                                   & (df_query_result_b3_base["Name"].str.contains("group for electricity" )==False)
                                                                   ].reset_index(drop=True)
        #NOT IN USE YET!
        df_query_result_b3_rawmaterial_extra=df_query_result_b3_base.loc[#below: Production without building material context (relevant to B2)                                                               
                                                                   (df_query_result_b3_base["Name2"].isna()) 
                                                                   & (df_query_result_b3_base["Raw_Material"].isna())
                                                                   & (df_query_result_b3_base["Name"].str.contains("electricity" )==False)
                                                                   & (df_query_result_b3_base["Name"].str.contains("heat production" )==False)
                                                                   & (df_query_result_b3_base["Name"].str.contains("operation" )==False)
                                                                   & (df_query_result_b3_base["Name"].str.contains("treatment of waste" )==False)
                                                                   & (df_query_result_b3_base["Power_Mix_Percentage"]!="{}")
                                                                   ].reset_index(drop=True)
        
        #NOT IN USE YET!
        df_query_result_b3_wastetreatment=df_query_result_b3_base.loc[(df_query_result_b3_base["Waste_Treatment"].notna())].reset_index(drop=True)
        
        df_query_result_b3_powermix_amount=df_query_result_b3_base.loc[(df_query_result_b3_base["Element_Amount_Power_Mix"].notna())].reset_index(drop=True)
        
        #NOT IN USE YET!
        df_query_result_b3_powermixgroup=df_query_result_b3_base.loc[(df_query_result_b3_base["Power_Mix_Group_Percentage_Raw_Material"].notna()) & (df_query_result_b3_base["Name"].str.contains("group for electricity" ))].reset_index(drop=True)

        #transformation and transmission included in energysource, it just does not need to be dynamic
        #for medium and high voltages it is transmission, for low voltage it is distribution
        df_query_result_b3_energysource_amount=df_query_result_b3_base.loc[(df_query_result_b3_base["Element_Amount_Energy_Source"].notna()) 
                                                                           & (df_query_result_b3_base["Raw_Material"].isna()) 
                                                                           & (df_query_result_b3_base["Waste_Name"].isna()) 
                                                                           & (df_query_result_b3_base["Power_Mix_Percentage"]=="{}") 
                                                                           | (df_query_result_b3_base["Name"].str.contains("transformation" )) 
                                                                           & (df_query_result_b3_base["Power_Transformation"].apply(lambda x: isinstance(x, float)))
                                                                           | (df_query_result_b3_base["Name"].str.contains("transmission"))].reset_index(drop=True)
        
        df_query_result_b3_energysource_amount_tolower=df_query_result_b3_base.loc[(df_query_result_b3_base["Name"].str.contains("transformation" )) 
                                                                                   & df_query_result_b3_base["Power_Transformation"].apply(lambda x: isinstance(x, str))
                                                                                   ].reset_index(drop=True)
        
        df_query_result_b3_dynamic_ratio=df_query_result_b3_base.loc[(df_query_result_b3_base["Energy_Source_Percentage_Dynamic"].notna() & (df_query_result_b3_base["Dynamic_Scenario"]==dynamic_scenario))].reset_index(drop=True)

       
        #material
        #NOT IN USE YET!
        df_query_result_b3_final_material=[]
        
        for i in df_query_result.index:
            df_query_result_b3_final_material.append([df_query_result.loc[i,"Building_Construction_Type"],df_query_result.loc[i,"Building_Component"],df_query_result.loc[i,"Building_Material"],[],[]])
            
        for i in df_query_result_b3_final_material:
            for j in df_query_result_b3_rawmaterial.index:
                if df_query_result_b3_rawmaterial.loc[j,"Building_Construction_Type"] == i[0]\
                and df_query_result_b3_rawmaterial.loc[j,"Building_Component"] == i[1]\
                and df_query_result_b3_rawmaterial.loc[j,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b3_rawmaterial.iloc[[j]].reset_index(drop=True))
                    i[4]=[df_query_result_b3_powermix_amount,df_query_result_b3_energysource_amount,df_query_result_b3_dynamic_ratio]
            
            for d in df_query_result_b3_powermixgroup.index:
                if df_query_result_b3_powermixgroup.loc[d,"Building_Construction_Type"] == i[0]\
                and df_query_result_b3_powermixgroup.loc[d,"Building_Component"] == i[1]\
                and df_query_result_b3_powermixgroup.loc[d,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b3_powermixgroup.iloc[[d]].reset_index(drop=True))
                    i[4]=[df_query_result_b3_powermix_amount,df_query_result_b3_energysource_amount,df_query_result_b3_dynamic_ratio]


        #waste
        #NOT IN USE YET!
        df_query_result_b3_final_waste=[]
        
        for i in df_query_result.index:
            df_query_result_b3_final_waste.append([df_query_result.loc[i,"Building_Construction_Type"],df_query_result.loc[i,"Building_Component"],df_query_result.loc[i,"Building_Material"],[],[]])
            
        for i in df_query_result_b3_final_waste:
            for j in df_query_result_b3_wastetreatment.index:
                if df_query_result_b3_wastetreatment.loc[j,"Building_Construction_Type"] == i[0]\
                and df_query_result_b3_wastetreatment.loc[j,"Building_Component"] == i[1]\
                and df_query_result_b3_wastetreatment.loc[j,"Building_Material"] == i[2]:
                    i[3].append(df_query_result_b3_wastetreatment.iloc[[j]].reset_index(drop=True))
                    i[4]=[df_query_result_b3_powermix_amount,df_query_result_b3_energysource_amount,df_query_result_b3_dynamic_ratio]
                
        #heat
        df_query_result_b3_final_heat=[]
        
        for i in df_query_result_heat.index:
            df_query_result_b3_final_heat.append([df_query_result_heat.loc[i,"Heat"],
                                                  df_query_result_heat.loc[i,"Energysource"],
                                                  df_query_result_heat.loc[i,"Power_Mix"],
                                                  [df_query_result_b3_powermix_amount,df_query_result_b3_energysource_amount,df_query_result_b3_dynamic_ratio]])
        
        df_query_result_b3_final_power=[[[],[],[],[df_query_result_b3_powermix_amount,df_query_result_b3_energysource_amount,df_query_result_b3_dynamic_ratio]]]
            
        #influence on low voltage
        high2medium = df_query_result_b3_energysource_amount_tolower.loc[0,"Power_Mix_Percentage"]
        high_ratio_static = df_query_result_b4_energysource_amount.loc[(df_query_result_b4_energysource_amount["Power_Transformation"].apply(lambda x: isinstance(x, float)))].reset_index(drop=True)
        
        
    return df_query_result_b5_final_material, df_query_result_b5_final_waste, df_query_result_b5_dynamic_ratio, df_query_result_b5_energysource_amount, df_query_result_b4_final_material, df_query_result_b4_final_waste, df_query_result_b4_dynamic_ratio, df_query_result_b4_energysource_amount, medium2low, medium_ratio_static, df_query_result_b3_final_material, df_query_result_b3_final_waste, df_query_result_b3_dynamic_ratio, df_query_result_b3_energysource_amount, high2medium, high_ratio_static, df_query_result_b5_final_heat, df_query_result_b4_final_heat, df_query_result_b3_final_heat, df_query_result_b5_final_power, df_query_result_b4_final_power, df_query_result_b3_final_power

#%%
##############################################################################################################################################################
#Part 2: Dynamic calculation functions

# ------------------------
# B7 dynamic-factor tables (AGWP/AGTP time-series)
#


from functools import lru_cache


def _default_b7_import_path() -> str:
    """Return a stable default path for InputResearch regardless of current working directory."""
    try:
        return str((Path(__file__).resolve().parent / "InputResearch").as_posix() + "/")
    except Exception:
        # fallback: keep old behavior
        return "./InputResearch/"


@lru_cache(maxsize=8)
def prepare_df_b7(import_path: str, years_param: int):

    import_path = import_path + "/"
    
    #Static and Dynamic LCIA processes (B7)

    #First import the calculation indicators
    df_dynamicfactor_b7_dagwp_co2 = pd.read_csv(import_path+"DAGWP/AGWP_co2_dynamic.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagwp_ch4_bio = pd.read_csv(import_path+"DAGWP/AGWP_ch4_dynamic_bio.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagwp_ch4_fossil = pd.read_csv(import_path+"DAGWP/AGWP_ch4_dynamic_fossil.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagwp_n2o = pd.read_csv(import_path+"DAGWP/AGWP_n2o_dynamic.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagwp_halogen = pd.read_csv(import_path+"DAGWP/AGWP_halogen_dynamic.csv").iloc[:, 1:]

    df_dynamicfactor_b7_dagtp_co2 = pd.read_csv(import_path+"DAGTP/AGTP_co2_dynamic.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagtp_ch4_bio = pd.read_csv(import_path+"DAGTP/AGTP_ch4_dynamic_bio.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagtp_ch4_fossil = pd.read_csv(import_path+"DAGTP/AGTP_ch4_dynamic_fossil.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagtp_n2o = pd.read_csv(import_path+"DAGTP/AGTP_n2o_dynamic.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagtp_halogen = pd.read_csv(import_path+"DAGTP/AGTP_halogen_dynamic.csv").iloc[:, 1:]

    #non-cumulative version
    df_dynamicfactor_b7_dagwp_co2_noncumulative = pd.read_csv(import_path+"DAGWP/AGWP_co2_dynamic_noncumulative.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagwp_ch4_bio_noncumulative = pd.read_csv(import_path+"DAGWP/AGWP_ch4_dynamic_bio_noncumulative.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagwp_ch4_fossil_noncumulative = pd.read_csv(import_path+"DAGWP/AGWP_ch4_dynamic_fossil_noncumulative.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagwp_n2o_noncumulative = pd.read_csv(import_path+"DAGWP/AGWP_n2o_dynamic_noncumulative.csv").iloc[:, 1:]
    df_dynamicfactor_b7_dagwp_halogen_noncumulative = pd.read_csv(import_path+"DAGWP/AGWP_halogen_dynamic_noncumulative.csv").iloc[:, 1:]

    indicators = {
        'co2': {
            'cumulative': {
                'agwp': df_dynamicfactor_b7_dagwp_co2["AGWP_co2"][0:years_param*10+1],
                'agwp_neg': 0-(df_dynamicfactor_b7_dagwp_co2["AGWP_co2"][0:years_param*10+1])
            },
            'non-cumulative': {
                'agwp': df_dynamicfactor_b7_dagwp_co2_noncumulative["AGWP_co2"][0:years_param*10+1],
                'agwp_neg': 0-(df_dynamicfactor_b7_dagwp_co2_noncumulative["AGWP_co2"][0:years_param*10+1])
            },
            'agtp': df_dynamicfactor_b7_dagtp_co2["AGTP_co2"][0:years_param*10+1],
            'agtp_neg': 0-(df_dynamicfactor_b7_dagtp_co2["AGTP_co2"][0:years_param*10+1])
        },
        'ch4_fossil': {
            'cumulative': {'agwp': df_dynamicfactor_b7_dagwp_ch4_fossil["AGWP_ch4"][0:years_param*10+1]},
            'non-cumulative': {'agwp': df_dynamicfactor_b7_dagwp_ch4_fossil_noncumulative["AGWP_ch4"][0:years_param*10+1]},
            'agtp': df_dynamicfactor_b7_dagtp_ch4_fossil["AGTP_ch4"][0:years_param*10+1]
        },
        'ch4_bio': {
            'cumulative': {'agwp': df_dynamicfactor_b7_dagwp_ch4_bio["AGWP_ch4"][0:years_param*10+1]},
            'non-cumulative': {'agwp': df_dynamicfactor_b7_dagwp_ch4_bio_noncumulative["AGWP_ch4"][0:years_param*10+1]},
            'agtp': df_dynamicfactor_b7_dagtp_ch4_bio["AGTP_ch4"][0:years_param*10+1]
        },
        'n2o': {
            'cumulative': {'agwp': df_dynamicfactor_b7_dagwp_n2o["AGWP_n2o"][0:years_param*10+1]},
            'non-cumulative': {'agwp': df_dynamicfactor_b7_dagwp_n2o_noncumulative["AGWP_n2o"][0:years_param*10+1]},
            'agtp': df_dynamicfactor_b7_dagtp_n2o["AGTP_n2o"][0:years_param*10+1]
        }
    }

    # Pre-compute halogen indicators
    halogen_indicators = {}
    for col in df_dynamicfactor_b7_dagwp_halogen.columns:
        halogen_indicators[col.lower()] = {
            'cumulative': {'agwp': df_dynamicfactor_b7_dagwp_halogen[col][0:years_param*10+1]},
            'non-cumulative': {'agwp': df_dynamicfactor_b7_dagwp_halogen_noncumulative[col][0:years_param*10+1]},
            'agtp': df_dynamicfactor_b7_dagtp_halogen[col][0:years_param*10+1]
        }
    
    return df_dynamicfactor_b7_dagwp_co2, df_dynamicfactor_b7_dagwp_ch4_bio, df_dynamicfactor_b7_dagwp_ch4_fossil,\
        df_dynamicfactor_b7_dagwp_n2o, df_dynamicfactor_b7_dagwp_halogen, df_dynamicfactor_b7_dagtp_co2,\
        df_dynamicfactor_b7_dagtp_ch4_bio, df_dynamicfactor_b7_dagtp_ch4_fossil, df_dynamicfactor_b7_dagtp_n2o,\
        df_dynamicfactor_b7_dagtp_halogen,\
        \
        df_dynamicfactor_b7_dagwp_co2_noncumulative, df_dynamicfactor_b7_dagwp_ch4_bio_noncumulative,\
        df_dynamicfactor_b7_dagwp_ch4_fossil_noncumulative, df_dynamicfactor_b7_dagwp_n2o_noncumulative,\
        df_dynamicfactor_b7_dagwp_halogen_noncumulative,\
        indicators, halogen_indicators




#%%
# Create a lookup for element processing to avoid repetitive if-else
def create_element_processor(indicators, halogen_indicators, cumulative):
    # Pre-compile regex patterns once
    patterns = {
        'co2_fossil': re.compile(r'carbon dioxide, fossil|carbon dioxide, from soil or biomass stock', re.IGNORECASE),
        'co2_bio': re.compile(r'carbon dioxide, to soil or biomass stock', re.IGNORECASE),
        'ch4_fossil': re.compile(r'methane, fossil|methane, from soil or biomass stock', re.IGNORECASE),
        'ch4_bio': re.compile(r'methane, non-fossil', re.IGNORECASE),
        'n2o': re.compile(r'dinitrogen monoxide', re.IGNORECASE)
    }
    
    # Pre-process halogen names for faster lookup
    halogen_lookup = {}
    special_halogens = {'butane', 'ethane', 'propane', 'ae'}
    for col in halogen_indicators.keys():
        halogen_lookup[col] = {
            'special': col in special_halogens,
            'indicators': halogen_indicators[col]
        }
    
    def process_element_optimized(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio):
        key_lower = key.lower()
        factor = elementamount * unit * area
        
        # Use regex matching instead of multiple string operations
        if patterns['co2_fossil'].search(key_lower):
            AGWP += factor * indicators['co2'][cumulative]['agwp']
            AGWP_fossil += factor * indicators['co2'][cumulative]['agwp']
            AGTP += factor * indicators['co2']['agtp']
            AGTP_fossil += factor * indicators['co2']['agtp']
            return
            
        if patterns['co2_bio'].search(key_lower):
            AGWP += factor * indicators['co2'][cumulative]['agwp_neg']
            AGWP_bio += factor * indicators['co2'][cumulative]['agwp_neg']
            AGTP += factor * indicators['co2']['agtp_neg']
            AGTP_bio += factor * indicators['co2']['agtp_neg']
            return
            
        if patterns['ch4_fossil'].search(key_lower):
            AGWP += factor * indicators['ch4_fossil'][cumulative]['agwp']
            AGWP_fossil += factor * indicators['ch4_fossil'][cumulative]['agwp']
            AGTP += factor * indicators['ch4_fossil']['agtp']
            AGTP_fossil += factor * indicators['ch4_fossil']['agtp']
            return
            
        if patterns['ch4_bio'].search(key_lower):
            AGWP += factor * indicators['ch4_bio'][cumulative]['agwp']
            AGWP_bio += factor * indicators['ch4_bio'][cumulative]['agwp']
            AGTP += factor * indicators['ch4_bio']['agtp']
            AGTP_bio += factor * indicators['ch4_bio']['agtp']
            return
            
        if patterns['n2o'].search(key_lower):
            AGWP += factor * indicators['n2o'][cumulative]['agwp']
            AGWP_fossil += factor * indicators['n2o'][cumulative]['agwp']
            AGTP += factor * indicators['n2o']['agtp']
            AGTP_fossil += factor * indicators['n2o']['agtp']
            return
        
        # Check halogens with optimized lookup
        for hal_name, hal_data in halogen_lookup.items():
            if hal_name in key_lower:
                if hal_data['special']:
                    # Special case for exact length match
                    if len(hal_name) != len(key):
                        continue
                
                AGWP += factor * hal_data['indicators'][cumulative]['agwp']
                AGWP_fossil += factor * hal_data['indicators'][cumulative]['agwp']
                AGTP += factor * hal_data['indicators']['agtp']
                AGTP_fossil += factor * hal_data['indicators']['agtp']
                return
    
    return process_element_optimized

def init_b7_resources(import_path: str | None = None, years_param: int | None = None, cumulative_param: str | None = None):
    """Initialize B7 CSV tables + element processor."""

    if import_path is None:
        import_path = str(B7_INPUT_DIR)

    if years_param is None:
        years_param = int(globals().get("years", 100))

    if cumulative_param is None:
        cumulative_param = str(globals().get("cumulative", "cumulative"))

    (
        globals()["df_dynamicfactor_b7_dagwp_co2"],
        globals()["df_dynamicfactor_b7_dagwp_ch4_bio"],
        globals()["df_dynamicfactor_b7_dagwp_ch4_fossil"],
        globals()["df_dynamicfactor_b7_dagwp_n2o"],
        globals()["df_dynamicfactor_b7_dagwp_halogen"],
        globals()["df_dynamicfactor_b7_dagtp_co2"],
        globals()["df_dynamicfactor_b7_dagtp_ch4_bio"],
        globals()["df_dynamicfactor_b7_dagtp_ch4_fossil"],
        globals()["df_dynamicfactor_b7_dagtp_n2o"],
        globals()["df_dynamicfactor_b7_dagtp_halogen"],
        globals()["df_dynamicfactor_b7_dagwp_co2_noncumulative"],
        globals()["df_dynamicfactor_b7_dagwp_ch4_bio_noncumulative"],
        globals()["df_dynamicfactor_b7_dagwp_ch4_fossil_noncumulative"],
        globals()["df_dynamicfactor_b7_dagwp_n2o_noncumulative"],
        globals()["df_dynamicfactor_b7_dagwp_halogen_noncumulative"],
        indicators_local,
        halogen_indicators_local,
    ) = prepare_df_b7(import_path, years_param)

    
    globals()["indicators"] = indicators_local
    globals()["halogen_indicators"] = halogen_indicators_local

    globals()["process_element"] = create_element_processor(
        indicators=indicators_local,
        halogen_indicators=halogen_indicators_local,
        cumulative=cumulative_param,
    )

    return globals()["process_element"]


            
#%%
#calculation functions-static
def static_LCIA_material (df_query_result_calc, LCIAindicator, years):
    GWP=0
    GWP_fossil=0
    GWP_bio=0
    GTP=0
    GTP_fossil=0
    GTP_bio=0
    
    for i in df_query_result_calc.index:   
        elementamounts = ast.literal_eval(df_query_result_calc.loc[i,"Element_Amount"])
        for key in elementamounts.keys():
            if "carbon dioxide, fossil" in key.lower() or "carbon dioxide, from soil or biomass stock" in key.lower():         
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = 1
                GWP += elementamount * indicator
                GWP_fossil += elementamount * indicator
                GTP += elementamount * indicator
                GTP_fossil += elementamount * indicator
            
            elif "carbon dioxide, to soil or biomass stock" in key.lower():
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = -1
                GWP += elementamount * indicator
                GWP_bio += elementamount * indicator
                GTP += elementamount * indicator
                GTP_bio += elementamount * indicator
            
            elif "methane, fossil" in key.lower() or "methane, from soil or biomass stock" in key.lower():
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_ch4_fossil.loc[years*10,"AGWP_ch4"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                #indicator = 29.8
                GWP += elementamount * indicator
                GWP_fossil += elementamount * indicator
                
                indicator = df_dynamicfactor_b7_dagtp_ch4_fossil.loc[years*10,"AGTP_ch4"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator
                GTP_fossil += elementamount * indicator
            
            elif "methane, non-fossil" in key.lower():
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_ch4_bio.loc[years*10,"AGWP_ch4"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                #indicator = 27
                GWP += elementamount * indicator
                GWP_bio += elementamount * indicator
                
                indicator = df_dynamicfactor_b7_dagtp_ch4_bio.loc[years*10,"AGTP_ch4"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator
                GTP_bio += elementamount * indicator
            
            elif "dinitrogen monoxide" in key.lower():
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_n2o.loc[years*10,"AGWP_n2o"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                GWP += elementamount * indicator
                GWP_fossil += elementamount * indicator
                
                indicator = df_dynamicfactor_b7_dagtp_n2o.loc[years*10,"AGTP_n2o"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator
                GTP_fossil += elementamount * indicator
            
            else:
                for col in df_dynamicfactor_b7_dagwp_halogen.columns:
                    if col.lower() in key.lower():
                        if col == "Butane" or col == "Ethane" or col == "Propane" or col == "AE":
                            if len(col) == len(key):
                                elementamount = elementamounts[key]
                                print(key + "---"+col +":"+str(elementamount))
                                indicator = df_dynamicfactor_b7_dagwp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                                GWP += elementamount * indicator
                                GWP_fossil += elementamount * indicator
                                
                                indicator = df_dynamicfactor_b7_dagtp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                                GTP += elementamount * indicator
                                GTP_fossil += elementamount * indicator
                        
                        else:
                            elementamount = elementamounts[key]
                            print(key + "---"+col +":"+str(elementamount))
                            indicator = df_dynamicfactor_b7_dagwp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                            GWP += elementamount * indicator
                            GWP_fossil += elementamount * indicator
                            
                            indicator = df_dynamicfactor_b7_dagtp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                            GTP += elementamount * indicator
                            GTP_fossil += elementamount * indicator        
        
    indicators = {
        "GWP": GWP,
        "GWP_fossil": GWP_fossil,
        "GWP_bio": GWP_bio,
        "GTP": GTP,
        "GTP_fossil": GTP_fossil,
        "GTP_bio": GTP_bio
    }
    return indicators.get(LCIAindicator)

def static_LCIA_component (df_query_result_calc_required, LCIAindicator, years, area, waste, component):
    GWP=0
    GWP_fossil=0
    GWP_bio=0
    GTP=0
    GTP_fossil=0
    GTP_bio=0
    
    #df_query_result_calc_required = df_query_result_calc_required[df_query_result_calc_required["Building_Construction_Type"].str.contains(building_type)]
    df_query_result_calc_required = df_query_result_calc_required.groupby(['Building_Material'], as_index=False).min()

    
    if len(df_query_result_calc_required) == 0:
        print("No Result: No component information")
        return 0
    
    for i in df_query_result_calc_required.index:   
        
        density=df_query_result_calc_required.loc[i,"Material_Density"]
        thickness=df_query_result_calc_required.loc[i,"Material_Thickness"] 
        rsl=df_query_result_calc_required.loc[i,"Material_RSL"] 
        
        if "BP" in component:
            rsl = rsp
        
        unit_lookup = {
            "m3": thickness,
            "kg": density * thickness,
            "m2": 1,
            "metric ton*km": density * thickness
            }
        unit = unit_lookup.get(df_query_result_calc_required.loc[i,"Material_Unit"], 1)

        #if df_query_result_calc_required.loc[i,"Material_Unit"] == "m" and "50 mm wide" in df_query_result_calc_required.loc[i,"Building_Material"]:
        #    #originally only 0.05m2 per meter, so it should be 20 times the component area
        #    #and in this case, the density and thickness dont play a role
        #    unit = 1/0.05
        
        if waste == True:
            
            if rsp % rsl == 0: # RSP is perfectly divisible by RSL
                replacements = math.floor(rsp/rsl) - 1
            else:
                replacements = math.floor(rsp/rsl)
        else:
            replacements = math.ceil(rsp/rsl)
        
        elementamounts = ast.literal_eval(df_query_result_calc_required.loc[i,"Element_Amount"])
        for key in elementamounts.keys():
            if "carbon dioxide, fossil" in key.lower() or "carbon dioxide, from soil or biomass stock" in key.lower():         
                elementamount = elementamounts[key]
                #print(key +":"+str(elementamount))
                indicator = 1
                GWP += elementamount * indicator * unit * area * replacements
                GWP_fossil += elementamount * indicator * unit * area * replacements
                GTP += elementamount * indicator * unit * area * replacements
                GTP_fossil += elementamount * indicator * unit * area * replacements
            
            elif "carbon dioxide, to soil or biomass stock" in key.lower():
                elementamount = elementamounts[key]
                #print(key +":"+str(elementamount))
                indicator = -1
                GWP += elementamount * indicator * unit * area * replacements
                GWP_bio += elementamount * indicator * unit * area * replacements
                GTP += elementamount * indicator * unit * area * replacements
                GTP_bio += elementamount * indicator * unit * area * replacements
            
            elif "methane, fossil" in key.lower() or "methane, from soil or biomass stock" in key.lower():
                elementamount = elementamounts[key]
                #print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_ch4_fossil.loc[years*10,"AGWP_ch4"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                #indicator = 29.8
                GWP += elementamount * indicator * unit * area * replacements
                GWP_fossil += elementamount * indicator * unit * area * replacements
                
                indicator = df_dynamicfactor_b7_dagtp_ch4_fossil.loc[years*10,"AGTP_ch4"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator * unit * area * replacements
                GTP_fossil += elementamount * indicator * unit * area * replacements
            
            elif "methane, non-fossil" in key.lower():
                elementamount = elementamounts[key]
                #print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_ch4_bio.loc[years*10,"AGWP_ch4"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                #indicator = 27
                GWP += elementamount * indicator * unit * area * replacements
                GWP_bio += elementamount * indicator * unit * area * replacements
                
                indicator = df_dynamicfactor_b7_dagtp_ch4_bio.loc[years*10,"AGTP_ch4"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator * unit * area * replacements
                GTP_bio += elementamount * indicator * unit * area * replacements
            
            elif "dinitrogen monoxide" in key.lower():
                elementamount = elementamounts[key]
                #print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_n2o.loc[years*10,"AGWP_n2o"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                GWP += elementamount * indicator * unit * area * replacements
                GWP_fossil += elementamount * indicator * unit * area * replacements
                
                indicator = df_dynamicfactor_b7_dagtp_n2o.loc[years*10,"AGTP_n2o"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator * unit * area * replacements
                GTP_fossil += elementamount * indicator * unit * area * replacements
            
            else:
                for col in df_dynamicfactor_b7_dagwp_halogen.columns:
                    if col.lower() in key.lower():
                        if col == "Butane" or col == "Ethane" or col == "Propane" or col == "AE":
                            if len(col) == len(key):
                                elementamount = elementamounts[key]
                                #print(key + "---"+col +":"+str(elementamount))
                                indicator = df_dynamicfactor_b7_dagwp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                                GWP += elementamount * indicator * unit * area * replacements
                                GWP_fossil += elementamount * indicator * unit * area * replacements
                                
                                indicator = df_dynamicfactor_b7_dagtp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                                GTP += elementamount * indicator * unit * area * replacements
                                GTP_fossil += elementamount * indicator * unit * area * replacements
                        
                        else:
                            elementamount = elementamounts[key]
                            #print(key + "---"+col +":"+str(elementamount))
                            indicator = df_dynamicfactor_b7_dagwp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                            GWP += elementamount * indicator * unit * area * replacements
                            GWP_fossil += elementamount * indicator * unit * area * replacements
                            
                            indicator = df_dynamicfactor_b7_dagtp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                            GTP += elementamount * indicator * unit * area * replacements
                            GTP_fossil += elementamount * indicator * unit * area * replacements    

    indicators = {
        "GWP": GWP,
        "GWP_fossil": GWP_fossil,
        "GWP_bio": GWP_bio,
        "GTP": GTP,
        "GTP_fossil": GTP_fossil,
        "GTP_bio": GTP_bio
    }
    return indicators.get(LCIAindicator)

#here no calculation, only summing the components up and plotting!  (unlike components and materials, the code here is only for without waste)
def static_LCIA_building (building_type, all_components, all_components_area, LCIAindicator, years): #here no calculation, only summing the components up and plotting!
    GWP_total=0
    GWP_fossil_total=0
    GWP_bio_total=0
    GTP_total=0
    GTP_fossil_total=0
    GTP_bio_total=0
    
    result_static_component=0
    
    required_building_type = df_query_result[df_query_result["Building_Construction_Type"].str.contains(building_type)]
    
    for component, area in zip(all_components, all_components_area):
        # Filter only the relevant component from the pre-filtered dataframe
        df_query_result_calc_required = required_building_type[required_building_type["Building_Component"].str.contains(component)]
        
        result_static_component += static_LCIA_component(df_query_result_calc_required, LCIAindicator, years, area, False, component)
        
    if LCIAindicator == "GWP":            
        GWP_total=result_static_component     
        print(GWP_total)
        return GWP_total
    
    if LCIAindicator == "GWP_fossil":
        GWP_fossil_total=result_static_component              
        print(GWP_fossil_total)
        return GWP_fossil_total
        
    if LCIAindicator == "GWP_bio":
        GWP_bio_total=result_static_component   
        print(GWP_bio_total)
        return GWP_bio_total
    
    if LCIAindicator == "GTP":
        GTP_total=result_static_component          
        print(GTP_total)
        return GTP_total
    if LCIAindicator == "GTP_fossil":
        GTP_fossil_total=result_static_component         
        print(GTP_fossil_total)
        return GTP_fossil_total
    if LCIAindicator == "GTP_bio":
        GTP_bio_total=result_static_component         
        print(GTP_bio_total)
        return GTP_bio_total


#calculation functions-dynamic
def dynamic_LCIA_b7_material_plot(LCIAindicator, LCIAindicatorvalue, cumulative, name):
    plt.figure(figsize=(10, 5))
    ax = plt.subplot()
    ax.plot(LCIAindicatorvalue,label=LCIAindicator+" "+name+", "+cumulative, linewidth=0.8)
    ax.fill_between(LCIAindicatorvalue.index,LCIAindicatorvalue, alpha=0.07)
    plt.xlabel("Year",fontsize=18)

    if "AGWP" in LCIAindicator and cumulative=="non-cumulative":
        plt.ylabel("Absolute Global Warming Potential \n (AGWP) [W m$^{-2} kg^{-1}$]",fontsize=16)
    if "AGWP" in LCIAindicator and cumulative=="cumulative":
        plt.ylabel("Absolute Global Warming Potential \n (AGWP) [W m$^{-2} yr kg^{-1}$]",fontsize=16)
    if "AGTP" in LCIAindicator:
        plt.ylabel("Absolute Global Temperature Potential \n (AGTP) [K $kg^{-1}$]",fontsize=16)
    plt.legend(fontsize=15)
    ticks=np.arange(0,(len(LCIAindicatorvalue)-1)/10 + 1,10)
    plt.xticks(np.linspace(0, len(LCIAindicatorvalue), len(ticks)), ticks.astype(int))
    plt.tick_params(labelsize=15)
    
    ax.spines["bottom"].set_linewidth(2)
    ax.spines[['right', 'top']].set_visible(False)
    
    ax.set_axisbelow(True)
    ax.grid(color='gray', linestyle='dashed', alpha=0.3)
   
    if phase_C:
     waste_folder = "with_waste"
    else:
     waste_folder = "without_waste"
    
    if "-" not in dynamic_factor:
        fn = PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_{cumulative}_{'_'.join(dynamic_factor)}_{dynamic_scenario}.pdf"  
        
    else:
        fn = PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_{cumulative}.pdf"    
        fn.parent.mkdir(parents=True, exist_ok=True)
    if not fn.exists():
        ax.figure.savefig(fn, bbox_inches="tight")
    


    if show_plots:
        plt.savefig(fn, bbox_inches="tight")
    else:
        plt.close()
    
def dynamic_LCIA_b7_material (df_query_result_calc, LCIAindicator, years, cumulative):
    AGWP=pd.Series(0, range(0,years*10+1))
    AGWP_fossil=pd.Series(0, range(0,years*10+1))
    AGWP_bio=pd.Series(0, range(0,years*10+1))
    AGTP=pd.Series(0, range(0,years*10+1))
    AGTP_fossil=pd.Series(0, range(0,years*10+1))
    AGTP_bio=pd.Series(0, range(0,years*10+1))
   
    for i in range(len(df_query_result_calc)):
        material=df_query_result_calc.loc[i,"Building_Material"]
        elementamounts = ast.literal_eval(df_query_result_calc.loc[i,"Element_Amount"])
        
        # Process each element in the current power
        for key, amount in elementamounts.items():
            elementamount = amount
            process_element(key, elementamount, 1, 1, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio) 
        
    if LCIAindicator == "AGWP":
        print(AGWP)
        #if phase_C==False: #so for the case when adding the waste interim results will not be plotted
        dynamic_LCIA_b7_material_plot(LCIAindicator,AGWP,cumulative,material)
        return AGWP
    
    if LCIAindicator == "AGWP_fossil":
        print(AGWP_fossil)
        #if phase_C==False:
        dynamic_LCIA_b7_material_plot(LCIAindicator,AGWP_fossil,cumulative,material)
        return AGWP_fossil
    
    if LCIAindicator == "AGWP_bio":
        print(AGWP_bio)
        #if phase_C==False:
        dynamic_LCIA_b7_material_plot(LCIAindicator,AGWP_bio,cumulative,material)
        return AGWP_bio
    
    if LCIAindicator == "AGTP":
        print(AGTP)
        #if phase_C==False:
        dynamic_LCIA_b7_material_plot(LCIAindicator,AGTP,cumulative,material)
        return AGTP
    
    if LCIAindicator == "AGTP_fossil":
        print(AGTP_fossil)
        #if phase_C==False:
        dynamic_LCIA_b7_material_plot(LCIAindicator,AGTP_fossil,cumulative,material)
        return AGTP_fossil
    
    if LCIAindicator == "AGTP_bio":
        print(AGTP_bio)
        #if phase_C==False:
        dynamic_LCIA_b7_material_plot(LCIAindicator,AGTP_bio,cumulative,material)
        return AGTP_bio


def dynamic_LCIA_b7_plot(building_id, LCIAindicator, LCIAindicatorvalue, cumulative, name):
    if phase_C==False:
        waste_folder = "without_waste"
    if phase_C==True:
        waste_folder = "with_waste"
        
    plt.figure(figsize=(10, 5))
    ax = plt.subplot()
    ax.fill_between(LCIAindicatorvalue.index,LCIAindicatorvalue, alpha=0.07)
    ax.plot(LCIAindicatorvalue,label=LCIAindicator+" "+name+", "+cumulative, linewidth=0.8)
    plt.xlabel("Year",fontsize=18)
    
    if "AGWP" in LCIAindicator and cumulative=="non-cumulative":        
        plt.ylabel("Absolute Global Warming Potential \n (AGWP) [W m$^{-2}$]",fontsize=16)
    if "AGWP" in LCIAindicator and cumulative=="cumulative":        
        plt.ylabel("Absolute Global Warming Potential \n (AGWP) [W m$^{-2}$ yr]",fontsize=16)
    if "AGTP" in LCIAindicator:
        plt.ylabel("Absolute Global Temperature Potential \n (AGTP) [K]",fontsize=16)
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2,fontsize=15)
    ticks=np.arange(starting_time,starting_time+(len(LCIAindicatorvalue)-1)/10 + 1,10)
    plt.xticks(np.linspace(0, len(LCIAindicatorvalue), len(ticks)), ticks.astype(int))
    if level=="Building_Material":
        ticks=np.arange(0,(len(LCIAindicatorvalue)-1)/10 + 1,10)
        plt.xticks(np.linspace(0, len(LCIAindicatorvalue), len(ticks)), ticks.astype(int))
    plt.tick_params(labelsize=15)

    
    ax.spines["bottom"].set_linewidth(2)
    ax.spines[['right', 'top']].set_visible(False)
    
    ax.set_axisbelow(True)
    ax.grid(color='gray', linestyle='dashed', alpha=0.3)
    
    if phase_C:
     waste_folder = "with_waste"
    else:
     waste_folder = "without_waste"
    
    if "-" not in dynamic_factor:
        fn = PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_{cumulative}_{'_'.join(dynamic_factor)}_{dynamic_scenario}.pdf"  
        
    else:
        fn = PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_{cumulative}.pdf"    
        fn.parent.mkdir(parents=True, exist_ok=True)
    if not fn.exists():
        ax.figure.savefig(fn, bbox_inches="tight")
    
    if show_plots:
        plt.savefig(fn, bbox_inches="tight")
    else:
        plt.close()
    
    #export for further analyses
    if "-" not in dynamic_factor:
        filepath = Path(".")/PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_{cumulative}_{'_'.join(dynamic_factor)}_{dynamic_scenario}.parquet"
        if not filepath.exists():
            df_temp = pd.DataFrame({'value': LCIAindicatorvalue})
            df_temp.to_parquet(filepath, engine='pyarrow', compression='snappy')
    
    else:
        filepath = Path(".")/PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_{cumulative}.parquet"
        if not filepath.exists():
            df_temp = pd.DataFrame({'value': LCIAindicatorvalue})
            df_temp.to_parquet(filepath, engine='pyarrow', compression='snappy')
    
    
def dynamic_LCIA_b7_plot_subparts_in_part(building_id, collect, LCIAindicator, cumulative, name, waste): #input "collect" should be a list
    global PDF_CHART_DATA
    if phase_C==False:
        #waste_folder = "without waste/"
        waste_folder = "without_waste"
    if phase_C==True:
        #waste_folder = "with waste/"
        waste_folder = "with_waste"
        
    plt.figure(figsize=(10, 5))
    ax = plt.subplot()
        
    for i in range(len(collect)):
        subpart = collect[i][0]
        LCIAindicatorvalue = collect[i][1]
       
        #export for further analyses
        if "-" not in dynamic_factor:
            filepath = Path(".")/PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_{subpart.replace('/', '_').replace('<', '_').replace('>', '_').replace(':', '_').replace('|', '_').replace('?', '_').replace('*', '_')}_{cumulative}_{'_'.join(dynamic_factor)}_{dynamic_scenario}_{waste}.parquet"
            if not filepath.exists():
                df_temp = pd.DataFrame({'value': LCIAindicatorvalue})
                df_temp.to_parquet(filepath, engine='pyarrow', compression='snappy')
        else:
            filepath = Path(".")/PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_{subpart.replace('/', '_').replace('<', '_').replace('>', '_').replace(':', '_').replace('|', '_').replace('?', '_').replace('*', '_')}_{cumulative}.parquet"
            if not filepath.exists():
                df_temp = pd.DataFrame({'value': LCIAindicatorvalue})
                df_temp.to_parquet(filepath, engine='pyarrow', compression='snappy')
            
        ax.fill_between(LCIAindicatorvalue.index,LCIAindicatorvalue, alpha=0.07)
        ax.plot(LCIAindicatorvalue,label=LCIAindicator+" "+subpart+", "+cumulative, linewidth=0.8)
        plt.xlabel("Year",fontsize=16)
        
        if "AGWP" in LCIAindicator and cumulative=="non-cumulative": 
            plt.ylabel("Absolute Global Warming Potential \n (AGWP) [W m$^{-2}$]",fontsize=16)
        if "AGWP" in LCIAindicator and cumulative=="cumulative": 
            plt.ylabel("Absolute Global Warming Potential \n (AGWP) [W m$^{-2}$ yr]",fontsize=16)
        if "AGTP" in LCIAindicator:
            plt.ylabel("Absolute Global Temperature Potential \n (AGTP) [K]",fontsize=16)        
        
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2,fontsize=15)
    ticks=np.arange(starting_time,starting_time+(len(LCIAindicatorvalue)-1)/10 + 1,10)
    plt.xticks(np.linspace(0, len(LCIAindicatorvalue), len(ticks)), ticks.astype(int))
    if level=="Building_Material":
        ticks=np.arange(0,(len(LCIAindicatorvalue)-1)/10 + 1,10)
        plt.xticks(np.linspace(0, len(LCIAindicatorvalue), len(ticks)), ticks.astype(int))
    plt.tick_params(labelsize=15)
    
    ax.spines["bottom"].set_linewidth(2)
    ax.spines[['right', 'top']].set_visible(False)
    
    ax.set_axisbelow(True)
    ax.grid(color='gray', linestyle='dashed', alpha=0.3)
    
    if "-" not in dynamic_factor:
        fn = PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_subparts_{cumulative}_{'_'.join(dynamic_factor)}_{dynamic_scenario}_{waste}.pdf" #the waste here is for separately plotting production and waste in the case of considering circular waste treatment
    else:
        fn = PLOTS_DIR/waste_folder/f"{LCIAindicator}_{building_id}_{building_type}_{name}_subparts_{cumulative}.pdf"    
        fn.parent.mkdir(parents=True, exist_ok=True)
    if not fn.exists():
        ax.figure.savefig(fn, bbox_inches="tight")
    
    if show_plots:
        plt.savefig(fn, bbox_inches="tight")
    else:
        plt.close()   
    
def dynamic_LCIA_b7_waste_replacement_adjust(LCIAindicator, LCIAindicatorvalue, rsl, years, replace):
    indicator_material = LCIAindicatorvalue.copy()
    indicator_temp = pd.Series(0, range(0,rsl*10))
    indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
    waste=indicator_material[0:rsp*10+1]    
            
    return waste

#%%
def import_ratio_b1_stochastic(rate, initial_import, year_difference,
                                upper_outlier, lower_outlier,
                                upper_outlier_f, lower_outlier_f):
    """
    Draw ONE stochastic import-ratio trajectory.

    For each year in year_difference, independently samples the annual rate
    of change from {rate, upper_outlier, lower_outlier} with the given
    frequencies, and compounds it onto initial_import. Returns the final
    (clipped to [0, 1]) ratio as a single float.

    Outer Monte Carlo (running the whole LCIA pipeline N times to obtain a
    distribution of final temp values) is handled by uncertainty_merge.py,
    NOT here. Each call to this function returns one realization; the n_sim
    loop that used to live inside this function has been removed on
    purpose — its presence caused the caller to collapse draws to a median
    and hid all sampling variance from the outer wrapper loop.

    Parameters
    ----------
    rate:             normal annual rate of change (Amount)
    initial_import:   starting import ratio (1 - sum(Raw_Material))
    year_difference:  number of years to compound over
    upper_outlier:    upper-bound annual rate
    lower_outlier:    lower-bound annual rate
    upper_outlier_f:  upper-bound occurrence frequency (e.g. 0.05 = 1/20 yr)
    lower_outlier_f:  lower-bound occurrence frequency
    """
    # None/NaN guards
    if pd.isna(upper_outlier) or upper_outlier is None:
        upper_outlier = rate
    if pd.isna(lower_outlier) or lower_outlier is None:
        lower_outlier = rate
    if pd.isna(upper_outlier_f) or upper_outlier_f is None:
        upper_outlier_f = 0
    if pd.isna(lower_outlier_f) or lower_outlier_f is None:
        lower_outlier_f = 0

    upper_outlier = float(upper_outlier)
    lower_outlier = float(lower_outlier)
    upper_outlier_f = float(upper_outlier_f)
    lower_outlier_f = float(lower_outlier_f)

    p_normal = max(1.0 - upper_outlier_f - lower_outlier_f, 0)

    cumulative_factor = initial_import
    for _ in range(year_difference):
        annual_rate = np.random.choice(
            [rate, upper_outlier, lower_outlier],
            p=[p_normal, upper_outlier_f, lower_outlier_f],
        )
        cumulative_factor *= (1 + annual_rate)

    return max(0.0, min(1.0, cumulative_factor))


def change_percent_b2_calc(k,df_query_result_b, year_difference, original_material, original_component):
    
    change_percent = df_query_result_b.loc[k,"Amount_Specific"] * year_difference   
    reduction_reference = df_query_result_b.loc[k,"Reduction_Reference"] * year_difference  
    reduction_reference_waste = df_query_result_b.loc[k,"Reduction_Reference_Waste"] * year_difference  
    
    year_difference_reduction = 5000
    year_difference_reduction_waste = 5000
    
    reduction_in_material_max = df_query_result_b.loc[k,"Reduction_In_Material_Max"]
    
    #This one is currently not needed, because the distribution of the recycled part is proportionally accordingly to the partial %
    reduction_in_material_max_smaller = df_query_result_b.loc[k,"Reduction_In_Material_Max_Smaller"]
    
    reduction_in_waste_max = df_query_result_b.loc[k,"Waste_Reduction_Max"]
    
    
    if "B1" in dynamic_factor:
        for m in range(len(df_query_result_b1)):            
            if df_query_result_b1[m][2] == original_material and df_query_result_b1[m][1] == original_component: #THINK ABOUT IF AND HOW TO ADD CONSTRUCTION TYPE AS FILTER - solved

                dataframes = df_query_result_b1[m][3]
                filtered_indices = [
                    t for t in range(len(dataframes))
                    if not dataframes[t].empty and dataframes[t].loc[0, "Region_x"] in geography
                    ] 
                
                if filtered_indices:
                    selected_df = dataframes[filtered_indices[0]]
                    
                    #IT IS NOW BASED ON IMPORT, SO +, import is (1-local original)
                    #IT IS NOW SUM OF ALL REGIONAL
                    
                    temp = (1 + selected_df.loc[0, "Amount"]) ** year_difference * (1-selected_df["Raw_Material"].sum())
                    
                                        
                    if temp > 1:
                        temp = 1
                    if temp < 0:
                        temp=0
                        
                    temp_regional = 1-temp
                    
                    #The sum of the additional conversion factor times the new regional factor, we now have the new reduction max in material
                    reduction_in_material_max = temp_regional * df_query_result_b.loc[k,"Additional_Conversion_Factor"]
    
    #Check the individual stopping point in both production and waste
    if reduction_reference < (0-reduction_in_material_max): #100% reduction already
        year_difference_reduction = math.floor((0-reduction_in_material_max)/df_query_result_b.loc[k,"Reduction_Reference"])
        #get year difference first         
        
        #comparing both influence in production and reduction in waste. The earliest offset determines the stop point of the recycling ratio.
        if year_difference_reduction<=year_difference_reduction_waste:
            change_percent = df_query_result_b.loc[k,"Amount_Specific"] * year_difference_reduction
        else:
            change_percent = df_query_result_b.loc[k,"Amount_Specific"] * year_difference_reduction_waste 
    
    if reduction_reference_waste < (0-reduction_in_waste_max): #100% reduction already
        year_difference_reduction_waste= math.floor((0-reduction_in_waste_max)/df_query_result_b.loc[k,"Reduction_Reference_Waste"])
        #get year difference first     
        
        #comparing both influence in production and reduction in waste. The earliest offset determines the stop point of the recycling ratio.
        if year_difference_reduction<=year_difference_reduction_waste:
            change_percent = df_query_result_b.loc[k,"Amount_Specific"] * year_difference_reduction
        else:
            change_percent = df_query_result_b.loc[k,"Amount_Specific"] * year_difference_reduction_waste 
    
    
    #Check the partial stopping point using smaller (if the smaller one reaches 0, the other ones will have 100%)
    #This one is currently not needed, because the distribution of the recycled part is proportionally accordingly to the partial %
    
    
    return change_percent

def change_percent_b1_calc(k,d,df_query_result_b,temp,import_original):
    if df_query_result_b[k][3][d].loc[0,"Region_x"] not in geography: # if it is related to import
        
        #Since it is possible to have multiple import modules, a multiplication of ratio is important
        part_import = float(df_query_result_b[k][3][d].loc[0,"Raw_Material"]) / import_original
        
        change_percent = temp * part_import - float(df_query_result_b[k][3][d].loc[0,"Raw_Material"])
        
        if temp > 1: #if import is 100%
            change_percent = 1 * part_import -float(df_query_result_b[k][3][d].loc[0,"Raw_Material"])
        elif temp < 0: #if import is 0%
            change_percent = 0-float(df_query_result_b[k][3][d].loc[0,"Raw_Material"])      
    
    else: # this is related to local or regional production
    
        #Since it is possible to have multiple regional modules, a multiplication of ratio is important
        part_regional = float(df_query_result_b[k][3][d].loc[0,"Raw_Material"]) / (1-import_original)   
    
        change_percent = (1-temp) * part_regional -float(df_query_result_b[k][3][d].loc[0,"Raw_Material"])
        
        if temp > 1: #if import is 100%, should minus original rate of local production because it is now 0
            change_percent = 0-float(df_query_result_b[k][3][d].loc[0,"Raw_Material"])
        elif temp < 0: #if import is 0%, should add the corresponding rate of the import because it all belongs to local production
            change_percent = import_original * part_regional
    
    return change_percent

def separate_calculation_new_elementflow(current_dynamic_factor, LCIAindicator, df_query_result_b, year_difference, original_material, original_component, area, lower_influence, df_query_result_b_lower, df_query_result_b_lower2, df_query_result_b2):
    AGWP=pd.Series(0, range(0,years*10+1))
    AGWP_fossil=pd.Series(0, range(0,years*10+1))
    AGWP_bio=pd.Series(0, range(0,years*10+1))
    AGTP=pd.Series(0, range(0,years*10+1))
    AGTP_fossil=pd.Series(0, range(0,years*10+1))
    AGTP_bio=pd.Series(0, range(0,years*10+1))
    
    if current_dynamic_factor == "B2":
        for k in df_query_result_b.index:    
            if df_query_result_b.loc[k,"Building_Material"] == original_material and df_query_result_b.loc[k,"Building_Component"] == original_component: #THINK ABOUT IF AND HOW TO ADD CONSTRUCTION TYPE AS FILTER - solved
                
                density=df_query_result_b.loc[k,"Material_Density"]
                thickness=df_query_result_b.loc[k,"Material_Thickness"]                
                
                change_percent = change_percent_b2_calc(k,df_query_result_b, year_difference, original_material, original_component)

                unit_lookup = {
                    "m3": thickness,
                    "kg": density * thickness,
                    "m2": 1,
                    "metric ton*km": density * thickness
                    }
                unit = unit_lookup.get(df_query_result_b.loc[k,"Unit"], 1)                     
                
                elementamounts = ast.literal_eval(df_query_result_b.loc[k,"Element_Amount"])
                
                for key, amount in elementamounts.items():
                    elementamount = amount * change_percent
                    process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                          
                
    elif current_dynamic_factor == "B1":        
        for k in range(len(df_query_result_b)):            
            if df_query_result_b[k][2] == original_material and df_query_result_b[k][1] == original_component: #THINK ABOUT IF AND HOW TO ADD CONSTRUCTION TYPE AS FILTER - solved

                dataframes = df_query_result_b[k][3]
                filtered_indices = [
                    t for t in range(len(dataframes))
                    if not dataframes[t].empty and dataframes[t].loc[0, "Region_x"] in geography
                    ] 
                
                if filtered_indices:
                    selected_df = dataframes[filtered_indices[0]]

                    #IT IS NOW BASED ON IMPORT, SO +, import is (1-local original)
                    #IT IS NOW SUM OF ALL REGIONAL
                    
                    """
                    #CONSIDER UNCERTAINTY
                    rate = float(selected_df.loc[0, "Amount"])
                    import_original=(1-selected_df["Raw_Material"].sum())
                    
                    
                    # 从 df_query_result_b1_prep 中取上下界
                    upper_outlier = selected_df.loc[0, "Upper_Outlier"] if "Upper_Outlier" in selected_df.columns else None
                    lower_outlier = selected_df.loc[0, "Lower_Outlier"] if "Lower_Outlier" in selected_df.columns else None
                    upper_outlier_f = selected_df.loc[0, "Upper_Outlier_F"] if "Upper_Outlier_F" in selected_df.columns else None
                    lower_outlier_f = selected_df.loc[0, "Lower_Outlier_F"] if "Lower_Outlier_F" in selected_df.columns else None
                    
                    # Single stochastic draw; outer Monte Carlo is handled
                    # by uncertainty_merge.py (100 wrapper sims). We DO NOT
                    # median-collapse here — that would hide all sampling
                    # variance from the outer loop.
                    temp = import_ratio_b1_stochastic(
                        rate, import_original, year_difference,
                        upper_outlier, lower_outlier,
                        upper_outlier_f, lower_outlier_f,
                        )

                    """
                    #NOT CONSIDER UNCERTAINTY
                    temp = (1 + selected_df.loc[0, "Amount"]) ** year_difference * (1-selected_df["Raw_Material"].sum())
                    
                    import_original=(1-selected_df["Raw_Material"].sum())
                            
                for d in range(len(df_query_result_b[k][3])):
                    density=df_query_result_b[k][3][d].loc[0,"Material_Density"]
                    thickness=df_query_result_b[k][3][d].loc[0,"Material_Thickness"]                     
                    
                    change_percent = change_percent_b1_calc(k,d,df_query_result_b,temp,import_original)
                    
                    unit_lookup = {
                        "m3": thickness,
                        "kg": density * thickness,
                        "m2": 1,
                        "metric ton*km": density * thickness
                        }
                    unit = unit_lookup.get(df_query_result_b[k][3][d].loc[0,"Unit"], 1)
                            
                    elementamounts = ast.literal_eval(df_query_result_b[k][3][d].loc[0,"Element_Amount"])
                    
                    for key, amount in elementamounts.items():
                        elementamount = amount * change_percent
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)

                    
    elif (current_dynamic_factor == "B5" or current_dynamic_factor == "B4" or current_dynamic_factor == "B3") and not lower_influence:        
        
        if not any(len(sublist[3]) > 0 for sublist in df_query_result_b):
            # No changes needed, variables remain as they are
            
            AGWP=AGWP
            AGWP_fossil=AGWP_fossil
            AGWP_bio=AGWP_bio
            AGTP=AGTP
            AGTP_fossil=AGTP_fossil
            AGTP_bio=AGTP_bio
        else:
            # Pre-calculate exact_year outside the loop
            exact_year = min(starting_time + year_difference, 2060)
            
            if "power-2024" in dynamic_factor:
                exact_year = 2024
            
            # Main processing loop with more efficient structure
            for k in range(len(df_query_result_b)):
                item = df_query_result_b[k]
                
                # Skip iterations that don't match criteria or have no data
                if item[2] != original_material or item[1] != original_component or len(item[3]) <= 0:
                    continue
                
                #print(current_dynamic_factor+" :"+str(exact_year)+" "+original_material+original_component)
                
                power_mix = item[4][0]
                
                dynamic_ratio = item[4][2]
                dynamic_ratio = dynamic_ratio.loc[(dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                
                energy_source = item[4][1]
                dynamic_ratio_value = dynamic_ratio.loc[0,"Energy_Source_Percentage_Dynamic"] if not dynamic_ratio.empty else None
                
                # Process energy sources once
                for g in energy_source.index:
                    if dynamic_ratio_value is not None:
                        energy_source.loc[g,"Energy_Source_Percentage_Dynamic"] = dynamic_ratio_value
                    
                    if isinstance(energy_source.loc[g,"Power_Transmission_Network"], float):
                        energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Power_Transmission_Network"]
                    elif "sulfur hexafluoride, liquid" in energy_source.loc[g,"Name"]:
                        energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Energy_Source"]
                    else:
                        energysourcedynamics = ast.literal_eval(energy_source.loc[g,"Energy_Source_Percentage_Dynamic"])
                        for key in energysourcedynamics:
                            if energy_source.loc[g,"Name"] in key:
                                value = energysourcedynamics[key]
                                energy_source.loc[g,"Energy_Source_Percentage_Final"] = value if isinstance(value, (float, int)) else value[0]
                                break 
                        
                rawmaterials_or_waste = item[3]
                
                # Process each material in the lower voltage
                for raw_material in rawmaterials_or_waste:
                    waste_name = raw_material.loc[0,"Waste_Name"] #waste_name is only for condition and is the market
                    has_name2 = raw_material.loc[0,"Name2"]
                    
                    # Calculate change_percent based on material type
                    if waste_name is None:  # for material
                        if has_name2 is None:
                            ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Raw_Material"]
                            
                            rawmaterial_name = raw_material.loc[0,"Name"] #raw material (production)
                            
                        else:  # when having power mix group
                            ratios = (raw_material.loc[0,"Power_Mix_Percentage"] * 
                                     raw_material.loc[0,"Power_Mix_Group_Percentage_Raw_Material"] * 
                                     raw_material.loc[0,"Raw_Material"])
                            
                            rawmaterial_name = has_name2 #raw material (production)
                            
                        change_percent = 0 - ratios
                    else:  # for waste
                        if has_name2 is None:
                            ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Waste_Treatment"]
                            change_percent = 0 - ratios
                            
                            rawmaterial_name = raw_material.loc[0,"Name"] #waste treatment, waste_name was only for condition and is the market
                        #not included yet
                        #else: #when having power mix group
                        #    ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Power_Mix_Group_Percentage"] * raw_material.loc[0,"Waste_Treatment"]
                    
                    
                    # Get material properties
                    density = raw_material.loc[0,"Material_Density"]
                    thickness = raw_material.loc[0,"Material_Thickness"]
                    
                    # Calculate unit using dictionary lookup instead of if-else
                    unit_lookup = {
                        "m3": thickness,
                        "kg": density * thickness,
                        "m2": 1,
                        "metric ton*km": density * thickness
                    }
                    unit = unit_lookup.get(raw_material.loc[0,"Material_Unit"], 1)
                    
                    change_percent_b2 = 0
                    
                    if "B2" in dynamic_factor:
                        mask = ((df_query_result_b2["Building_Material"] == original_material) & 
                                (df_query_result_b2["Building_Component"] == original_component) &
                                (df_query_result_b2["Name"] == rawmaterial_name)) #raw material production or waste treatment
    
                        matching_indices = df_query_result_b2.index[mask]
    
                        if len(matching_indices) > 0:
                            m = matching_indices[0]  # Get the first (and presumably only) match
                            change_percent_b2 = change_percent_b2_calc(m, df_query_result_b2, year_difference, original_material, original_component)
                    
                    change_percent_b1 = 0
                    
                    if "B1" in dynamic_factor:
                        for n in range(len(df_query_result_b1)):  
                            if df_query_result_b1[n][2] == original_material and df_query_result_b1[n][1] == original_component:
                                dataframes = df_query_result_b1[n][3]
                                filtered_indices = [
                                    t for t in range(len(dataframes))
                                    if not dataframes[t].empty and dataframes[t].loc[0, "Region_x"] in geography
                                ]
                                
                                if filtered_indices:
                                    selected_df = dataframes[filtered_indices[0]]
                                    #IT IS NOW BASED ON IMPORT, SO +, import is (1-local original)
                                    #IT IS NOW SUM OF ALL REGIONAL
                                    temp = (1 + selected_df.loc[0,"Amount"]) ** year_difference * (1-selected_df["Raw_Material"].sum())
                                    
                                    import_original=(1-selected_df["Raw_Material"].sum())
                                     
                                            
                                for d in range(len(df_query_result_b1[n][3])):
                                    if df_query_result_b1[n][3][d].loc[0,"Name_x"] == rawmaterial_name: #raw material production or waste treatment
                                        change_percent_b1 = change_percent_b1_calc(n,d,df_query_result_b1,temp,import_original)
                                        break  # Exit inner loop after finding raw material match
                                
                                break  # Exit outer loop after finding main match
                    
                    
                    # Process current higher voltage power
                    elementamounts = ast.literal_eval(power_mix.loc[0,"Element_Amount_Power_Mix"])
                    
                    # Process each element in the current power
                    for key, amount in elementamounts.items():
                        elementamount = amount * change_percent * (1+change_percent_b2) * (1+change_percent_b1) #if B1 and or B2 are present, the change is no more upon the original amount, but the CHANGED amount of B1 and B2, thus (1+%)
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                    
                    # Add new higher voltage power
                    for p in energy_source.index:
                        new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                        percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                        
                        for key, amount in new_elementamounts.items():
                            elementamount = amount * ratios * percentage_final * (1+change_percent_b2) * (1+change_percent_b1) #if B1 and or B2 are present, the change is no more upon the original amount, but the CHANGED amount of B1 and B2, thus (1+%)
                            process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
        
                           
    elif current_dynamic_factor == "B4" and lower_influence == True:
        
        if not any(len(sublist[3]) > 0 for sublist in df_query_result_b_lower):
            # No changes needed, variables remain as they are
            AGWP=AGWP
            AGWP_fossil=AGWP_fossil
            AGWP_bio=AGWP_bio
            AGTP=AGTP
            AGTP_fossil=AGTP_fossil
            AGTP_bio=AGTP_bio
        else:
            
            # Calculate power transformation factor once
            power_transform_factor = medium_ratio_static.loc[0,"Power_Transformation"]
            
            # Pre-calculate exact_year outside the loop
            exact_year = min(starting_time + year_difference, 2060)
            
            if "power-2024" in dynamic_factor:
                exact_year = 2024
            
            # Prepare dynamic ratio once (outside the k loop)
            dynamic_ratio = df_query_result_b4_dynamic_ratio.loc[(df_query_result_b4_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
            
            # Process energy source preparation once (outside the k loop)
            energy_source = df_query_result_b4_energysource_amount.copy()
            dynamic_ratio_value = dynamic_ratio.loc[0,"Energy_Source_Percentage_Dynamic"] if not dynamic_ratio.empty else None
            
            # Process energy sources once
            for g in energy_source.index:
                if dynamic_ratio_value is not None:
                    energy_source.loc[g,"Energy_Source_Percentage_Dynamic"] = dynamic_ratio_value
                
                if isinstance(energy_source.loc[g,"Power_Transmission_Network"], float):
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Power_Transmission_Network"]
                elif "sulfur hexafluoride, liquid" in energy_source.loc[g,"Name"]:
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Energy_Source"]
                else:
                    energysourcedynamics = ast.literal_eval(energy_source.loc[g,"Energy_Source_Percentage_Dynamic"])
                    for key in energysourcedynamics:
                        if energy_source.loc[g,"Name"] in key:
                            value = energysourcedynamics[key]
                            energy_source.loc[g,"Energy_Source_Percentage_Final"] = value if isinstance(value, (float, int)) else value[0]
                            break           
            
            if "B5" in dynamic_factor:
                dynamic_ratio_b5 = df_query_result_b5_dynamic_ratio.loc[(df_query_result_b5_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                dynamic_ratio_value_b5 = ast.literal_eval(dynamic_ratio_b5.loc[0,"Energy_Source_Percentage_Dynamic"])
                
                matching_keys = [key for key in dynamic_ratio_value_b5 if "electricity voltage transformation from medium to low voltage" in key]
                if matching_keys:
                    power_transform_factor_new = dynamic_ratio_value_b5[matching_keys[0]]
                    power_transform_factor = power_transform_factor_new
            
            # Main processing loop with more efficient structure
            for k in range(len(df_query_result_b_lower)):
                item = df_query_result_b_lower[k]
                
                # Skip iterations that don't match criteria or have no data
                if item[2] != original_material or item[1] != original_component or len(item[3]) <= 0:
                    continue
                
                #print(current_dynamic_factor+" :"+str(exact_year)+" "+original_material+original_component)
                
                rawmaterials_or_waste = item[3]
                
                # Process each material in the lower voltage
                for raw_material in rawmaterials_or_waste:
                    waste_name = raw_material.loc[0,"Waste_Name"] #waste_name is only for condition and is the market
                    has_name2 = raw_material.loc[0,"Name2"]
                    
                    # Calculate change_percent based on material type
                    if waste_name is None:  # for material
                        if has_name2 is None:
                            ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Raw_Material"]
                            
                            rawmaterial_name = raw_material.loc[0,"Name"] #raw material (production)
                            
                        else:  # when having power mix group
                            ratios = (raw_material.loc[0,"Power_Mix_Percentage"] * 
                                     raw_material.loc[0,"Power_Mix_Group_Percentage_Raw_Material"] * 
                                     raw_material.loc[0,"Raw_Material"])
                            
                            rawmaterial_name = has_name2 #raw material (production)
                            
                        change_percent = 0 - ratios
                    else:  # for waste
                        if has_name2 is None:
                            ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Waste_Treatment"]
                            change_percent = 0 - ratios
                            
                            rawmaterial_name = raw_material.loc[0,"Name"] #waste treatment, waste_name was only for condition and is the market
                        #not included yet
                        #else: #when having power mix group
                        #    ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Power_Mix_Group_Percentage"] * raw_material.loc[0,"Waste_Treatment"]
                    
                    
                    # Get material properties
                    density = raw_material.loc[0,"Material_Density"]
                    thickness = raw_material.loc[0,"Material_Thickness"]
                    
                    # Calculate unit using dictionary lookup instead of if-else
                    unit_lookup = {
                        "m3": thickness,
                        "kg": density * thickness,
                        "m2": 1,
                        "metric ton*km": density * thickness
                    }
                    unit = unit_lookup.get(raw_material.loc[0,"Material_Unit"], 1)
                                        
                    change_percent_b2 = 0
                    
                    if "B2" in dynamic_factor:
                        mask = ((df_query_result_b2["Building_Material"] == original_material) & 
                                (df_query_result_b2["Building_Component"] == original_component) &
                                (df_query_result_b2["Name"] == rawmaterial_name)) #raw material production or waste treatment
    
                        matching_indices = df_query_result_b2.index[mask]
    
                        if len(matching_indices) > 0:
                            m = matching_indices[0]  # Get the first (and presumably only) match
                            change_percent_b2 = change_percent_b2_calc(m, df_query_result_b2, year_difference, original_material, original_component)
                    
                    change_percent_b1 = 0
                    
                    if "B1" in dynamic_factor:
                        for n in range(len(df_query_result_b1)):  
                            if df_query_result_b1[n][2] == original_material and df_query_result_b1[n][1] == original_component:
                                dataframes = df_query_result_b1[n][3]
                                filtered_indices = [
                                    t for t in range(len(dataframes))
                                    if not dataframes[t].empty and dataframes[t].loc[0, "Region_x"] in geography
                                ]
                                
                                if filtered_indices:
                                    selected_df = dataframes[filtered_indices[0]]
                                    #IT IS NOW BASED ON IMPORT, SO +, import is (1-local original)
                                    #IT IS NOW SUM OF ALL REGIONAL
                                    temp = (1 + selected_df.loc[0,"Amount"]) ** year_difference * (1-selected_df["Raw_Material"].sum())
                                    
                                    import_original=(1-selected_df["Raw_Material"].sum())
                                     
                                            
                                for d in range(len(df_query_result_b1[n][3])):
                                    if df_query_result_b1[n][3][d].loc[0,"Name_x"] == rawmaterial_name: #raw material production or waste treatment
                                        change_percent_b1 = change_percent_b1_calc(n,d,df_query_result_b1,temp,import_original)
                                        break  # Exit inner loop after finding raw material match
                                
                                break  # Exit outer loop after finding main match
                                
                    # Process current higher voltage power
                    elementamounts = ast.literal_eval(medium_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                    
                    # Process each element in the current power
                    for key, amount in elementamounts.items():
                        elementamount = amount * change_percent * power_transform_factor * (1+change_percent_b2) * (1+change_percent_b1)
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                        
                    # Add new higher voltage power
                    for p in energy_source.index:
                        new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                        percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]

                        for key, amount in new_elementamounts.items():
                            elementamount = amount * ratios * percentage_final * power_transform_factor * (1+change_percent_b2) * (1+change_percent_b1)
                            process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
        
    elif current_dynamic_factor == "B3" and lower_influence == True:
        
        if not any(len(sublist[3]) > 0 for sublist in df_query_result_b_lower):
            # No changes needed, variables remain as they are
            AGWP=AGWP
            AGWP_fossil=AGWP_fossil
            AGWP_bio=AGWP_bio
            AGTP=AGTP
            AGTP_fossil=AGTP_fossil
            AGTP_bio=AGTP_bio
        else:
            # Calculate power transformation factor once
            power_transform_factor = high_ratio_static.loc[0,"Power_Transformation"]
            
            # Pre-calculate exact_year outside the loop
            exact_year = min(starting_time + year_difference, 2060)
            
            if "power-2024" in dynamic_factor:
                exact_year = 2024
            
            # Prepare dynamic ratio once (outside the k loop)
            dynamic_ratio = df_query_result_b3_dynamic_ratio.loc[(df_query_result_b3_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
            
            # Process energy source preparation once (outside the k loop)
            energy_source = df_query_result_b3_energysource_amount.copy()
            dynamic_ratio_value = dynamic_ratio.loc[0,"Energy_Source_Percentage_Dynamic"] if not dynamic_ratio.empty else None
            
            # Process energy sources once
            for g in energy_source.index:
                if dynamic_ratio_value is not None:
                    energy_source.loc[g,"Energy_Source_Percentage_Dynamic"] = dynamic_ratio_value
                
                if isinstance(energy_source.loc[g,"Power_Transmission_Network"], float):
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Power_Transmission_Network"]
                elif "sulfur hexafluoride, liquid" in energy_source.loc[g,"Name"]:
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Energy_Source"]
                else:
                    energysourcedynamics = ast.literal_eval(energy_source.loc[g,"Energy_Source_Percentage_Dynamic"])
                    for key in energysourcedynamics:
                        if energy_source.loc[g,"Name"] in key:
                            value = energysourcedynamics[key]
                            energy_source.loc[g,"Energy_Source_Percentage_Final"] = value if isinstance(value, (float, int)) else value[0]
                            break           
            
            if "B4" in dynamic_factor:
                dynamic_ratio_b4 = df_query_result_b4_dynamic_ratio.loc[(df_query_result_b4_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                dynamic_ratio_value_b4 = ast.literal_eval(dynamic_ratio_b4.loc[0,"Energy_Source_Percentage_Dynamic"])
                
                matching_keys = [key for key in dynamic_ratio_value_b4 if "electricity voltage transformation from medium to low voltage" in key]
                if matching_keys:
                    power_transform_factor_new = dynamic_ratio_value_b4[matching_keys[0]]
                    power_transform_factor = power_transform_factor_new
            
            # Main processing loop with more efficient structure
            for k in range(len(df_query_result_b_lower)):
                item = df_query_result_b_lower[k]
                
                # Skip iterations that don't match criteria or have no data
                if item[2] != original_material or item[1] != original_component or len(item[3]) <= 0:
                    continue
                    
                rawmaterials_or_waste = item[3]
                
                # Process each material in the lower voltage
                for raw_material in rawmaterials_or_waste:
                    waste_name = raw_material.loc[0,"Waste_Name"] #waste_name is only for condition and is the market
                    has_name2 = raw_material.loc[0,"Name2"]
                    
                    # Calculate change_percent based on material type
                    if waste_name is None:  # for material
                        if has_name2 is None:
                            ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Raw_Material"]
                            
                            rawmaterial_name = raw_material.loc[0,"Name"] #raw material (production)
                            
                        else:  # when having power mix group
                            ratios = (raw_material.loc[0,"Power_Mix_Percentage"] * 
                                     raw_material.loc[0,"Power_Mix_Group_Percentage_Raw_Material"] * 
                                     raw_material.loc[0,"Raw_Material"])
                            
                            rawmaterial_name = has_name2 #raw material (production)
                            
                        change_percent = 0 - ratios
                    else:  # for waste
                        if has_name2 is None:
                            ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Waste_Treatment"]
                            change_percent = 0 - ratios
                            
                            rawmaterial_name = raw_material.loc[0,"Name"] #waste treatment, waste_name was only for condition and is the market
                        #not included yet
                        #else: #when having power mix group
                        #    ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Power_Mix_Group_Percentage"] * raw_material.loc[0,"Waste_Treatment"]
                    
                    
                    # Get material properties
                    density = raw_material.loc[0,"Material_Density"]
                    thickness = raw_material.loc[0,"Material_Thickness"]
                    
                    # Calculate unit using dictionary lookup instead of if-else
                    unit_lookup = {
                        "m3": thickness,
                        "kg": density * thickness,
                        "m2": 1,
                        "metric ton*km": density * thickness
                    }
                    unit = unit_lookup.get(raw_material.loc[0,"Material_Unit"], 1)
                    
                    change_percent_b2 = 0
                    
                    if "B2" in dynamic_factor:
                        mask = ((df_query_result_b2["Building_Material"] == original_material) & 
                                (df_query_result_b2["Building_Component"] == original_component) &
                                (df_query_result_b2["Name"] == rawmaterial_name)) #raw material production or waste treatment
    
                        matching_indices = df_query_result_b2.index[mask]
    
                        if len(matching_indices) > 0:
                            m = matching_indices[0]  # Get the first (and presumably only) match
                            change_percent_b2 = change_percent_b2_calc(m, df_query_result_b2, year_difference, original_material, original_component)
                    
                    change_percent_b1 = 0
                    
                    if "B1" in dynamic_factor:
                        for n in range(len(df_query_result_b1)):  
                            if df_query_result_b1[n][2] == original_material and df_query_result_b1[n][1] == original_component:
                                dataframes = df_query_result_b1[n][3]
                                filtered_indices = [
                                    t for t in range(len(dataframes))
                                    if not dataframes[t].empty and dataframes[t].loc[0, "Region_x"] in geography
                                ]
                                
                                if filtered_indices:
                                    selected_df = dataframes[filtered_indices[0]]
                                    #IT IS NOW BASED ON IMPORT, SO +, import is (1-local original)
                                    #IT IS NOW SUM OF ALL REGIONAL
                                    temp = (1 + selected_df.loc[0,"Amount"]) ** year_difference * (1-selected_df["Raw_Material"].sum())
                                    
                                    import_original=(1-selected_df["Raw_Material"].sum())
                                     
                                            
                                for d in range(len(df_query_result_b1[n][3])):
                                    if df_query_result_b1[n][3][d].loc[0,"Name_x"] == rawmaterial_name: #raw material production or waste treatment
                                        change_percent_b1 = change_percent_b1_calc(n,d,df_query_result_b1,temp,import_original)
                                        break  # Exit inner loop after finding raw material match
                                
                                break  # Exit outer loop after finding main match
                                
                    # Process current higher voltage power
                    elementamounts = ast.literal_eval(high_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                    
                    # Process each element in the current power
                    for key, amount in elementamounts.items():
                        elementamount = amount * change_percent * power_transform_factor * (1+change_percent_b2) * (1+change_percent_b1)
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                    
                    # Add new higher voltage power
                    for p in energy_source.index:
                        new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                        percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                        
                        for key, amount in new_elementamounts.items():
                            elementamount = amount * ratios * percentage_final * power_transform_factor * (1+change_percent_b2) * (1+change_percent_b1)
                            process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
        
        
        if not any(len(sublist[3]) > 0 for sublist in df_query_result_b_lower2):
            # No changes needed, variables remain as they are
            AGWP=AGWP
            AGWP_fossil=AGWP_fossil
            AGWP_bio=AGWP_bio
            AGTP=AGTP
            AGTP_fossil=AGTP_fossil
            AGTP_bio=AGTP_bio
        else:
            # Calculate power transformation factor once
            power_transform_factor = high_ratio_static.loc[0,"Power_Transformation"] * medium_ratio_static.loc[0,"Power_Transformation"]
            
            # Pre-calculate exact_year outside the loop
            exact_year = min(starting_time + year_difference, 2060)
            
            if "power-2024" in dynamic_factor:
                exact_year = 2024
            
            # Prepare dynamic ratio once (outside the k loop)
            dynamic_ratio = df_query_result_b3_dynamic_ratio.loc[(df_query_result_b3_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
            
            # Process energy source preparation once (outside the k loop)
            energy_source = df_query_result_b3_energysource_amount.copy()
            dynamic_ratio_value = dynamic_ratio.loc[0,"Energy_Source_Percentage_Dynamic"] if not dynamic_ratio.empty else None
            
            # Process energy sources once
            for g in energy_source.index:
                if dynamic_ratio_value is not None:
                    energy_source.loc[g,"Energy_Source_Percentage_Dynamic"] = dynamic_ratio_value
                
                if isinstance(energy_source.loc[g,"Power_Transmission_Network"], float):
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Power_Transmission_Network"]
                elif "sulfur hexafluoride, liquid" in energy_source.loc[g,"Name"]:
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Energy_Source"]
                else:
                    energysourcedynamics = ast.literal_eval(energy_source.loc[g,"Energy_Source_Percentage_Dynamic"])
                    for key in energysourcedynamics:
                        if energy_source.loc[g,"Name"] in key:
                            value = energysourcedynamics[key]
                            energy_source.loc[g,"Energy_Source_Percentage_Final"] = value if isinstance(value, (float, int)) else value[0]
                            break           
            
            if "B5" in dynamic_factor:
                dynamic_ratio_b5 = df_query_result_b5_dynamic_ratio.loc[(df_query_result_b5_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                dynamic_ratio_value_b5 = ast.literal_eval(dynamic_ratio_b5.loc[0,"Energy_Source_Percentage_Dynamic"])
                
                matching_keys = [key for key in dynamic_ratio_value_b5 if "electricity voltage transformation from medium to low voltage" in key]
                if matching_keys:
                    power_transform_factor_new_b5 = dynamic_ratio_value_b5[matching_keys[0]]
                    power_transform_factor = high_ratio_static.loc[0,"Power_Transformation"]*power_transform_factor_new_b5
            
            if "B4" in dynamic_factor:
                dynamic_ratio_b4 = df_query_result_b4_dynamic_ratio.loc[(df_query_result_b4_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                dynamic_ratio_value_b4 = ast.literal_eval(dynamic_ratio_b4.loc[0,"Energy_Source_Percentage_Dynamic"])
                
                matching_keys = [key for key in dynamic_ratio_value_b4 if "electricity voltage transformation from medium to low voltage" in key]
                if matching_keys:
                    power_transform_factor_new_b4 = dynamic_ratio_value_b4[matching_keys[0]]
                    power_transform_factor = power_transform_factor_new_b5 * power_transform_factor_new_b4
            
            # Main processing loop with more efficient structure
            for k in range(len(df_query_result_b_lower2)):
                item = df_query_result_b_lower2[k]
                
                # Skip iterations that don't match criteria or have no data
                if item[2] != original_material or item[1] != original_component or len(item[3]) <= 0:
                    continue
                    
                rawmaterials_or_waste = item[3]
                
                # Process each material in the lower voltage
                for raw_material in rawmaterials_or_waste:
                    waste_name = raw_material.loc[0,"Waste_Name"] #waste_name is only for condition and is the market
                    has_name2 = raw_material.loc[0,"Name2"]
                    
                    # Calculate change_percent based on material type
                    if waste_name is None:  # for material
                        if has_name2 is None:
                            ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Raw_Material"]
                            
                            rawmaterial_name = raw_material.loc[0,"Name"] #raw material (production)
                            
                        else:  # when having power mix group
                            ratios = (raw_material.loc[0,"Power_Mix_Percentage"] * 
                                     raw_material.loc[0,"Power_Mix_Group_Percentage_Raw_Material"] * 
                                     raw_material.loc[0,"Raw_Material"])
                            
                            rawmaterial_name = has_name2 #raw material (production)
                            
                        change_percent = 0 - ratios
                    else:  # for waste
                        if has_name2 is None:
                            ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Waste_Treatment"]
                            change_percent = 0 - ratios
                            
                            rawmaterial_name = raw_material.loc[0,"Name"] #waste treatment, waste_name was only for condition and is the market
                        #not included yet
                        #else: #when having power mix group
                        #    ratios = raw_material.loc[0,"Power_Mix_Percentage"] * raw_material.loc[0,"Power_Mix_Group_Percentage"] * raw_material.loc[0,"Waste_Treatment"]
                    
                    
                    # Get material properties
                    density = raw_material.loc[0,"Material_Density"]
                    thickness = raw_material.loc[0,"Material_Thickness"]
                    
                    # Calculate unit using dictionary lookup instead of if-else
                    unit_lookup = {
                        "m3": thickness,
                        "kg": density * thickness,
                        "m2": 1,
                        "metric ton*km": density * thickness
                    }
                    unit = unit_lookup.get(raw_material.loc[0,"Material_Unit"], 1)
                    
                    change_percent_b2 = 0
                    
                    if "B2" in dynamic_factor:
                        mask = ((df_query_result_b2["Building_Material"] == original_material) & 
                                (df_query_result_b2["Building_Component"] == original_component) &
                                (df_query_result_b2["Name"] == rawmaterial_name)) #raw material production or waste treatment
    
                        matching_indices = df_query_result_b2.index[mask]
    
                        if len(matching_indices) > 0:
                            m = matching_indices[0]  # Get the first (and presumably only) match
                            change_percent_b2 = change_percent_b2_calc(m, df_query_result_b2, year_difference, original_material, original_component)
                    
                    change_percent_b1 = 0
                    
                    if "B1" in dynamic_factor:
                        for n in range(len(df_query_result_b1)):  
                            if df_query_result_b1[n][2] == original_material and df_query_result_b1[n][1] == original_component:
                                dataframes = df_query_result_b1[n][3]
                                filtered_indices = [
                                    t for t in range(len(dataframes))
                                    if not dataframes[t].empty and dataframes[t].loc[0, "Region_x"] in geography
                                ]
                                
                                if filtered_indices:
                                    selected_df = dataframes[filtered_indices[0]]
                                    #IT IS NOW BASED ON IMPORT, SO +, import is (1-local original)
                                    #IT IS NOW SUM OF ALL REGIONAL
                                    temp = (1 + selected_df.loc[0,"Amount"]) ** year_difference * (1-selected_df["Raw_Material"].sum())
                                    
                                    import_original=(1-selected_df["Raw_Material"].sum())
                                     
                                            
                                for d in range(len(df_query_result_b1[n][3])):
                                    if df_query_result_b1[n][3][d].loc[0,"Name_x"] == rawmaterial_name: #raw material production or waste treatment
                                        change_percent_b1 = change_percent_b1_calc(n,d,df_query_result_b1,temp,import_original)
                                        break  # Exit inner loop after finding raw material match
                                
                                break  # Exit outer loop after finding main match
                           
                    # Process current higher voltage power
                    elementamounts = ast.literal_eval(high_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                    
                    # Process each element in the current power
                    for key, amount in elementamounts.items():
                        elementamount = amount * change_percent * power_transform_factor * (1+change_percent_b2) * (1+change_percent_b1)
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                    
                    # Add new higher voltage power
                    for p in energy_source.index:
                        new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                        percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                        
                        for key, amount in new_elementamounts.items():
                            elementamount = amount * ratios * percentage_final * power_transform_factor * (1+change_percent_b2) * (1+change_percent_b1)
                            process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)        
        
    indicators = {
        "AGWP": AGWP,
        "AGWP_fossil": AGWP_fossil,
        "AGWP_bio": AGWP_bio,
        "AGTP": AGTP,
        "AGTP_fossil": AGTP_fossil,
        "AGTP_bio": AGTP_bio
    }
    return indicators.get(LCIAindicator)   
    
#test=separate_calculation_new_elementflow("AGWP",df_query_result_b2_influence, 30,"concrete, 25MPa, reinforced concrete","FLmas_1",1, False, None, None)

#%%  

def dynamic_LCIA_b7_replacement(LCIAindicator, LCIAindicatorvalue, rsl, years, replace, waste, material, component, area):
    
    #STATIC COMPARISON
    if static_comparison:
        gwp = 0
    #STATIC COMPARISON    
    
    if "-" not in dynamic_factor:
            
        if waste == "waste":
            
            for j in range(math.floor(rsp/rsl)): #because the first time implement is already considered above, starting from here is just the replacement
             
                LCIAindicatorvalue_difference = 0
                
                if "B5" in dynamic_factor or "power-2024" in dynamic_factor: 
                    
                    #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                    LCIAindicatorvalue_difference_b5=separate_calculation_new_elementflow("B5", LCIAindicator, df_query_result_b5_final_waste, rsl*(j+1), material, component, area, False, None, None, df_query_result_b2_further)

                    #so that the difference LCIAindicator also first starts when replacement is needed (blank place holder always with waste to represent the offset)
                    LCIAindicatorvalue_difference_b5 = dynamic_LCIA_b7_waste_replacement_adjust(LCIAindicator, LCIAindicatorvalue_difference_b5, rsl, years, LCIAindicatorvalue_difference_b5)
                    
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b5
                   
                if "B4" in dynamic_factor or "power-2024" in dynamic_factor:     
                    #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                    LCIAindicatorvalue_difference_b4=separate_calculation_new_elementflow("B4", LCIAindicator, df_query_result_b4_final_waste, rsl*(j+1), material, component, area, False, None, None, df_query_result_b2_further)
                    
                    #repeat the process for the lower voltage
                    LCIAindicatorvalue_difference_b4_low=separate_calculation_new_elementflow("B4", LCIAindicator, df_query_result_b4_final_waste, rsl*(j+1), material, component, area, True, df_query_result_b5_final_waste, None, df_query_result_b2_further)
                    
                    #so that the difference LCIAindicator also first starts when replacement is needed (blank place holder always with waste to represent the offset)
                    LCIAindicatorvalue_difference_b4 = dynamic_LCIA_b7_waste_replacement_adjust(LCIAindicator, LCIAindicatorvalue_difference_b4, rsl, years, LCIAindicatorvalue_difference_b4)
                    #repeat the process for the lower voltage
                    LCIAindicatorvalue_difference_b4_low = dynamic_LCIA_b7_waste_replacement_adjust(LCIAindicator, LCIAindicatorvalue_difference_b4_low, rsl, years, LCIAindicatorvalue_difference_b4_low)
                    
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b4 + LCIAindicatorvalue_difference_b4_low
                    
                    #exclude influences
                    #LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b4
                    
                if "B3" in dynamic_factor or "power-2024" in dynamic_factor: 
                    LCIAindicatorvalue_difference_b3=separate_calculation_new_elementflow("B3", LCIAindicator, df_query_result_b3_final_waste, rsl*(j+1), material, component, area, False, None, None, df_query_result_b2_further)            
                    
                    #repeat the process for the lower voltage
                    LCIAindicatorvalue_difference_b3_low=separate_calculation_new_elementflow("B3", LCIAindicator, df_query_result_b3_final_waste, rsl*(j+1), material, component, area, True, df_query_result_b4_final_waste, df_query_result_b5_final_waste, df_query_result_b2_further)
                    
                    #so that the difference LCIAindicator also first starts when replacement is needed (blank place holder always with waste to represent the offset)
                    LCIAindicatorvalue_difference_b3 = dynamic_LCIA_b7_waste_replacement_adjust(LCIAindicator, LCIAindicatorvalue_difference_b3, rsl, years, LCIAindicatorvalue_difference_b3)
                    #repeat the process for the lower voltage
                    LCIAindicatorvalue_difference_b3_low = dynamic_LCIA_b7_waste_replacement_adjust(LCIAindicator, LCIAindicatorvalue_difference_b3_low, rsl, years, LCIAindicatorvalue_difference_b3_low)
                    
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b3 + LCIAindicatorvalue_difference_b3_low
                    #LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b3
                
                if "B2" in dynamic_factor:
                    #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                    LCIAindicatorvalue_difference_b2=separate_calculation_new_elementflow("B2", LCIAindicator, df_query_result_b2_further, rsl*(j+1), material, component, area, False, None, None, None)
                    
                    #so that the difference LCIAindicator also first starts when replacement is needed (blank place holder always with waste to represent the offset)
                    LCIAindicatorvalue_difference_b2 = dynamic_LCIA_b7_waste_replacement_adjust(LCIAindicator, LCIAindicatorvalue_difference_b2, rsl, years, LCIAindicatorvalue_difference_b2)
                    
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b2                
                
                if "B1" in dynamic_factor: #for waste not relevant! the same as the original one
                    LCIAindicatorvalue_difference = LCIAindicatorvalue_difference

                
                #STATIC COMPARISON
                if static_comparison: #here the same as the code in waste treatment below
                    if j == 0:
                        #the waste at the time of replacement should be replaced by the new value
                        indicator_material = LCIAindicatorvalue + LCIAindicatorvalue_difference
                        
                        #GWP of the passed LCIAindicatorvalue
                        gwp = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-rsl)*10,"AGWP_co2"]
                    
                    elif j < math.floor(rsp/rsl)-1 and j != 0:
                        indicator_material = LCIAindicatorvalue + LCIAindicatorvalue_difference
                        indicator_temp = pd.Series(0, range(0,rsl*(j)*10))
                        indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)  
                        
                        indicator_material_1 = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-rsl*(j+1))*10,"AGWP_co2"]
                        
                        print(indicator_material_1)
                        gwp += indicator_material_1
                        
                        
                        if j == math.floor(rsp/rsl)-2 and rsp - math.floor(rsp/rsl) * rsl > 0:
                            #adding the calculation in the math.floor(rsp/rsl) order extra
                            
                            indicator_material = LCIAindicatorvalue + LCIAindicatorvalue_difference
                            indicator_temp = pd.Series(0, range(0,rsl*(math.floor(rsp/rsl)-1)*10))
                            indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                            
                            indicator_material_2 = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-math.floor(rsp/rsl)*rsl)*10,"AGWP_co2"]
                            gwp += indicator_material_2
                    
                #STATIC COMPARISON
                                   
                else:
                
                    if j == 0:
                        
                        #the waste at the time of replacement should be replaced by the new value
                        replace = LCIAindicatorvalue + LCIAindicatorvalue_difference
                    
                    else:
                        #calculate the new LCIAindicatorvalue: original LCIAindicatorvalue + (- represented as negative) difference LCIAindicatorvalue
                        indicator_material = LCIAindicatorvalue + LCIAindicatorvalue_difference
                        
                        indicator_temp = pd.Series(0, range(0,rsl*(j)*10)) #because one blank place holder is already included in waste, so j instead of j+1
                        indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                        replace = pd.concat([replace,indicator_material],axis=1)
                        replace[np.isnan(replace)]=0
                        replace=replace.sum(axis=1, numeric_only=True)[0:rsp*10+1]

        else: #for production relevant
        
            for j in range(math.floor(rsp/rsl)): #because the first time implement is already considered above, starting from here is just the replacement
        
                LCIAindicatorvalue_difference = 0
                
                if "B5" in dynamic_factor or "power-2024" in dynamic_factor: 
                    #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                    LCIAindicatorvalue_difference_b5=separate_calculation_new_elementflow("B5", LCIAindicator, df_query_result_b5_final_material, rsl*(j+1), material, component, area, False, None, None, df_query_result_b2_influence)
                    
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b5
                    
                if "B4" in dynamic_factor or "power-2024" in dynamic_factor:     
                    #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                    LCIAindicatorvalue_difference_b4=separate_calculation_new_elementflow("B4", LCIAindicator, df_query_result_b4_final_material, rsl*(j+1), material, component, area, False, None, None, df_query_result_b2_influence)
                    
                    #repeat the process for the lower voltage
                    LCIAindicatorvalue_difference_b4_low=separate_calculation_new_elementflow("B4", LCIAindicator, df_query_result_b4_final_material, rsl*(j+1), material, component, area, True, df_query_result_b5_final_material, None, df_query_result_b2_influence)
                                        
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b4 + LCIAindicatorvalue_difference_b4_low
                    
                    #exclude influences
                    #LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b4
            
                if "B3" in dynamic_factor or "power-2024" in dynamic_factor: 
                    #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                    LCIAindicatorvalue_difference_b3=separate_calculation_new_elementflow("B3", LCIAindicator, df_query_result_b3_final_material, rsl*(j+1), material, component, area, False, None, None, df_query_result_b2_influence)
                    
                    #repeat the process for the lower voltage
                    LCIAindicatorvalue_difference_b3_low=separate_calculation_new_elementflow("B3", LCIAindicator, df_query_result_b3_final_material, rsl*(j+1), material, component, area, True, df_query_result_b4_final_material, df_query_result_b5_final_material, df_query_result_b2_influence)
                    
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b3 + LCIAindicatorvalue_difference_b3_low
                    #LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b3
                    
                if "B2" in dynamic_factor:
                    #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                    LCIAindicatorvalue_difference_b2=separate_calculation_new_elementflow("B2", LCIAindicator, df_query_result_b2_influence, rsl*(j+1), material, component, area, False, None, None, None)
                    
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b2
                                    
                if "B1" in dynamic_factor: #for production relevant
                    #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                    LCIAindicatorvalue_difference_b1=separate_calculation_new_elementflow("B1", LCIAindicator, df_query_result_b1, rsl*(j+1), material, component, area, False, None, None, None)
                    
                    LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b1
                
                #STATIC COMPARISON
                if static_comparison:
                    if j == 0:
                        #GWP of the passed LCIAindicatorvalue
                        gwp = LCIAindicatorvalue[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years)*10,"AGWP_co2"]
                    
                    else:
                        indicator_material = LCIAindicatorvalue + LCIAindicatorvalue_difference
                        indicator_temp = pd.Series(0, range(0,rsl*(j)*10))
                        indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)  
                        
                        indicator_material_1 = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-rsl*j)*10,"AGWP_co2"]
                        
                        print(indicator_material_1)
                        gwp += indicator_material_1
                        
                        
                        if j == math.floor(rsp/rsl)-1 and rsp - math.floor(rsp/rsl) * rsl > 0: 
                            #adding the calculation in the math.floor(rsp/rsl) order extra
                            
                            indicator_material = LCIAindicatorvalue + LCIAindicatorvalue_difference
                            indicator_temp = pd.Series(0, range(0,rsl*math.floor(rsp/rsl)*10))
                            indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                            
                            indicator_material_2 = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-math.floor(rsp/rsl)*rsl)*10,"AGWP_co2"]
                            gwp += indicator_material_2
                    
                #STATIC COMPARISON
                
                else:
                    
                    #calculate the new LCIAindicatorvalue: original LCIAindicatorvalue + (- represented as negative) difference LCIAindicatorvalue
                    indicator_material = LCIAindicatorvalue + LCIAindicatorvalue_difference
                    
                    indicator_temp = pd.Series(0, range(0,rsl*(j+1)*10))
                    indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                    
                    replace = pd.concat([replace,indicator_material],axis=1)
                    replace[np.isnan(replace)]=0
                    replace=replace.sum(axis=1, numeric_only=True)[0:rsp*10+1]             
                        
    else:            
        
        #STATIC COMPARISON
        if static_comparison:
            
            if waste != "waste": 
                print(LCIAindicatorvalue)
                #then doing the replacements
                for j in range(math.floor(rsp/rsl)):
                    if j == 0:
                        #GWP of the passed LCIAindicatorvalue
                        gwp = LCIAindicatorvalue[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years)*10,"AGWP_co2"]
                        
                        #print(gwp)
                    
                    else:
                        indicator_material = LCIAindicatorvalue.copy()
                        indicator_temp = pd.Series(0, range(0,rsl*(j)*10))
                        indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)  
                        
                        indicator_material_1 = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-rsl*j)*10,"AGWP_co2"]
                        
                        print(indicator_material_1)
                        gwp += indicator_material_1
                                       
                if rsp - math.floor(rsp/rsl) * rsl > 0:
                    
                    indicator_material = LCIAindicatorvalue.copy()
                    indicator_temp = pd.Series(0, range(0,rsl*math.floor(rsp/rsl)*10))
                    indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                    
                    indicator_material_2 = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-math.floor(rsp/rsl)*rsl)*10,"AGWP_co2"]
                    gwp += indicator_material_2
                                
                    
            if waste == "waste":
                #then doing the replacements
                
                for j in range(math.floor(rsp/rsl)):
                    if j == 0:
                        #GWP of the passed LCIAindicatorvalue
                        gwp = LCIAindicatorvalue[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-rsl)*10,"AGWP_co2"]
                        
                        #print(gwp)
                    
                    elif j < math.floor(rsp/rsl)-1 and j != 0:
                    #else:
                        indicator_material = LCIAindicatorvalue.copy()
                        indicator_temp = pd.Series(0, range(0,rsl*(j)*10))
                        indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)  
                        
                        indicator_material_1 = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-rsl*(j+1))*10,"AGWP_co2"]
                        
                        print(indicator_material_1)
                        gwp += indicator_material_1
                                       
                if rsp - math.floor(rsp/rsl) * rsl > 0:
                    
                    indicator_material = LCIAindicatorvalue.copy()
                    indicator_temp = pd.Series(0, range(0,rsl*(math.floor(rsp/rsl)-1)*10))
                    indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                    
                    indicator_material_2 = indicator_material[years*10] /df_dynamicfactor_b7_dagwp_co2.loc[(years-math.floor(rsp/rsl)*rsl)*10,"AGWP_co2"]
                    gwp += indicator_material_2

                
        #STATIC COMPARISON

        
        else:
            for j in range(math.floor(rsp/rsl)): #because the first time implement is already considered above, starting from here is just the replacement

                indicator_material = LCIAindicatorvalue.copy()
                indicator_temp = pd.Series(0, range(0,rsl*(j+1)*10))
                indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                
                replace = pd.concat([replace,indicator_material],axis=1)
                replace[np.isnan(replace)]=0
                replace=replace.sum(axis=1, numeric_only=True)[0:rsp*10+1]
                
    
    #STATIC COMPARISON
    if static_comparison:
        return gwp
    #STATIC COMPARISON
    else:
        return replace    


def dynamic_LCIA_b7_component (building_id, df_query_result_calc_required, LCIAindicator, years, cumulative,area,waste, component):
    # Initialize results dictionary to store all metrics in one structure
    results = {
        'AGWP': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGWP_fossil': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGWP_bio': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP_fossil': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP_bio': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []}
    }
    
    #STATIC COMPARISON
    if static_comparison:
        dynamicgwp_result = 0        
    #STATIC COMPARISON
        
    #df_query_result_calc_required = df_query_result_calc_required[df_query_result_calc_required["Building_Construction_Type"].str.contains(building_type)]
    df_query_result_calc_required = df_query_result_calc_required.groupby(['Building_Material'], as_index=False).min()
    
    if len(df_query_result_calc_required) == 0:
        print("No Result: No component information")
        if static_comparison:
            return 0
        else:
            return pd.Series(0, range(0,years*10+1)) 
    
    # Pre-define the unit lookup dictionary outside the loop
    unit_lookup = {
        "m3": "Material_Thickness",
        "kg": lambda row: row["Material_Density"] * row["Material_Thickness"],
        "m2": 1,
        "metric ton*km": lambda row: row["Material_Density"] * row["Material_Thickness"]
    }
    
    for _, row in df_query_result_calc_required.iterrows():
        # Create metrics dictionary for current material
        metrics = {metric: pd.Series(0, range(0, years*10+1)) for metric in results.keys()}
        
        # Extract material properties once
        rsl = row["Material_RSL"]
        material = row["Building_Material"]
        component = row["Building_Component"]
        
        if "BP" in component:
            rsl = rsp
        
        # Calculate unit more efficiently
        unit_key = row["Material_Unit"]
        if unit_key in unit_lookup:
            lookup_val = unit_lookup[unit_key]
            unit = lookup_val if isinstance(lookup_val, (int, float)) else (
                lookup_val(row) if callable(lookup_val) else row[lookup_val]
            )
        else:
            unit = 1
        
        # Process elements more efficiently
        elementamounts = ast.literal_eval(row["Element_Amount"])
        for key, amount in elementamounts.items():
            process_element(key, amount, unit, area, 
                           metrics['AGWP'], metrics['AGWP_fossil'], metrics['AGWP_bio'],
                           metrics['AGTP'], metrics['AGTP_fossil'], metrics['AGTP_bio'])
        
        # Handle waste adjustment if needed
        
        if waste == "waste":
            metrics[LCIAindicator] = dynamic_LCIA_b7_waste_replacement_adjust(
                LCIAindicator, metrics[LCIAindicator], rsl, years, metrics[LCIAindicator]
            )
        
        #STATIC COMPARISON
        if static_comparison:
            # When static_comparison is True, the function returns a tuple
            dynamicgwp = dynamic_LCIA_b7_replacement(
                LCIAindicator, metrics[LCIAindicator], rsl, years, 
                metrics[LCIAindicator], waste, material, component, area
            )
            #print(dynamicgwp)
            
            dynamicgwp_result += dynamicgwp           
        #STATIC COMPARISON
        else:
            # Apply replacement calculation only for the requested indicator               
            metrics[LCIAindicator]= dynamic_LCIA_b7_replacement(
                LCIAindicator, metrics[LCIAindicator], rsl, years, 
                metrics[LCIAindicator], waste, material, component, area
            )
            
            print(metrics[LCIAindicator])
                    
            # Update the total and collect the result
            results[LCIAindicator]['total'] += metrics[LCIAindicator]
            results[LCIAindicator]['collect'].append([material, metrics[LCIAindicator]])
   
    #STATIC COMPARISON
    if static_comparison:
        #print(dynamicgwp_result)
        return dynamicgwp_result        
    #STATIC COMPARISON
    else:
        # Process and plot only the requested indicator
        print(results[LCIAindicator]['total'])

        dynamic_LCIA_b7_plot(building_id, LCIAindicator, results[LCIAindicator]['total'], cumulative, component + " total")
        dynamic_LCIA_b7_plot_subparts_in_part(building_id, results[LCIAindicator]['collect'], LCIAindicator, cumulative, component, waste)
        
        return results[LCIAindicator]['total']    
    
#here no calculation, only summing the components up and plotting! (unlike components and materials, the code here is only for without waste)
def dynamic_LCIA_b7_building(building_id, building_type, all_components, all_components_area, LCIAindicator, years, cumulative):
    # Initialize results dictionary to store all metrics in one structure
    results = {
        'AGWP': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGWP_fossil': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGWP_bio': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP_fossil': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP_bio': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []}
    }
    
    #STATIC COMPARISON
    if static_comparison:
        dynamicgwp_result = 0        
    #STATIC COMPARISON
    
    # Filter relevant components and their areas (faster than filtering in the loop)
    # Uncomment if needed:
    # components_with_areas = [(comp, area) for comp, area in zip(all_components, all_components_area) if area != 0]
    # if components_with_areas:
    #     all_components, all_components_area = zip(*components_with_areas)
    
    # Pre-filter the dataframe once for the building type
    df_building_type = df_query_result[df_query_result["Building_Construction_Type"].str.contains(building_type)]
    
    for i, (component, area) in enumerate(zip(all_components, all_components_area)):
        # Filter only the relevant component from the pre-filtered dataframe
        df_query_result_calc_required = df_building_type[df_building_type["Building_Component"].str.contains(component)]
        
        result_dynamic_component = dynamic_LCIA_b7_component(
            building_id, df_query_result_calc_required, LCIAindicator, years, cumulative, area, "-", component
        )
        
        #print(result_dynamic_component)
        
        #STATIC COMPARISON
        if static_comparison:
            dynamicgwp_result += result_dynamic_component            
        #STATIC COMPARISON
        
        else:
            # Update the results for the requested indicator
            results[LCIAindicator]['total'] += result_dynamic_component
            results[LCIAindicator]['collect'].append([component, result_dynamic_component])
    
    #STATIC COMPARISON
    if static_comparison:
        print(dynamicgwp_result)
        return dynamicgwp_result, []     
    #STATIC COMPARISON
    
    else:
        # Process and plot only the requested indicator
        print(results[LCIAindicator]['total'])
        dynamic_LCIA_b7_plot(
            building_id, LCIAindicator, results[LCIAindicator]['total'], cumulative, building_type + " total"
        )
        dynamic_LCIA_b7_plot_subparts_in_part(
            building_id, results[LCIAindicator]['collect'], LCIAindicator, cumulative, building_type, ""
        )
        
       
        return results[LCIAindicator]['total'], results[LCIAindicator]['collect']

#%%
#Part 2.5: Dynamic calculation functions of waste in the cycle

#Static and Dynamic LCIA processes (B7)

def static_LCIA_waste_material (df_query_result_waste_calc_required, LCIAindicator, years):
    result_static_waste=static_LCIA_material (df_query_result_waste_calc_required,LCIAindicator, years)     
    return result_static_waste

def static_LCIA_waste_component (df_query_result_waste_calc_required, LCIAindicator, years, area):
    df_query_result_waste_calc_required = df_query_result_waste_calc_required.groupby(['Building_Material'], as_index=False).min()
    
    result_static_waste=static_LCIA_component (df_query_result_waste_calc_required,LCIAindicator, years, area, True, component_name)
    return result_static_waste

def static_LCIA_waste_building (building_type, all_components, all_components_area, LCIAindicator, years): #here no calculation, only summing the components up and plotting!
    GWP_total=0
    GWP_fossil_total=0
    GWP_bio_total=0
    GTP_total=0
    GTP_fossil_total=0
    GTP_bio_total=0
    
    result_static_component=0
    
    required_building_type = df_query_result_waste[df_query_result_waste["Building_Construction_Type"].str.contains(building_type)]
    
    for component, area in zip(all_components, all_components_area):
        # Filter only the relevant component from the pre-filtered dataframe
        df_query_result_waste_calc_required = required_building_type[required_building_type["Building_Component"].str.contains(component)]
        #print(df_query_result_waste_calc_required["Building_Material"])
        result_static_component += static_LCIA_component(df_query_result_waste_calc_required, LCIAindicator, years, area, True, component)
                              
    if LCIAindicator == "GWP":            
        GWP_total=result_static_component     
        print(GWP_total)
        return GWP_total
    
    if LCIAindicator == "GWP_fossil":
        GWP_fossil_total=result_static_component              
        print(GWP_fossil_total)
        return GWP_fossil_total
        
    if LCIAindicator == "GWP_bio":
        GWP_bio_total=result_static_component   
        print(GWP_bio_total)
        return GWP_bio_total
    
    if LCIAindicator == "GTP":
        GTP_total=result_static_component          
        print(GTP_total)
        return GTP_total
    if LCIAindicator == "GTP_fossil":
        GTP_fossil_total=result_static_component         
        print(GTP_fossil_total)
        return GTP_fossil_total
    if LCIAindicator == "GTP_bio":
        GTP_bio_total=result_static_component         
        print(GTP_bio_total)
        return GTP_bio_total


def dynamic_LCIA_b7_waste_material(df_query_result_waste_calc_required, LCIAindicator, years, cumulative):
    df_query_result_waste_calc_required = df_query_result_waste_calc_required.groupby(['Building_Material'], as_index=False).min()
    
    result_dynamic_waste_collect = []
    
    for i in df_query_result_waste_calc_required.index:
        result_dynamic_waste_collect.append([df_query_result_waste_calc_required.loc[i,"Waste_Name"],dynamic_LCIA_b7_material(df_query_result_waste_calc_required.loc[[i]],LCIAindicator, years,cumulative) ])
    return result_dynamic_waste_collect

def dynamic_LCIA_b7_waste_component(building_id, df_query_result_waste_calc_required, LCIAindicator, years, cumulative, area):
    # Initialize results dictionary to store all metrics in one structure
    results = {
        'AGWP': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGWP_fossil': {'total': pd.Series(0, range(0, years *10+1)), 'collect': []},
        'AGWP_bio': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP_fossil': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP_bio': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []}
    }
        
    #STATIC COMPARISON
    if static_comparison:
        dynamicgwp_result = 0        
    #STATIC COMPARISON
    
    df_query_result_waste_calc_required = df_query_result_waste_calc_required.groupby(['Building_Material'], as_index=False).min()

    result_dynamic_waste=dynamic_LCIA_b7_component (building_id, df_query_result_waste_calc_required,LCIAindicator, years,cumulative, area, "waste", component_name)    
    
    #STATIC COMPARISON
    if static_comparison:
        dynamicgwp_result += result_dynamic_waste
        
        return dynamicgwp_result
    #STATIC COMPARISON
    
    else:  
        results[LCIAindicator]['collect'].append([building_id, result_dynamic_waste])        
        return results[LCIAindicator]['collect']
    

def dynamic_LCIA_b7_waste_building(building_id, building_type, all_components, all_components_area, LCIAindicator, years, cumulative):
    # Initialize results dictionary to store all metrics in one structure
    results = {
        'AGWP': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGWP_fossil': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGWP_bio': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP_fossil': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []},
        'AGTP_bio': {'total': pd.Series(0, range(0, years*10+1)), 'collect': []}
    }
    
    #STATIC COMPARISON
    if static_comparison:
        dynamicgwp_result = 0   
    #STATIC COMPARISON
    
    # Pre-filter the dataframe once for the building type
    df_building_type = df_query_result_waste[df_query_result_waste["Building_Construction_Type"].astype(str).str.contains(building_type, regex=False, na=False)]
    
    for component, area in zip(all_components, all_components_area):
        # Filter only the relevant component from the pre-filtered dataframe
        df_query_result_waste_calc_required = df_building_type[df_building_type["Building_Component"].str.contains(component)]
        
        result_dynamic_component = dynamic_LCIA_b7_component(
            building_id, df_query_result_waste_calc_required, LCIAindicator, years, cumulative, area, "waste", component
        )
        
        print(result_dynamic_component)
        
        #STATIC COMPARISON
        if static_comparison:
            dynamicgwp_result += result_dynamic_component
        #STATIC COMPARISON
        
        else:
            results[LCIAindicator]['total'] += result_dynamic_component
            results[LCIAindicator]['collect'].append([component, result_dynamic_component])

    #STATIC COMPARISON
    if static_comparison:
        return dynamicgwp_result
    #STATIC COMPARISON    
    
    else:
        # Process and plot only the requested indicator
        print(results[LCIAindicator]['total'])
        
        dynamic_LCIA_b7_plot(
            building_id, LCIAindicator, results[LCIAindicator]['total'], cumulative, building_type + " total"
        )
        dynamic_LCIA_b7_plot_subparts_in_part(
            building_id, results[LCIAindicator]['collect'], LCIAindicator, cumulative, building_type, ""
        )
        return results[LCIAindicator]['collect']



def dynamic_LCIA_b7_waste_resultcombi(building_id, result_dynamic_waste, years, df_wo_waste, LCIAindicator, cumulative, name):
    result_dynamic_includingwaste_collect = result_dynamic_waste.copy() 
    result_dynamic_includingwaste_collect.append(["Without Waste",df_wo_waste]) #These two steps make all DFs in a list, separately

    dynamic_LCIA_b7_plot_subparts_in_part(building_id, result_dynamic_includingwaste_collect, LCIAindicator, cumulative, name, "") #plot the results of waste as separates

    result_dynamic_includingwaste = pd.Series(0, range(0,years*10+1))
    for i in range(len(result_dynamic_includingwaste_collect)):
        result_dynamic_includingwaste += result_dynamic_includingwaste_collect[i][1]
    
    dynamic_LCIA_b7_plot(building_id, LCIAindicator, result_dynamic_includingwaste, cumulative, name)
    
    return result_dynamic_includingwaste

#%%
#function for b6
def static_LCIA_b6 (consumption_power_or_heat, df_query_result_calc, LCIAindicator, years):
    GWP=0
    GWP_fossil=0
    GWP_bio=0
    GTP=0
    GTP_fossil=0
    GTP_bio=0
    
    consumption = consumption_power_or_heat.sum() 
        
    for i in df_query_result_calc.index:   
        if df_query_result_calc.loc[i,"Unit"] == "kWh":
            unit = 1
        if df_query_result_calc.loc[i,"Unit"] == "MJ":
            unit = 3.6            
            
        elementamounts = ast.literal_eval(df_query_result_calc.loc[i,"Element_Amount"])
        for key in elementamounts.keys():
            if "carbon dioxide, fossil" in key.lower() or "carbon dioxide, from soil or biomass stock" in key.lower():         
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = 1
                GWP += elementamount * indicator * unit * consumption                
                GWP_fossil += elementamount * indicator * unit * consumption        
                GTP += elementamount * indicator * unit * consumption        
                GTP_fossil += elementamount * indicator * unit * consumption        
            
            elif "carbon dioxide, to soil or biomass stock" in key.lower():
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = -1
                GWP += elementamount * indicator * unit * consumption      
                GWP_bio += elementamount * indicator * unit * consumption      
                GTP += elementamount * indicator * unit * consumption      
                GTP_bio += elementamount * indicator * unit * consumption      
            
            elif "methane, fossil" in key.lower() or "methane, from soil or biomass stock" in key.lower():
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_ch4_fossil.loc[years*10,"AGWP_ch4"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                #indicator = 29.8
                GWP += elementamount * indicator * unit * consumption      
                GWP_fossil += elementamount * indicator * unit * consumption      
                
                indicator = df_dynamicfactor_b7_dagtp_ch4_fossil.loc[years*10,"AGTP_ch4"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator * unit * consumption      
                GTP_fossil += elementamount * indicator * unit * consumption      
            
            elif "methane, non-fossil" in key.lower():
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_ch4_bio.loc[years*10,"AGWP_ch4"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                #indicator = 27
                GWP += elementamount * indicator * unit * consumption      
                GWP_bio += elementamount * indicator * unit * consumption      
                
                indicator = df_dynamicfactor_b7_dagtp_ch4_bio.loc[years*10,"AGTP_ch4"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator * unit * consumption      
                GTP_bio += elementamount * indicator * unit * consumption      
            
            elif "dinitrogen monoxide" in key.lower():
                elementamount = elementamounts[key]
                print(key +":"+str(elementamount))
                indicator = df_dynamicfactor_b7_dagwp_n2o.loc[years*10,"AGWP_n2o"]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                GWP += elementamount * indicator * unit * consumption      
                GWP_fossil += elementamount * indicator * unit * consumption      
                
                indicator = df_dynamicfactor_b7_dagtp_n2o.loc[years*10,"AGTP_n2o"]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                GTP += elementamount * indicator * unit * consumption      
                GTP_fossil += elementamount * indicator * unit * consumption      
            
            else:
                for col in df_dynamicfactor_b7_dagwp_halogen.columns:
                    if col.lower() in key.lower():
                        if col == "Butane" or col == "Ethane" or col == "Propane" or col == "AE":
                            if len(col) == len(key):
                                elementamount = elementamounts[key]
                                print(key + "---"+col +":"+str(elementamount))
                                indicator = df_dynamicfactor_b7_dagwp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                                GWP += elementamount * indicator * consumption 
                                GWP_fossil += elementamount * indicator * unit * consumption      
                                
                                indicator = df_dynamicfactor_b7_dagtp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                                GTP += elementamount * indicator * consumption 
                                GTP_fossil += elementamount * indicator * unit * consumption      
                        
                        else:
                            elementamount = elementamounts[key]
                            print(key + "---"+col +":"+str(elementamount))
                            indicator = df_dynamicfactor_b7_dagwp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagwp_co2.loc[years*10,"AGWP_co2"]
                            GWP += elementamount * indicator * unit * consumption      
                            GWP_fossil += elementamount * indicator * unit * consumption      
                            
                            indicator = df_dynamicfactor_b7_dagtp_halogen.loc[years*10,col]/df_dynamicfactor_b7_dagtp_co2.loc[years*10,"AGTP_co2"]
                            GTP += elementamount * indicator * unit * consumption      
                            GTP_fossil += elementamount * indicator * unit * consumption         
        
    indicators = {
        "GWP": GWP,
        "GWP_fossil": GWP_fossil,
        "GWP_bio": GWP_bio,
        "GTP": GTP,
        "GTP_fossil": GTP_fossil,
        "GTP_bio": GTP_bio
    }
    return indicators.get(LCIAindicator)


def separate_calculation_new_elementflow_b6(current_dynamic_factor, LCIAindicator, df_query_result_b, year_difference, material, lower_influence, df_query_result_b_lower, df_query_result_b_lower2, target):
    AGWP=pd.Series(0, range(0,years*10+1))
    AGWP_fossil=pd.Series(0, range(0,years*10+1))
    AGWP_bio=pd.Series(0, range(0,years*10+1))
    AGTP=pd.Series(0, range(0,years*10+1))
    AGTP_fossil=pd.Series(0, range(0,years*10+1))
    AGTP_bio=pd.Series(0, range(0,years*10+1))
    
    if (current_dynamic_factor == "B5" or current_dynamic_factor == "B4" or current_dynamic_factor == "B3") and not lower_influence:        
        
        if not any(len(sublist[3]) > 0 for sublist in df_query_result_b):
            
            AGWP=AGWP
            AGWP_fossil=AGWP_fossil
            AGWP_bio=AGWP_bio
            AGTP=AGTP
            AGTP_fossil=AGTP_fossil
            AGTP_bio=AGTP_bio
        else:
            # Pre-calculate exact_year outside the loop
            exact_year = min(starting_time + year_difference, 2060)
            
            if "power-2024" in dynamic_factor:
                exact_year = 2024
            
            # Main processing loop with more efficient structure
            for k in range(len(df_query_result_b)):
                item = df_query_result_b[k]
                
                # Skip iterations that don't match criteria or have no data
                if item[1] != material and target == "Heat": # material is the name of the energysource, this filtering is only for heat
                    continue

                power_mix = item[3][0]
                
                dynamic_ratio = item[3][2]
                dynamic_ratio = dynamic_ratio.loc[(dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                
                energy_source = item[3][1]
                dynamic_ratio_value = dynamic_ratio.loc[0,"Energy_Source_Percentage_Dynamic"] if not dynamic_ratio.empty else None
                
                # Process energy sources once
                for g in energy_source.index:
                    if dynamic_ratio_value is not None:
                        energy_source.loc[g,"Energy_Source_Percentage_Dynamic"] = dynamic_ratio_value
                    
                    if isinstance(energy_source.loc[g,"Power_Transmission_Network"], float):
                        energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Power_Transmission_Network"]
                    elif "sulfur hexafluoride, liquid" in energy_source.loc[g,"Name"]:
                        energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Energy_Source"]
                    else:
                        energysourcedynamics = ast.literal_eval(energy_source.loc[g,"Energy_Source_Percentage_Dynamic"])
                        for key in energysourcedynamics:
                            if energy_source.loc[g,"Name"] in key:
                                value = energysourcedynamics[key]
                                energy_source.loc[g,"Energy_Source_Percentage_Final"] = value if isinstance(value, (float, int)) else value[0]
                                break 
                
                if target == "Heat":
                
                    ratios = item[2] #e.g. {'electricity, low voltage - CH': 0.0008751684210526321}
                    
                    # Process each material in the lower voltage
                    for ratio in ratios:
                        
                        if ratio == power_mix.loc[0,"Power_Mix"]:
                        
                            original_ratio = ratios[ratio]
                            
                            change_percent = 0 - original_ratio
                            
                            # Get material properties
                            unit = 1 # for B6, and generally no unit conversion needed for this
                            area = 1 # for B6
                            
                            # Process current higher voltage power
                            elementamounts = ast.literal_eval(power_mix.loc[0,"Element_Amount_Power_Mix"])
                            
                            # Process each element in the current power
                            for key, amount in elementamounts.items():
                                elementamount = amount * change_percent
                                process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                            
                            # Add new higher voltage power
                            for p in energy_source.index:
                                new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                                percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                                
                                for key, amount in new_elementamounts.items():
                                    elementamount = amount * original_ratio * percentage_final
                                    process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                
                else:
                    original_ratio = 1
                    
                    change_percent = 0 - original_ratio
                    
                    # Get material properties
                    unit = 1 # for B6, and generally no unit conversion needed for this
                    area = 1 # for B6
                    
                    # Process current higher voltage power
                    elementamounts = ast.literal_eval(power_mix.loc[0,"Element_Amount_Power_Mix"])
                    
                    # Process each element in the current power
                    for key, amount in elementamounts.items():
                        elementamount = amount * change_percent
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                    
                    # Add new higher voltage power
                    for p in energy_source.index:
                        new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                        percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                        
                        for key, amount in new_elementamounts.items():
                            elementamount = amount * original_ratio * percentage_final
                            process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)                        
                            
                           
    elif current_dynamic_factor == "B4" and lower_influence == True:
        
        if not any(len(sublist[3]) > 0 for sublist in df_query_result_b_lower):
            # No changes needed, variables remain as they are
            AGWP=AGWP
            AGWP_fossil=AGWP_fossil
            AGWP_bio=AGWP_bio
            AGTP=AGTP
            AGTP_fossil=AGTP_fossil
            AGTP_bio=AGTP_bio
        else:
            
            # Calculate power transformation factor once
            power_transform_factor = medium_ratio_static.loc[0,"Power_Transformation"]
            
            # Pre-calculate exact_year outside the loop
            exact_year = min(starting_time + year_difference, 2060)
            
            if "power-2024" in dynamic_factor:
                exact_year = 2024
            
            # Prepare dynamic ratio once (outside the k loop)
            dynamic_ratio = df_query_result_b4_dynamic_ratio.loc[(df_query_result_b4_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
            
            # Process energy source preparation once (outside the k loop)
            energy_source = df_query_result_b4_energysource_amount.copy()
            dynamic_ratio_value = dynamic_ratio.loc[0,"Energy_Source_Percentage_Dynamic"] if not dynamic_ratio.empty else None
            
            
            # Process energy sources once
            for g in energy_source.index:
                if dynamic_ratio_value is not None:
                    energy_source.loc[g,"Energy_Source_Percentage_Dynamic"] = dynamic_ratio_value
                
                if isinstance(energy_source.loc[g,"Power_Transmission_Network"], float):
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Power_Transmission_Network"]
                elif "sulfur hexafluoride, liquid" in energy_source.loc[g,"Name"]:
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Energy_Source"]
                else:
                    energysourcedynamics = ast.literal_eval(energy_source.loc[g,"Energy_Source_Percentage_Dynamic"])
                    for key in energysourcedynamics:
                        if energy_source.loc[g,"Name"] in key:
                            value = energysourcedynamics[key]
                            energy_source.loc[g,"Energy_Source_Percentage_Final"] = value if isinstance(value, (float, int)) else value[0]
                            break           
            
            
            if "B5" in dynamic_factor:
                dynamic_ratio_b5 = df_query_result_b5_dynamic_ratio.loc[(df_query_result_b5_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                dynamic_ratio_value_b5 = ast.literal_eval(dynamic_ratio_b5.loc[0,"Energy_Source_Percentage_Dynamic"])
                
                matching_keys = [key for key in dynamic_ratio_value_b5 if "electricity voltage transformation from medium to low voltage" in key]
                if matching_keys:
                    power_transform_factor_new = dynamic_ratio_value_b5[matching_keys[0]]
                    power_transform_factor = power_transform_factor_new
            
            # Main processing loop with more efficient structure
            for k in range(len(df_query_result_b_lower)):
                item = df_query_result_b_lower[k]                               
                
                if target == "Heat":
                    # Skip iterations that don't match criteria or have no data
                    if item[1] != material: # material is the name of the energysource
                        continue
                    
                    power_mix = item[3][0]
                    
                    ratios = item[2] #e.g. {'electricity, low voltage - CH': 0.0008751684210526321}
                    
                    # Process each material in the lower voltage
                    for ratio in ratios:
                        
                        if ratio == power_mix.loc[0,"Power_Mix"]:
                        
                            original_ratio = ratios[ratio]
                            
                            change_percent = 0 - original_ratio
                            
                            # Get material properties
                            unit = 1 # for B6, and generally no unit conversion needed for this
                            area = 1 # for B6
                                        
                            # Process current higher voltage power
                            elementamounts = ast.literal_eval(medium_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                            
                            # Process each element in the current power
                            for key, amount in elementamounts.items():
                                elementamount = amount * change_percent * power_transform_factor
                                process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                                
                            # Add new higher voltage power
                            for p in energy_source.index:
                                new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                                percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]

                                for key, amount in new_elementamounts.items():
                                    elementamount = amount * original_ratio * percentage_final * power_transform_factor
                                    process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                
                else:
                    original_ratio = 1
                    
                    change_percent = 0 - original_ratio
                    
                    # Get material properties
                    unit = 1 # for B6, and generally no unit conversion needed for this
                    area = 1 # for B6
                                
                    # Process current higher voltage power
                    elementamounts = ast.literal_eval(medium_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                    
                    # Process each element in the current power
                    for key, amount in elementamounts.items():
                        elementamount = amount * change_percent * power_transform_factor
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                        
                    # Add new higher voltage power
                    for p in energy_source.index:
                        new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                        percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]

                        for key, amount in new_elementamounts.items():
                            elementamount = amount * original_ratio * percentage_final * power_transform_factor
                            process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
            
                            
        
    elif current_dynamic_factor == "B3" and lower_influence == True:
        
        if not any(len(sublist[3]) > 0 for sublist in df_query_result_b_lower):
            # No changes needed, variables remain as they are
            AGWP=AGWP
            AGWP_fossil=AGWP_fossil
            AGWP_bio=AGWP_bio
            AGTP=AGTP
            AGTP_fossil=AGTP_fossil
            AGTP_bio=AGTP_bio
        else:
            # Calculate power transformation factor once
            power_transform_factor = high_ratio_static.loc[0,"Power_Transformation"]
            
            # Pre-calculate exact_year outside the loop
            exact_year = min(starting_time + year_difference, 2060)
            
            if "power-2024" in dynamic_factor:
                exact_year = 2024
            
            # Prepare dynamic ratio once (outside the k loop)
            dynamic_ratio = df_query_result_b3_dynamic_ratio.loc[(df_query_result_b3_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
            
            # Process energy source preparation once (outside the k loop)
            energy_source = df_query_result_b3_energysource_amount.copy()
            dynamic_ratio_value = dynamic_ratio.loc[0,"Energy_Source_Percentage_Dynamic"] if not dynamic_ratio.empty else None
            
            # Process energy sources once
            for g in energy_source.index:
                if dynamic_ratio_value is not None:
                    energy_source.loc[g,"Energy_Source_Percentage_Dynamic"] = dynamic_ratio_value
                
                if isinstance(energy_source.loc[g,"Power_Transmission_Network"], float):
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Power_Transmission_Network"]
                elif "sulfur hexafluoride, liquid" in energy_source.loc[g,"Name"]:
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Energy_Source"]
                else:
                    energysourcedynamics = ast.literal_eval(energy_source.loc[g,"Energy_Source_Percentage_Dynamic"])
                    for key in energysourcedynamics:
                        if energy_source.loc[g,"Name"] in key:
                            value = energysourcedynamics[key]
                            energy_source.loc[g,"Energy_Source_Percentage_Final"] = value if isinstance(value, (float, int)) else value[0]
                            break           
            
            if "B4" in dynamic_factor:
                dynamic_ratio_b4 = df_query_result_b4_dynamic_ratio.loc[(df_query_result_b4_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                dynamic_ratio_value_b4 = ast.literal_eval(dynamic_ratio_b4.loc[0,"Energy_Source_Percentage_Dynamic"])
                
                matching_keys = [key for key in dynamic_ratio_value_b4 if "electricity voltage transformation from medium to low voltage" in key]
                if matching_keys:
                    power_transform_factor_new = dynamic_ratio_value_b4[matching_keys[0]]
                    power_transform_factor = power_transform_factor_new
            
            # Main processing loop with more efficient structure
            for k in range(len(df_query_result_b_lower)):
                item = df_query_result_b_lower[k]               
                
                if target == "Heat":
                    # Skip iterations that don't match criteria or have no data
                    if item[1] != material: # material is the name of the energysource
                        continue
                    
                    power_mix = item[3][0]
                    
                    ratios = item[2] #e.g. {'electricity, low voltage - CH': 0.0008751684210526321}
                    
                    # Process each material in the lower voltage
                    for ratio in ratios:
                        
                        if ratio == power_mix.loc[0,"Power_Mix"]:
                        
                            original_ratio = ratios[ratio]
                            
                            change_percent = 0 - original_ratio
                            
                            # Get material properties
                            unit = 1 # for B6, and generally no unit conversion needed for this
                            area = 1 # for B6
                                                        
                            # Process current higher voltage power
                            elementamounts = ast.literal_eval(high_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                            
                            # Process each element in the current power
                            for key, amount in elementamounts.items():
                                elementamount = amount * change_percent * power_transform_factor
                                process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                            
                            # Add new higher voltage power
                            for p in energy_source.index:
                                new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                                percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                                
                                for key, amount in new_elementamounts.items():
                                    elementamount = amount * original_ratio * percentage_final * power_transform_factor
                                    process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
            
            else:
                original_ratio = 1
                
                change_percent = 0 - original_ratio
                
                # Get material properties
                unit = 1 # for B6, and generally no unit conversion needed for this
                area = 1 # for B6
                                            
                # Process current higher voltage power
                elementamounts = ast.literal_eval(high_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                
                # Process each element in the current power
                for key, amount in elementamounts.items():
                    elementamount = amount * change_percent * power_transform_factor
                    process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                
                # Add new higher voltage power
                for p in energy_source.index:
                    new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                    percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                    
                    for key, amount in new_elementamounts.items():
                        elementamount = amount * original_ratio * percentage_final * power_transform_factor
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
        
        if not any(len(sublist[3]) > 0 for sublist in df_query_result_b_lower2):
            # No changes needed, variables remain as they are
            AGWP=AGWP
            AGWP_fossil=AGWP_fossil
            AGWP_bio=AGWP_bio
            AGTP=AGTP
            AGTP_fossil=AGTP_fossil
            AGTP_bio=AGTP_bio
        else:
            # Calculate power transformation factor once
            power_transform_factor = high_ratio_static.loc[0,"Power_Transformation"] * medium_ratio_static.loc[0,"Power_Transformation"]
            
            # Pre-calculate exact_year outside the loop
            exact_year = min(starting_time + year_difference, 2060)
            
            if "power-2024" in dynamic_factor:
                exact_year = 2024
            
            # Prepare dynamic ratio once (outside the k loop)
            dynamic_ratio = df_query_result_b3_dynamic_ratio.loc[(df_query_result_b3_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
            
            # Process energy source preparation once (outside the k loop)
            energy_source = df_query_result_b3_energysource_amount.copy()
            dynamic_ratio_value = dynamic_ratio.loc[0,"Energy_Source_Percentage_Dynamic"] if not dynamic_ratio.empty else None
            
            # Process energy sources once
            for g in energy_source.index:
                if dynamic_ratio_value is not None:
                    energy_source.loc[g,"Energy_Source_Percentage_Dynamic"] = dynamic_ratio_value
                
                if isinstance(energy_source.loc[g,"Power_Transmission_Network"], float):
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Power_Transmission_Network"]
                elif "sulfur hexafluoride, liquid" in energy_source.loc[g,"Name"]:
                    energy_source.loc[g,"Energy_Source_Percentage_Final"] = energy_source.loc[g,"Energy_Source"]
                else:
                    energysourcedynamics = ast.literal_eval(energy_source.loc[g,"Energy_Source_Percentage_Dynamic"])
                    for key in energysourcedynamics:
                        if energy_source.loc[g,"Name"] in key:
                            value = energysourcedynamics[key]
                            energy_source.loc[g,"Energy_Source_Percentage_Final"] = value if isinstance(value, (float, int)) else value[0]
                            break           
            
            if "B5" in dynamic_factor:
                dynamic_ratio_b5 = df_query_result_b5_dynamic_ratio.loc[(df_query_result_b5_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                dynamic_ratio_value_b5 = ast.literal_eval(dynamic_ratio_b5.loc[0,"Energy_Source_Percentage_Dynamic"])
                
                matching_keys = [key for key in dynamic_ratio_value_b5 if "electricity voltage transformation from medium to low voltage" in key]
                if matching_keys:
                    power_transform_factor_new_b5 = dynamic_ratio_value_b5[matching_keys[0]]
                    power_transform_factor = high_ratio_static.loc[0,"Power_Transformation"]*power_transform_factor_new_b5
            
            if "B4" in dynamic_factor:
                dynamic_ratio_b4 = df_query_result_b4_dynamic_ratio.loc[(df_query_result_b4_dynamic_ratio["Year"]==str(exact_year))].reset_index(drop=True)
                dynamic_ratio_value_b4 = ast.literal_eval(dynamic_ratio_b4.loc[0,"Energy_Source_Percentage_Dynamic"])
                
                matching_keys = [key for key in dynamic_ratio_value_b4 if "electricity voltage transformation from medium to low voltage" in key]
                if matching_keys:
                    power_transform_factor_new_b4 = dynamic_ratio_value_b4[matching_keys[0]]
                    power_transform_factor = power_transform_factor_new_b5 * power_transform_factor_new_b4
            
            # Main processing loop with more efficient structure
            for k in range(len(df_query_result_b_lower2)):
                                   
                if target == "Heat":
                    # Skip iterations that don't match criteria or have no data
                    if item[1] != material: # material is the name of the energysource
                        continue
                    
                    power_mix = item[3][0]                
                    
                    ratios = item[2] #e.g. {'electricity, low voltage - CH': 0.0008751684210526321}
                    
                    # Process each material in the lower voltage
                    for ratio in ratios:
                        
                        if ratio == power_mix.loc[0,"Power_Mix"]:
                        
                            original_ratio = ratios[ratio]
                            
                            change_percent = 0 - original_ratio
                            
                            # Get material properties
                            unit = 1 # for B6, and generally no unit conversion needed for this
                            area = 1 # for B6
                            
                            # Process current higher voltage power
                            elementamounts = ast.literal_eval(high_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                            
                            # Process each element in the current power
                            for key, amount in elementamounts.items():
                                elementamount = amount * change_percent * power_transform_factor
                                process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                            
                            # Add new higher voltage power
                            for p in energy_source.index:
                                new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                                percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                                
                                for key, amount in new_elementamounts.items():
                                    elementamount = amount * original_ratio * percentage_final * power_transform_factor
                                    process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)                                   
                                                
                else:
                    original_ratio = 1
                    
                    change_percent = 0 - original_ratio
                    
                    # Get material properties
                    unit = 1 # for B6, and generally no unit conversion needed for this
                    area = 1 # for B6
                    
                    # Process current higher voltage power
                    elementamounts = ast.literal_eval(high_ratio_static.loc[0,"Element_Amount_Energy_Source"])
                    
                    # Process each element in the current power
                    for key, amount in elementamounts.items():
                        elementamount = amount * change_percent * power_transform_factor
                        process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
                    
                    # Add new higher voltage power
                    for p in energy_source.index:
                        new_elementamounts = ast.literal_eval(energy_source.loc[p,"Element_Amount_Energy_Source"])
                        percentage_final = energy_source.loc[p,"Energy_Source_Percentage_Final"]
                        
                        for key, amount in new_elementamounts.items():
                            elementamount = amount * original_ratio * percentage_final * power_transform_factor
                            process_element(key, elementamount, unit, area, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)                                   
                
                
    indicators = {
        "AGWP": AGWP,
        "AGWP_fossil": AGWP_fossil,
        "AGWP_bio": AGWP_bio,
        "AGTP": AGTP,
        "AGTP_fossil": AGTP_fossil,
        "AGTP_bio": AGTP_bio
    }
    return indicators.get(LCIAindicator)  


def dynamic_LCIA_b7_b6_annual_consumption(LCIAindicator, LCIAindicatorvalue, consumption, years, target, type_heat_power):
    annual_consumption = pd.DataFrame()
    material = type_heat_power
    
    if target == "Heat":
        df_query_result_b5_final = df_query_result_b5_final_heat
        df_query_result_b4_final = df_query_result_b4_final_heat
        df_query_result_b3_final = df_query_result_b3_final_heat
    else:
        df_query_result_b5_final = df_query_result_b5_final_power
        df_query_result_b4_final = df_query_result_b4_final_power
        df_query_result_b3_final = df_query_result_b3_final_power
        
    
    if "-" not in dynamic_factor:
        for j in range(len(consumption)):
            LCIAindicatorvalue_difference = 0
            
            if "B5" in dynamic_factor or "power-2024" in dynamic_factor: 
                #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                
                LCIAindicatorvalue_difference_b5 = separate_calculation_new_elementflow_b6("B5", LCIAindicator, df_query_result_b5_final, (j+1), material, False, None, None, target)
                
                LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b5
                               
                
            if "B4" in dynamic_factor or "power-2024" in dynamic_factor:     
                #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                LCIAindicatorvalue_difference_b4 = separate_calculation_new_elementflow_b6("B4", LCIAindicator, df_query_result_b4_final, (j+1), material, False, None, None, target)
                
                #repeat the process for the lower voltage
                LCIAindicatorvalue_difference_b4_low = separate_calculation_new_elementflow_b6("B4", LCIAindicator, df_query_result_b4_final, (j+1), material, True, df_query_result_b5_final, None, target)

                                    
                LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b4 + LCIAindicatorvalue_difference_b4_low
                
        
            if "B3" in dynamic_factor or "power-2024" in dynamic_factor: 
                #separately calculate the difference LCIAindicatorvalue with the new element flow at this time
                LCIAindicatorvalue_difference_b3 = separate_calculation_new_elementflow_b6("B3", LCIAindicator, df_query_result_b3_final, (j+1), material, False, None, None, target)
                
                #repeat the process for the lower voltage
                LCIAindicatorvalue_difference_b3_low = separate_calculation_new_elementflow_b6("B3", LCIAindicator, df_query_result_b3_final, (j+1), material, True, df_query_result_b4_final, df_query_result_b5_final, target)
                
                LCIAindicatorvalue_difference += LCIAindicatorvalue_difference_b3 + LCIAindicatorvalue_difference_b3_low        
            
            indicator_material = (LCIAindicatorvalue.copy() + LCIAindicatorvalue_difference) * consumption[j]
            indicator_temp = pd.Series(0, range(0,j*10))
            indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                    
            annual_consumption = pd.concat([annual_consumption,indicator_material],axis=1)      
            annual_consumption=annual_consumption.sum(axis=1, numeric_only=True)[0:rsp*10+1]
        
    else:
        for j in range(len(consumption)):
            indicator_material = LCIAindicatorvalue.copy() * consumption[j]
            indicator_temp = pd.Series(0, range(0,j*10))
            indicator_material = pd.concat([indicator_temp, indicator_material], axis=0).reset_index(drop=True)
                    
            annual_consumption = pd.concat([annual_consumption,indicator_material],axis=1)      
            annual_consumption=annual_consumption.sum(axis=1, numeric_only=True)[0:rsp*10+1]
            
    return annual_consumption


def dynamic_LCIA_b7_b6 (consumption_power_or_heat, building_id, df_query_result_calc, LCIAindicator, years, cumulative, type_heat_power):
    AGWP_total=pd.Series(0, range(0,years*10+1))
    AGWP_fossil_total=pd.Series(0, range(0,years*10+1))
    AGWP_bio_total=pd.Series(0, range(0,years*10+1))
    AGTP_total=pd.Series(0, range(0,years*10+1))
    AGTP_fossil_total=pd.Series(0, range(0,years*10+1))
    AGTP_bio_total=pd.Series(0, range(0,years*10+1))    
    
    
    if "Powermix" in df_query_result_calc.columns:
        consumption = consumption_power
        target = "Powermix"
    if "Heat" in df_query_result_calc.columns:
        consumption = consumption_heat 
        target = "Heat"
    
    for i in df_query_result_calc.index: 
        AGWP=pd.Series(0, range(0,years*10+1))
        AGWP_fossil=pd.Series(0, range(0,years*10+1))
        AGWP_bio=pd.Series(0, range(0,years*10+1))
        AGTP=pd.Series(0, range(0,years*10+1))
        AGTP_fossil=pd.Series(0, range(0,years*10+1))
        AGTP_bio=pd.Series(0, range(0,years*10+1))
        
        if df_query_result_calc.loc[i,"Unit"] == "kWh":
            unit = 1
        if df_query_result_calc.loc[i,"Unit"] == "MJ":
            unit = 3.6
        if "Powermix" in df_query_result_calc.columns:
            material=df_query_result_calc.loc[i,"Powermix"]
        if "Heat" in df_query_result_calc.columns:
            material=df_query_result_calc.loc[i,"Energysource"]
            
        elementamounts = ast.literal_eval(df_query_result_calc.loc[i,"Element_Amount"])
        
        for key, amount in elementamounts.items():
            elementamount = amount
            process_element(key, elementamount, unit, 1, AGWP, AGWP_fossil, AGWP_bio, AGTP, AGTP_fossil, AGTP_bio)
        
        
        if LCIAindicator == "AGWP":
            AGWP = dynamic_LCIA_b7_b6_annual_consumption("AGWP", AGWP, consumption, years, target, type_heat_power)
            print(AGWP)
            AGWP_total += AGWP
        
        if LCIAindicator == "AGWP_fossil":
            AGWP_fossil = dynamic_LCIA_b7_b6_annual_consumption("AGWP_fossil", AGWP_fossil, consumption, years, target, type_heat_power)
            print(AGWP_fossil)
            AGWP_fossil_total += AGWP_fossil

        if LCIAindicator == "AGWP_bio":
            AGWP_bio = dynamic_LCIA_b7_b6_annual_consumption("AGWP_bio", AGWP_bio, consumption, years, target, type_heat_power)
            print(AGWP_bio)
            AGWP_bio_total += AGWP_bio  

        if LCIAindicator == "AGTP":
            AGTP = dynamic_LCIA_b7_b6_annual_consumption("AGTP", AGTP, consumption, years, target, type_heat_power)
            print(AGTP)
            AGTP_total += AGTP
        
        if LCIAindicator == "AGTP_fossil":
            AGTP_fossil = dynamic_LCIA_b7_b6_annual_consumption("AGTP_fossil", AGTP_fossil, consumption, years, target, type_heat_power)
            print(AGTP_fossil)
            AGTP_fossil_total += AGTP_fossil
            
        if LCIAindicator == "AGTP_bio":
            AGTP_bio = dynamic_LCIA_b7_b6_annual_consumption("AGTP_bio", AGTP_bio, consumption, years, target, type_heat_power)
            print(AGTP_bio)
            AGTP_bio_total += AGTP_bio
            
        
    if LCIAindicator == "AGWP":
        print(AGWP_total)
        if phase_C==False: #so for the case when adding the waste interim results will not be plotted
            dynamic_LCIA_b7_plot(building_id, LCIAindicator,AGWP_total,cumulative,material)
        return AGWP_total
    
    if LCIAindicator == "AGWP_fossil":
        print(AGWP_fossil_total)
        if phase_C==False:
            dynamic_LCIA_b7_plot(building_id, LCIAindicator,AGWP_fossil_total,cumulative,material)
        return AGWP_fossil_total
    
    if LCIAindicator == "AGWP_bio":
        print(AGWP_bio_total)
        if phase_C==False:
            dynamic_LCIA_b7_plot(building_id, LCIAindicator,AGWP_bio_total,cumulative,material)
        return AGWP_bio_total
    
    if LCIAindicator == "AGTP":
        print(AGTP_total)
        if phase_C==False:
            dynamic_LCIA_b7_plot(building_id, LCIAindicator,AGTP_total,cumulative,material)
        return AGTP_total
    
    if LCIAindicator == "AGTP_fossil":
        print(AGTP_fossil_total)
        if phase_C==False:
            dynamic_LCIA_b7_plot(building_id, LCIAindicator,AGTP_fossil_total,cumulative,material)
        return AGTP_fossil_total
    
    if LCIAindicator == "AGTP_bio":
        print(AGTP_bio_total)
        if phase_C==False:
            dynamic_LCIA_b7_plot(building_id, LCIAindicator,AGTP_bio_total,cumulative,material)
        return AGTP_bio_total

#%%
def consolidate_component_parquets(folder_path, choose_study, dynamic_factor, dynamic_scenario, delete_individual=True):
    """
    Consolidate ALL component Parquet files into a single file with structured naming
    Processes all files that don't start with 'consolidated_components_'
    
    Parameters:
    -----------
    folder_path : str
        Path to folder containing component Parquet files
    choose_study : str
        Study identifier (e.g., 'm2t2d2l2_1')
    dynamic_factor : list
        List of dynamic factors (e.g., ['B1', 'B2'])
    dynamic_scenario : str
        Scenario name (e.g., 'Carbon Neutral')
    delete_individual : bool
        If True, delete individual Parquet files after consolidation
    """
    import time
    
    print("\n" + "="*80)
    print("CONSOLIDATING COMPONENT PARQUET FILES")
    print("="*80)
    
    start_time = time.time()
    
    # Generate output filename using the same structure as results files
    if "-" not in dynamic_factor:
        output_filename = f'consolidated_components_{choose_study}_{"_".join(dynamic_factor)}_{dynamic_scenario}.parquet'
    else:
        output_filename = f'consolidated_components_{choose_study}_-.parquet'
    
    print(f"Output file: {output_filename}")
    
    # Find ALL parquet files (exclude only consolidated files)
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.parquet')]
    parquet_files = [f for f in all_files if not f.startswith('consolidated_components_')]
    
    if len(parquet_files) == 0:
        print("No individual Parquet files found to consolidate")
        return None
    
    print(f"Found {len(parquet_files)} Parquet files to consolidate")
    
    all_data = []
    errors = 0
    skipped = 0
    processed_files = []
    
    for i, filename in enumerate(parquet_files):
        if (i + 1) % 100 == 0:
            print(f"Processing... {i+1}/{len(parquet_files)}")
        
        try:
            # Initialize metadata dictionary
            metadata = {
                'building_id': None,
                'component': None,
                'b_scenario': None,
                'policy_scenario': None,
                'waste_scenario': None,
                'building_type': None,
                'indicator': None,
                'cumulative': None,
                'material_name': None,
                'component_detail': None
            }
            
            # Extract building ID - REQUIRED
            building_id_match = re.search(r'LOD2_(\d{7,8})', filename)
            if not building_id_match:
                skipped += 1
                continue
            
            metadata['building_id'] = building_id_match.group(1)
            
            # Extract component - more flexible matching
            component_found = False
            
            # Try detailed component names first (e.g., "IWmas_1")
            component_detail_match = re.search(r'_(BP|FL|CFL|CW|EW|IW|FRO|PRO|SCW|TFL|WIN)(?:mas|tim)?_?\d*_', filename)
            if component_detail_match:
                full_component = component_detail_match.group(0).strip('_')
                metadata['component_detail'] = full_component
                # Extract base component
                metadata['component'] = component_detail_match.group(1)
                component_found = True
            
            # If not found, try simple component patterns
            if not component_found:
                for pattern in ['_IW_', '_WIN_', '_PRO_', '_FRO_', '_EW_', '_FL_', '_BP_', '_CW_', '_CFL_', '_SCW_', '_TFL_']:
                    if pattern in filename:
                        metadata['component'] = pattern.strip('_')
                        component_found = True
                        break
            
            # If still not found, try without underscores at word boundaries
            if not component_found:
                comp_match = re.search(r'\b(IW|WIN|PRO|FRO|EW|FL|BP|CW|CFL|SCW|TFL)\b', filename)
                if comp_match:
                    metadata['component'] = comp_match.group(1)
                    component_found = True
            
            if not component_found:
                # Store as "Unknown" instead of skipping
                metadata['component'] = 'Unknown'
                print(f"  Warning: Could not extract component from: {filename[:60]}...")
            
            # Extract material name if present (between component and cumulative/scenario)
            # Look for text after component and before cumulative or scenario keywords
            material_match = re.search(r'_([a-zA-Z0-9\s,\.\-]+?)_(?:cumulative|non-cumulative|B1|B2|B3|B4|B5|Business|Carbon|Original)', filename)
            if material_match:
                material_candidate = material_match.group(1)
                material_candidate = re.sub(r'^\d+_', '', material_candidate)
                # Clean up material name
                if not any(kw in material_candidate.lower() for kw in ['deby', 'lod2', 'masonry', 'timber', 'agwp', 'agtp']):
                    metadata['material_name'] = material_candidate
            
            # Extract B scenario - handle all variations
            if 'B1_B2_B3_B4_B5' in filename:
                metadata['b_scenario'] = 'B12345'
            elif 'B3_B4_B5' in filename:
                metadata['b_scenario'] = 'B345'
            elif re.search(r'\bB2\b|_B2_', filename):
                metadata['b_scenario'] = 'B2'
            elif re.search(r'\bB1\b|_B1_', filename):
                metadata['b_scenario'] = 'B1'
            else:
                # Check if it's Original (no B patterns)
                b_patterns = ['B1', 'B2', 'B3', 'B4', 'B5']
                has_b_pattern = any(p in filename for p in b_patterns)
                if not has_b_pattern:
                    metadata['b_scenario'] = 'Original'
                else:
                    metadata['b_scenario'] = 'Unknown'
            
            # Extract policy scenario
            if 'Business As Usual' in filename or 'Business_As_Usual' in filename:
                metadata['policy_scenario'] = 'Business As Usual'
            elif 'Carbon Neutral' in filename or 'Carbon_Neutral' in filename:
                metadata['policy_scenario'] = 'Carbon Neutral'
            elif metadata['b_scenario'] == 'Original':
                metadata['policy_scenario'] = 'Original'
            else:
                metadata['policy_scenario'] = 'Not Specified'
            
            # Extract waste scenario - more flexible
            if re.search(r'_waste[_\.]', filename, re.IGNORECASE):
                metadata['waste_scenario'] = 'Waste'
            elif '_-_' in filename or '_-.' in filename or metadata['b_scenario'] == 'Original':
                metadata['waste_scenario'] = 'Without Waste'
            else:
                # Check the pattern - if it has scenario info but no explicit waste marker, it's likely "Total"
                if metadata['b_scenario'] != 'Unknown':
                    metadata['waste_scenario'] = 'Total'
                else:
                    metadata['waste_scenario'] = 'Unknown'
            
            # Extract building type - more flexible
            if 'Timber' in filename:
                # Check if it's a building type (Timber_1, Timber_2) or material (timber in component name)
                if re.search(r'Timber_\d+', filename):
                    metadata['building_type'] = 'Timber'
                else:
                    # Might be part of component name, check context
                    if 'Masonry' not in filename:
                        metadata['building_type'] = 'Timber'
                    else:
                        metadata['building_type'] = 'Not Specified'
            elif 'Masonry' in filename:
                if re.search(r'Masonry_\d+', filename):
                    metadata['building_type'] = 'Masonry'
                else:
                    metadata['building_type'] = 'Masonry'
            else:
                metadata['building_type'] = 'Not Specified'
            
            # Extract indicator
            if 'AGWP' in filename:
                metadata['indicator'] = 'AGWP'
            elif 'AGTP' in filename:
                metadata['indicator'] = 'AGTP'
            else:
                metadata['indicator'] = 'Unknown'
            
            # Extract cumulative type
            if 'non-cumulative' in filename:
                metadata['cumulative'] = 'non-cumulative'
            else:
                metadata['cumulative'] = 'cumulative'
            
            # Read file
            df = pd.read_parquet(os.path.join(folder_path, filename))
            
            # Handle different file structures
            if len(df.columns) == 0:
                print(f"  Warning: Empty file: {filename}")
                skipped += 1
                continue
            
            # Rename column to 'value'
            if len(df.columns) == 1:
                df.columns = ['value']
            else:
                # Take the first numeric column as value
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    df = df[[numeric_cols[0]]]
                    df.columns = ['value']
                else:
                    # Take first column
                    df = df.iloc[:, [0]]
                    df.columns = ['value']
            
            # Add timestep
            df['timestep'] = df.index
            
            # Add all metadata
            for key, value in metadata.items():
                df[key] = value
            
            # Add original filename for reference
            df['source_filename'] = filename
            
            all_data.append(df)
            processed_files.append(filename)
        
        except Exception as e:
            errors += 1
            if errors <= 10:  # Print first 10 errors
                print(f"  Error processing {filename}: {e}")
            continue
    
    if len(all_data) == 0:
        print("No valid data to consolidate")
        return None
    
    print(f"\nCombining {len(all_data)} dataframes...")
    print(f"Skipped {skipped} files (no building ID found)")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    print(f"Total rows: {len(combined_df):,}")
    print(f"Memory usage: {combined_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Save
    output_path = os.path.join(folder_path, output_filename)
    print(f"\nSaving to: {output_path}")
    
    combined_df.to_parquet(
        output_path,
        engine='pyarrow',
        compression='snappy',
        index=False
    )
    
    file_size_mb = os.path.getsize(output_path) / (1024**2)
    elapsed_time = time.time() - start_time
    
    print(f"\n✓ Consolidation complete!")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Time: {elapsed_time:.2f} seconds")
    print(f"  Compression ratio: {combined_df.memory_usage(deep=True).sum() / os.path.getsize(output_path):.2f}x")
    
    if errors > 0:
        print(f"  Warnings: {errors} files had errors")
    
    # Print detailed summary
    print("\n" + "-"*80)
    print("SUMMARY STATISTICS")
    print("-"*80)
    print(f"Total files processed: {len(processed_files)}")
    print(f"Buildings: {combined_df['building_id'].nunique()}")
    print(f"Components: {sorted(combined_df['component'].unique())}")
    print(f"B Scenarios: {sorted(combined_df['b_scenario'].unique())}")
    print(f"Policy Scenarios: {sorted(combined_df['policy_scenario'].unique())}")
    print(f"Waste Scenarios: {sorted(combined_df['waste_scenario'].unique())}")
    print(f"Building Types: {sorted(combined_df['building_type'].unique())}")
    print(f"Indicators: {sorted(combined_df['indicator'].unique())}")
    
    # Show material names if present
    if 'material_name' in combined_df.columns:
        unique_materials = combined_df['material_name'].dropna().unique()
        if len(unique_materials) > 0:
            print(f"Materials found: {len(unique_materials)}")
            if len(unique_materials) <= 20:
                print(f"  {sorted(unique_materials)}")
    
    # Show component details if present
    if 'component_detail' in combined_df.columns:
        unique_details = combined_df['component_detail'].dropna().unique()
        if len(unique_details) > 0:
            print(f"Component details: {len(unique_details)}")
    
    # Show any unknown classifications
    unknown_components = len(combined_df[combined_df['component'] == 'Unknown'])
    if unknown_components > 0:
        print(f"\nWarning: {unknown_components} rows with unknown component")
    
    unknown_scenarios = len(combined_df[combined_df['b_scenario'] == 'Unknown'])
    if unknown_scenarios > 0:
        print(f"Warning: {unknown_scenarios} rows with unknown B scenario")
    
    print("-"*80)
    
    # Delete individual files if requested
    if delete_individual and len(processed_files) > 0:
        print("\n" + "-"*80)
        print("CLEANING UP: Deleting individual Parquet files...")
        print("-"*80)
        
        deleted_count = 0
        delete_errors = 0
        
        for filename in processed_files:
            try:
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)
                deleted_count += 1
                
                if deleted_count % 100 == 0:
                    print(f"Deleted {deleted_count}/{len(processed_files)} files...")
                    
            except Exception as e:
                delete_errors += 1
                if delete_errors <= 3:
                    print(f"  Warning: Could not delete {filename}: {e}")
        
        print(f"\n✓ Cleanup complete!")
        print(f"  Deleted {deleted_count} individual files")
        
        if delete_errors > 0:
            print(f"  {delete_errors} files could not be deleted")
        
        # Calculate space saved
        original_size_mb = len(processed_files) * file_size_mb / len(all_data) if len(all_data) > 0 else 0
        print(f"  Approximate disk space saved: {original_size_mb - file_size_mb:.2f} MB")
    
    print("="*80 + "\n")
    
    return combined_df
#%%
def run_dlca_pipeline(
    building_list,
    buildingage_param,
    geography_param,
    dynamic_factor_param,
    phase_A4_param,
    phase_C_param,
    phase_B6_param,
    static_comparison_param,
    cumulative_param,
    years_param,
    LCIAindicator_param="GWP",
    LCIAindicator_dynamic_param="AGWP",
    dynamic_scenario_param="Carbon Neutral",
):
    global buildingage,geography, dynamic_factor, phase_A4, phase_C, phase_B6, static_comparison, cumulative
    global years, LCIAindicator, LCIAindicator_dynamic, dynamic_scenario
    global df_query_result_b1, df_query_result_b1_prep
    global df_query_result_b2_further, df_query_result_b2_influence, df_query_result_b2_base
    
    global df_query_result_b5_final_material, df_query_result_b5_final_waste, df_query_result_b5_dynamic_ratio, df_query_result_b5_energysource_amount
    global df_query_result_b4_final_material, df_query_result_b4_final_waste, df_query_result_b4_dynamic_ratio, df_query_result_b4_energysource_amount
    global df_query_result_b3_final_material, df_query_result_b3_final_waste, df_query_result_b3_dynamic_ratio, df_query_result_b3_energysource_amount
    
    global medium2low, medium_ratio_static, high2medium, high_ratio_static
    global df_query_result_b5_final_heat, df_query_result_b4_final_heat, df_query_result_b3_final_heat
    global df_query_result_b5_final_power, df_query_result_b4_final_power, df_query_result_b3_final_power
    global df_query_result_heat, df_query_result_powermix
    buildingage = buildingage_param
   
   
    raw_geo = geography_param[0] if isinstance(geography_param, (list, tuple)) and len(geography_param) > 0 else "EUROPE_GROUP"
    
    if raw_geo == "EUROPE_GROUP":
    
        geography = ("CH", "RER", "Europe without Austria", "IAI Area, EU27 & EFTA")
    elif raw_geo == "ROW":
        
        geography = ("RoW", "GLO")
    else:
        
        geography = ("CH", "RER", "Europe without Austria", "IAI Area, EU27 & EFTA")
        


    dynamic_factor = dynamic_factor_param
    phase_A4 = phase_A4_param
    phase_C = phase_C_param
    phase_B6 = phase_B6_param
    static_comparison = static_comparison_param
    cumulative = cumulative_param
    years = years_param
    LCIAindicator = LCIAindicator_param
    LCIAindicator_dynamic = LCIAindicator_dynamic_param
    dynamic_scenario = dynamic_scenario_param

    
    init_b7_resources(years_param=years, cumulative_param=cumulative)

    #%%
    #    # Conduction!
    df_query_result = read_db_basic(driver, URI, AUTH)
   
    globals()["df_query_result"] = df_query_result

    if phase_C == True:
        df_query_result_waste = read_db_waste(driver, URI, AUTH)
        globals()["df_query_result_waste"] = df_query_result_waste
    else:
        globals()["df_query_result_waste"] = None

    if phase_B6 == True:
        df_query_result_heat, df_query_result_powermix = read_db_heat_power(driver, URI, AUTH)
        
        globals()["df_query_result_heat"] = df_query_result_heat
    else:
        df_query_result_heat, df_query_result_powermix = None, None
        globals()["df_query_result_heat"] = None
    
    df_query_result_b2_further, df_query_result_b2_influence, df_query_result_b2_base = read_db_b2(
        dynamic_factor, driver, URI, AUTH
    )

    globals()["df_query_result_b2_further"] = df_query_result_b2_further
    globals()["df_query_result_b2_influence"] = df_query_result_b2_influence
    globals()["df_query_result_b2_base"] = df_query_result_b2_base

    df_query_result_b1, df_query_result_b1_prep = read_db_b1(dynamic_factor, driver, URI, AUTH, df_query_result)

    
    globals()["df_query_result_b1"] = df_query_result_b1
    globals()["df_query_result_b1_prep"] = df_query_result_b1_prep

    (
        df_query_result_b5_final_material,
        df_query_result_b5_final_waste,
        df_query_result_b5_dynamic_ratio,
        df_query_result_b5_energysource_amount,
        df_query_result_b4_final_material,
        df_query_result_b4_final_waste,
        df_query_result_b4_dynamic_ratio,
        df_query_result_b4_energysource_amount,
        medium2low,
        medium_ratio_static,
        df_query_result_b3_final_material,
        df_query_result_b3_final_waste,
        df_query_result_b3_dynamic_ratio,
        df_query_result_b3_energysource_amount,
        high2medium,
        high_ratio_static,
        df_query_result_b5_final_heat,
        df_query_result_b4_final_heat,
        df_query_result_b3_final_heat,
        df_query_result_b5_final_power,
        df_query_result_b4_final_power,
        df_query_result_b3_final_power,
    ) = read_db_b345(dynamic_factor, driver, URI, AUTH)

    df_query_result_b2_influence_ = df_query_result_b2_influence.copy() if df_query_result_b2_influence is not None else None
    df_query_result_b2_further_ = df_query_result_b2_further.copy() if df_query_result_b2_further is not None else None
    df_query_result_b1_ = df_query_result_b1.copy() if df_query_result_b1 is not None else None
    df_query_result_b5_final_material_ = (
        df_query_result_b5_final_material.copy() if df_query_result_b5_final_material is not None else None
    )
    df_query_result_b5_final_waste_ = (
        df_query_result_b5_final_waste.copy() if df_query_result_b5_final_waste is not None else None
    )
    df_query_result_b4_final_material_ = (
        df_query_result_b4_final_material.copy() if df_query_result_b4_final_material is not None else None
    )
    df_query_result_b4_final_waste_ = (
        df_query_result_b4_final_waste.copy() if df_query_result_b4_final_waste is not None else None
    )
    df_query_result_b3_final_material_ = (
        df_query_result_b3_final_material.copy() if df_query_result_b3_final_material is not None else None
    )
    df_query_result_b3_final_waste_ = (
        df_query_result_b3_final_waste.copy() if df_query_result_b3_final_waste is not None else None
    )

    df_query_result_b5_final_heat_ = df_query_result_b5_final_heat.copy() if df_query_result_b5_final_heat is not None else None
    df_query_result_b4_final_heat_ = df_query_result_b4_final_heat.copy() if df_query_result_b4_final_heat is not None else None
    df_query_result_b3_final_heat_ = df_query_result_b3_final_heat.copy() if df_query_result_b3_final_heat is not None else None

    df_query_result_b5_final_power_ = (
        df_query_result_b5_final_power.copy() if df_query_result_b5_final_power is not None else None
    )
    df_query_result_b4_final_power_ = (
        df_query_result_b4_final_power.copy() if df_query_result_b4_final_power is not None else None
    )
    df_query_result_b3_final_power_ = (
        df_query_result_b3_final_power.copy() if df_query_result_b3_final_power is not None else None
    )

    


    #%%
    # Building material level
    # For this level, building material name and the rough component group should be defined!
    if level == "Building_Material":
        df_query_result_calc = df_query_result[df_query_result["Building_Material"] == material_name][
            df_query_result["Building_Component"].str.contains(component_group)
        ].reset_index(drop=True)

        # try to skip other components
        if "B2" in dynamic_factor:
            df_query_result_b2_influence = df_query_result_b2_influence[
                df_query_result_b2_influence["Building_Material"] == material_name
            ][df_query_result["Building_Component"].str.contains(component_group)].reset_index(drop=True)
            df_query_result_b2_further = df_query_result_b2_further[
                df_query_result_b2_further["Building_Material"] == material_name
            ][df_query_result["Building_Component"].str.contains(component_group)].reset_index(drop=True)

        if "B1" in dynamic_factor:
            df_query_result_b1 = [
                sublist for sublist in df_query_result_b1 if component_group in sublist[1] and material_name in sublist[2]
            ]

        result_static = static_LCIA_material(df_query_result_calc, LCIAindicator, years)
        result_dynamic = dynamic_LCIA_b7_material(df_query_result_calc, LCIAindicator_dynamic, years, cumulative)

        # -------------------------------------------------
        # Adding waste to the cycle (C phases)
        if phase_C == True:
            df_query_result_waste_calc = df_query_result_waste[df_query_result_waste["Building_Material"] == material_name][
                df_query_result_waste["Building_Component"].str.contains(component_group)
            ].reset_index(drop=True)
            result_static_waste = static_LCIA_waste_material(df_query_result_waste_calc, LCIAindicator, years)

            result_dynamic_waste = dynamic_LCIA_b7_waste_material(
                df_query_result_waste_calc, LCIAindicator_dynamic, years, cumulative
            )

            # -------------------------------------------------
            # Sum of the material
            result_static_includingwaste = result_static + result_static_waste
            result_dynamic_includingwaste = dynamic_LCIA_b7_waste_resultcombi(
                building_id,
                result_dynamic_waste,
                years,
                result_dynamic,
                LCIAindicator_dynamic,
                cumulative,
                df_query_result_waste_calc.loc[0, "Building_Material"] + " including waste",
            )

    # Building component level
    # Either the exact component name should be given or the building construction type and component group should be given
    if level == "Building_Component":
        if component_name is not None:
            df_query_result_calc = df_query_result[df_query_result["Building_Component"].str.contains(component_name)].reset_index(
                drop=True
            )

            # Infer building_type from the component, used to filter dynamic-factor data
            inferred_building_type = df_query_result_calc.loc[0, "Building_Construction_Type"]

            # Restrict the main material dataframe to the inferred building type so
            # that static_LCIA_component's internal groupby(['Building_Material']).min()
            # aggregates within a single Building_Construction_Type.
            df_query_result_calc = df_query_result_calc[
                df_query_result_calc["Building_Construction_Type"] == inferred_building_type
            ].reset_index(drop=True)

            # try to skip other components
            if "B2" in dynamic_factor:
                df_query_result_b2_influence = df_query_result_b2_influence[
                    (df_query_result_b2_influence["Building_Component"].str.contains(component_name))
                    & (df_query_result_b2_influence["Building_Construction_Type"] == inferred_building_type)
                ].reset_index(drop=True)
                df_query_result_b2_further = df_query_result_b2_further[
                    (df_query_result_b2_further["Building_Component"].str.contains(component_name))
                    & (df_query_result_b2_further["Building_Construction_Type"] == inferred_building_type)
                ].reset_index(drop=True)

            if "B1" in dynamic_factor:
                df_query_result_b1 = [sublist for sublist in df_query_result_b1 if sublist[1] == component_name and sublist[0] == inferred_building_type]

            if "B5" in dynamic_factor or "B4" in dynamic_factor or "B3" in dynamic_factor or "power-2024" in dynamic_factor:
                df_query_result_b5_final_material = [
                    sublist for sublist in df_query_result_b5_final_material if sublist[1] == component_name and sublist[0] == inferred_building_type
                ]
                df_query_result_b5_final_waste = [
                    sublist for sublist in df_query_result_b5_final_waste if sublist[1] == component_name and sublist[0] == inferred_building_type
                ]
            if "B4" in dynamic_factor or "B3" in dynamic_factor or "power-2024" in dynamic_factor:
                df_query_result_b4_final_material = [
                    sublist for sublist in df_query_result_b4_final_material if sublist[1] == component_name and sublist[0] == inferred_building_type
                ]
                df_query_result_b4_final_waste = [
                    sublist for sublist in df_query_result_b4_final_waste if sublist[1] == component_name and sublist[0] == inferred_building_type
                ]
            if "B3" in dynamic_factor or "power-2024" in dynamic_factor:
                df_query_result_b3_final_material = [
                    sublist for sublist in df_query_result_b3_final_material if sublist[1] == component_name and sublist[0] == inferred_building_type
                ]
                df_query_result_b3_final_waste = [
                    sublist for sublist in df_query_result_b3_final_waste if sublist[1] == component_name and sublist[0] == inferred_building_type
                ]

        else:
            df_query_result_calc = df_query_result[
                df_query_result["Building_Construction_Type"].str.contains(building_type)
            ][df_query_result["Building_Component"].str.contains(component_group)].reset_index(drop=True)

            # try to skip other components
            if "B2" in dynamic_factor:
                df_query_result_b2_influence = df_query_result_b2_influence[
                    df_query_result_b2_influence["Building_Construction_Type"].str.contains(building_type)
                ][df_query_result["Building_Component"].str.contains(component_group)].reset_index(drop=True)
                df_query_result_b2_further = df_query_result_b2_further[
                    df_query_result_b2_further["Building_Construction_Type"].str.contains(building_type)
                ][df_query_result["Building_Component"].str.contains(component_group)].reset_index(drop=True)

            if "B1" in dynamic_factor:
                df_query_result_b1 = [
                    sublist
                    for sublist in df_query_result_b1
                    if sublist[0] == building_type and sublist[1].str.contains(component_group)
                ]

            if "B5" in dynamic_factor or "B4" in dynamic_factor or "B3" in dynamic_factor or "power-2024" in dynamic_factor:
                df_query_result_b5_final_material = [
                    sublist
                    for sublist in df_query_result_b5_final_material
                    if sublist[0] == building_type and sublist[1].str.contains(component_group)
                ]
                df_query_result_b5_final_waste = [
                    sublist
                    for sublist in df_query_result_b5_final_waste
                    if sublist[0] == building_type and sublist[1].str.contains(component_group)
                ]
            if "B4" in dynamic_factor or "B3" in dynamic_factor or "power-2024" in dynamic_factor:
                df_query_result_b4_final_material = [
                    sublist
                    for sublist in df_query_result_b4_final_material
                    if sublist[0] == building_type and sublist[1].str.contains(component_group)
                ]
                df_query_result_b4_final_waste = [
                    sublist
                    for sublist in df_query_result_b4_final_waste
                    if sublist[0] == building_type and sublist[1].str.contains(component_group)
                ]
            if "B3" in dynamic_factor or "power-2024" in dynamic_factor:
                df_query_result_b3_final_material = [
                    sublist
                    for sublist in df_query_result_b3_final_material
                    if sublist[0] == building_type and sublist[1].str.contains(component_group)
                ]
                df_query_result_b3_final_waste = [
                    sublist
                    for sublist in df_query_result_b3_final_waste
                    if sublist[0] == building_type and sublist[1].str.contains(component_group)
                ]

        result_static = static_LCIA_component(
            df_query_result_calc, LCIAindicator, years, component_area, False, component_name
        )
        result_dynamic = dynamic_LCIA_b7_component(
            building_id, df_query_result_calc, LCIAindicator_dynamic, years, cumulative, component_area, "-", component_name
        )

        # -------------------------------------------------
        # Adding waste to the cycle (C phases)
        if phase_C == True:
            if component_name is not None:
                df_query_result_waste_calc = df_query_result_waste[
                    (df_query_result_waste["Building_Component"].str.contains(component_name))
                    & (df_query_result_waste["Building_Construction_Type"] == inferred_building_type)
                ].reset_index(drop=True)

            else:
                df_query_result_waste_calc = df_query_result_waste[
                    df_query_result_waste["Building_Construction_Type"].str.contains(building_type)
                ][df_query_result_waste["Building_Component"].str.contains(component_group)].reset_index(drop=True)

            result_static_waste = static_LCIA_waste_component(df_query_result_waste_calc, LCIAindicator, years, component_area)
            result_dynamic_waste = dynamic_LCIA_b7_waste_component(
                building_id, df_query_result_waste_calc, LCIAindicator_dynamic, years, cumulative, component_area
            )

            # -------------------------------------------------
            # Sum of the material
            result_static_includingwaste = result_static + result_static_waste

            result_dynamic_includingwaste = dynamic_LCIA_b7_waste_resultcombi(
                building_id,
                result_dynamic_waste,
                years,
                result_dynamic,
                LCIAindicator_dynamic,
                cumulative,
                df_query_result_waste_calc.loc[0, "Building_Component"] + " including waste",
            )

    # Building level
    if level == "Building":

        # Pre-compute dynamic factor conditions to avoid repeated string operations
        needs_b2 = "B2" in dynamic_factor
        needs_b1 = "B1" in dynamic_factor
        needs_b5_b4_b3 = any(x in dynamic_factor for x in ["B5", "B4", "B3", "power-2024"])
        needs_b4_b3 = any(x in dynamic_factor for x in ["B4", "B3", "power-2024"])
        needs_b3 = any(x in dynamic_factor for x in ["B3", "power-2024"])

        # Get unique building types for pre-filtering
        building_types = list(set(building["building_type"] for building in building_list))

        heat_types = list(set(building["heating_system"] for building in building_list))
        power_types = list(set(building["power_system"] for building in building_list))

        # Pre-filter all dataframes by building types to avoid repeated operations
        filtered_dataframes = {}

        # Pre-filter B2 dataframes if needed
        if needs_b2:
            if df_query_result_b2_influence_ is not None:
                filtered_dataframes["b2_influence"] = {}
                for building_type in building_types:
                    mask = df_query_result_b2_influence_["Building_Construction_Type"].str.contains(
                        building_type, na=False
                    )
                    filtered_dataframes["b2_influence"][building_type] = df_query_result_b2_influence_[mask].reset_index(
                        drop=True
                    )

            if df_query_result_b2_further_ is not None:
                filtered_dataframes["b2_further"] = {}
                for building_type in building_types:
                    mask = df_query_result_b2_further_["Building_Construction_Type"].str.contains(
                        building_type, na=False
                    )
                    filtered_dataframes["b2_further"][building_type] = df_query_result_b2_further_[mask].reset_index(
                        drop=True
                    )

        # Pre-filter B1 lists if needed
        if needs_b1 and df_query_result_b1_ is not None:
            filtered_dataframes["b1"] = {}
            for building_type in building_types:
                filtered_dataframes["b1"][building_type] = [
                    sublist for sublist in df_query_result_b1_ if sublist[0] == building_type
                ]

        # Pre-filter B5 lists if needed
        if needs_b5_b4_b3:
            if df_query_result_b5_final_material_ is not None:
                filtered_dataframes["b5_material"] = {}
                for building_type in building_types:
                    filtered_dataframes["b5_material"][building_type] = [
                        sublist for sublist in df_query_result_b5_final_material_ if sublist[0] == building_type
                    ]

            if df_query_result_b5_final_waste_ is not None:
                filtered_dataframes["b5_waste"] = {}
                for building_type in building_types:
                    filtered_dataframes["b5_waste"][building_type] = [
                        sublist for sublist in df_query_result_b5_final_waste_ if sublist[0] == building_type
                    ]

        # Pre-filter B4 lists if needed
        if needs_b4_b3:
            if df_query_result_b4_final_material_ is not None:
                filtered_dataframes["b4_material"] = {}
                for building_type in building_types:
                    filtered_dataframes["b4_material"][building_type] = [
                        sublist for sublist in df_query_result_b4_final_material_ if sublist[0] == building_type
                    ]

            if df_query_result_b4_final_waste_ is not None:
                filtered_dataframes["b4_waste"] = {}
                for building_type in building_types:
                    filtered_dataframes["b4_waste"][building_type] = [
                        sublist for sublist in df_query_result_b4_final_waste_ if sublist[0] == building_type
                    ]

        # Pre-filter B3 lists if needed
        if needs_b3:
            if df_query_result_b3_final_material_ is not None:
                filtered_dataframes["b3_material"] = {}
                for building_type in building_types:
                    filtered_dataframes["b3_material"][building_type] = [
                        sublist for sublist in df_query_result_b3_final_material_ if sublist[0] == building_type
                    ]

            if df_query_result_b3_final_waste_ is not None:
                filtered_dataframes["b3_waste"] = {}
                for building_type in building_types:
                    filtered_dataframes["b3_waste"][building_type] = [
                        sublist for sublist in df_query_result_b3_final_waste_ if sublist[0] == building_type
                    ]

        # Pre-filter powermix and heat dataframes for B6 phase if needed
        if phase_B6:
            # Get unique power and heat systems
            power_systems = list(set(building["power_system"] for building in building_list))
            heat_systems = list(set(building["heating_system"] for building in building_list))

            # Pre-filter powermix dataframe
            filtered_dataframes["powermix"] = {}
            for power_system in power_systems:
                mask = df_query_result_powermix["Powermix"] == power_system
                filtered_dataframes["powermix"][power_system] = df_query_result_powermix[mask].reset_index(drop=True)

            # Pre-filter heat dataframe
            filtered_dataframes["heat"] = {}
            for heat_system in heat_systems:
                mask = df_query_result_heat["Energysource"] == heat_system
                filtered_dataframes["heat"][heat_system] = df_query_result_heat[mask].reset_index(drop=True)

            # Pre-filter B5 lists if needed
            if needs_b5_b4_b3:
                if df_query_result_b5_final_heat_ is not None:
                    filtered_dataframes["b5_heat"] = {}
                    for heat_type in heat_types:
                        filtered_dataframes["b5_heat"][heat_type] = [
                            sublist for sublist in df_query_result_b5_final_heat_ if sublist[1] == heat_type
                        ]

                if df_query_result_b5_final_power_ is not None:
                    filtered_dataframes["b5_power"] = {}
                    for power_type in power_types:
                        filtered_dataframes["b5_power"][power_type] = [
                            sublist for sublist in df_query_result_b5_final_power_ if sublist[1] == power_type
                        ]

            # Pre-filter B4 lists if needed
            if needs_b4_b3:
                if df_query_result_b4_final_heat_ is not None:
                    filtered_dataframes["b4_heat"] = {}
                    for heat_type in heat_types:
                        filtered_dataframes["b4_heat"][heat_type] = [
                            sublist for sublist in df_query_result_b4_final_heat_ if sublist[1] == heat_type
                        ]

                if df_query_result_b4_final_power_ is not None:
                    filtered_dataframes["b4_power"] = {}
                    for power_type in power_types:
                        filtered_dataframes["b4_power"][power_type] = [
                            sublist for sublist in df_query_result_b4_final_power_ if sublist[1] == power_type
                        ]

            # Pre-filter B3 lists if needed
            if needs_b3:
                if df_query_result_b3_final_heat_ is not None:
                    filtered_dataframes["b3_heat"] = {}
                    for heat_type in heat_types:
                        filtered_dataframes["b3_heat"][heat_type] = [
                            sublist for sublist in df_query_result_b3_final_heat_ if sublist[1] == heat_type
                        ]

                if df_query_result_b3_final_power_ is not None:
                    filtered_dataframes["b3_power"] = {}
                    for power_type in power_types:
                        filtered_dataframes["b3_power"][power_type] = [
                            sublist for sublist in df_query_result_b3_final_power_ if sublist[1] == power_type
                        ]

        result_building_list = []

        for building in building_list:

            result_building_list_temp = {}
            result_dynamic_collect = []
            result_dynamic_waste_collect = []

            building_id = building["building_id"]
            building_type = building["building_type"]
            all_components = building["building_components"]
            all_components_area = building["building_components_area"]

            consumption_power = building["consumption_power"]
            consumption_heat = building["consumption_heat"]
            power_type = building["power_system"]
            heat_type = building["heating_system"]
            total_floor_area = building["total_floor_area"]

            # Get pre-filtered dataframes for this building type
            if needs_b2:
                if "b2_influence" in filtered_dataframes and building_type in filtered_dataframes["b2_influence"]:
                    df_query_result_b2_influence = filtered_dataframes["b2_influence"][building_type]
                if "b2_further" in filtered_dataframes and building_type in filtered_dataframes["b2_further"]:
                    df_query_result_b2_further = filtered_dataframes["b2_further"][building_type]

            if needs_b1:
                if "b1" in filtered_dataframes and building_type in filtered_dataframes["b1"]:
                    df_query_result_b1 = filtered_dataframes["b1"][building_type]

            if needs_b5_b4_b3:
                if "b5_material" in filtered_dataframes and building_type in filtered_dataframes["b5_material"]:
                    df_query_result_b5_final_material = filtered_dataframes["b5_material"][building_type]
                if "b5_waste" in filtered_dataframes and building_type in filtered_dataframes["b5_waste"]:
                    df_query_result_b5_final_waste = filtered_dataframes["b5_waste"][building_type]

                if "b5_heat" in filtered_dataframes and heat_type in filtered_dataframes["b5_heat"]:
                    df_query_result_b5_final_heat = filtered_dataframes["b5_heat"][heat_type]
                if "b5_power" in filtered_dataframes and power_type in filtered_dataframes["b5_power"]:
                    df_query_result_b5_final_power = filtered_dataframes["b5_power"][power_type]

            if needs_b4_b3:
                if "b4_material" in filtered_dataframes and building_type in filtered_dataframes["b4_material"]:
                    df_query_result_b4_final_material = filtered_dataframes["b4_material"][building_type]
                if "b4_waste" in filtered_dataframes and building_type in filtered_dataframes["b4_waste"]:
                    df_query_result_b4_final_waste = filtered_dataframes["b4_waste"][building_type]

                if "b4_heat" in filtered_dataframes and heat_type in filtered_dataframes["b4_heat"]:
                    df_query_result_b4_final_heat = filtered_dataframes["b4_heat"][heat_type]
                if "b4_power" in filtered_dataframes and power_type in filtered_dataframes["b4_power"]:
                    df_query_result_b4_final_power = filtered_dataframes["b4_power"][power_type]

            if needs_b3:
                if "b3_material" in filtered_dataframes and building_type in filtered_dataframes["b3_material"]:
                    df_query_result_b3_final_material = filtered_dataframes["b3_material"][building_type]
                if "b3_waste" in filtered_dataframes and building_type in filtered_dataframes["b3_waste"]:
                    df_query_result_b3_final_waste = filtered_dataframes["b3_waste"][building_type]

                if "b3_heat" in filtered_dataframes and heat_type in filtered_dataframes["b3_heat"]:
                    df_query_result_b3_final_heat = filtered_dataframes["b3_heat"][heat_type]
                if "b3_power" in filtered_dataframes and power_type in filtered_dataframes["b3_power"]:
                    df_query_result_b3_final_power = filtered_dataframes["b3_power"][power_type]

            # Main calculations
            result_static = static_LCIA_building(
                building_type, all_components, all_components_area, LCIAindicator, years
            )
            
            
            result_dynamic_tuple = dynamic_LCIA_b7_building(
                building_id,
                building_type,
                all_components,
                all_components_area,
                LCIAindicator_dynamic,
                years,
                cumulative,
            )
            if isinstance(result_dynamic_tuple, tuple):
                result_dynamic = result_dynamic_tuple[0]
                result_dynamic_collect = result_dynamic_tuple[1]
            else:
                result_dynamic = result_dynamic_tuple

            result_building_list_temp["building_id"] = building_id
            result_building_list_temp["result_static"] = float(result_static)
            result_building_list_temp["result_dynamic"] = result_dynamic
            result_building_list_temp["total_floor_area"] = total_floor_area
            result_building_list_temp["building_type"] = building_type
            result_building_list_temp["heat_type"] = heat_type
            result_building_list_temp["power_type"] = power_type

            # Process waste (C phases) if needed
            if phase_C:
                result_static_waste = static_LCIA_waste_building(
                    building_type, all_components, all_components_area, LCIAindicator, years
                )
                result_dynamic_waste = dynamic_LCIA_b7_waste_building(
                    building_id,
                    building_type,
                    all_components,
                    all_components_area,
                    LCIAindicator_dynamic,
                    years,
                    cumulative,
                )

                result_static_includingwaste = result_static + result_static_waste

                # STATIC COMPARISON
                if static_comparison:
                    result_dynamic_includingwaste = result_dynamic + result_dynamic_waste
                # STATIC COMPARISON
                else:
                    result_dynamic_waste_collect = result_dynamic_waste.copy() if isinstance(result_dynamic_waste, list) else []
                    result_dynamic_waste_building = sum(item[1] for item in result_dynamic_waste)
                    result_dynamic_waste = result_dynamic_waste_building
                    result_dynamic_waste_building = [["Waste", result_dynamic_waste_building]]
                    result_dynamic_includingwaste = dynamic_LCIA_b7_waste_resultcombi(
                        building_id,
                        result_dynamic_waste_building,
                        years,
                        result_dynamic,
                        LCIAindicator_dynamic,
                        cumulative,
                        building_type + " including waste",
                    )

                result_building_list_temp["result_static_waste"] = float(result_static_waste)
                result_building_list_temp["result_dynamic_waste"] = result_dynamic_waste
                result_building_list_temp["result_static_includingwaste"] = float(result_static_includingwaste)
                result_building_list_temp["result_dynamic_includingwaste"] = result_dynamic_includingwaste

            # Process B6 phase if needed
            if phase_B6:
                # Get pre-filtered dataframes or filter on-demand
                if "powermix" in filtered_dataframes and power_type in filtered_dataframes["powermix"]:
                    df_query_result_calc_powermix = filtered_dataframes["powermix"][power_type]
                else:
                    df_query_result_calc_powermix = df_query_result_powermix[
                        df_query_result_powermix["Powermix"] == power_type
                    ].reset_index(drop=True)

                if "heat" in filtered_dataframes and heat_type in filtered_dataframes["heat"]:
                    df_query_result_calc_heat = filtered_dataframes["heat"][heat_type]
                else:
                    df_query_result_calc_heat = df_query_result_heat[
                        df_query_result_heat["Energysource"] == heat_type
                    ].reset_index(drop=True)

                result_static_powermix = static_LCIA_b6(
                    consumption_power, df_query_result_calc_powermix, LCIAindicator, years
                )
                result_dynamic_powermix = dynamic_LCIA_b7_b6(
                    consumption_power,
                    building_id,
                    df_query_result_calc_powermix,
                    LCIAindicator_dynamic,
                    years,
                    cumulative,
                    power_type,
                )

                result_static_heat = static_LCIA_b6(
                    consumption_heat, df_query_result_calc_heat, LCIAindicator, years
                )
                result_dynamic_heat = dynamic_LCIA_b7_b6(
                    consumption_heat,
                    building_id,
                    df_query_result_calc_heat,
                    LCIAindicator_dynamic,
                    years,
                    cumulative,
                    heat_type,
                )

                result_building_list_temp["result_static_powermix"] = float(result_static_powermix)
                result_building_list_temp["result_dynamic_powermix"] = result_dynamic_powermix
                result_building_list_temp["result_static_heat"] = float(result_static_heat)
                result_building_list_temp["result_dynamic_heat"] = result_dynamic_heat

            
            try:
                def safe_tolist(series):
                    if isinstance(series, pd.Series):
                        return series.iloc[::10].tolist()
                    return []

                all_charts = {
                    "components": {},  
                    "waste": {},       
                    "energy": {},     
                    "totals": {}       
                }

                
                for comp_name, comp_series in result_dynamic_collect:
                    all_charts["components"][comp_name] = safe_tolist(comp_series)
                
                all_charts["totals"]["base_materials"] = safe_tolist(result_dynamic)

                
                if phase_C:
                    for waste_name, waste_series in result_dynamic_waste_collect:
                        all_charts["waste"][waste_name] = safe_tolist(waste_series)
                    
                    if isinstance(result_dynamic_waste, pd.Series):
                        all_charts["totals"]["waste_total"] = safe_tolist(result_dynamic_waste)
                    
                    if "result_dynamic_includingwaste" in result_building_list_temp:
                        all_charts["totals"]["base_and_waste"] = safe_tolist(result_building_list_temp["result_dynamic_includingwaste"])

                
                if phase_B6:
                    if "result_dynamic_powermix" in result_building_list_temp and isinstance(result_building_list_temp["result_dynamic_powermix"], pd.Series):
                        all_charts["energy"]["Power"] = safe_tolist(result_building_list_temp["result_dynamic_powermix"])
                    if "result_dynamic_heat" in result_building_list_temp and isinstance(result_building_list_temp["result_dynamic_heat"], pd.Series):
                        all_charts["energy"]["Heat"] = safe_tolist(result_building_list_temp["result_dynamic_heat"])

                
                total_series = result_dynamic.copy() if isinstance(result_dynamic, pd.Series) else pd.Series(0, range(0,years*10+1))
                if phase_C and "result_dynamic_includingwaste" in result_building_list_temp:
                    if isinstance(result_building_list_temp["result_dynamic_includingwaste"], pd.Series):
                        total_series = result_building_list_temp["result_dynamic_includingwaste"].copy()
                if phase_B6:
                    if "result_dynamic_powermix" in result_building_list_temp and isinstance(result_building_list_temp["result_dynamic_powermix"], pd.Series):
                        total_series += result_building_list_temp["result_dynamic_powermix"]
                    if "result_dynamic_heat" in result_building_list_temp and isinstance(result_building_list_temp["result_dynamic_heat"], pd.Series):
                        total_series += result_building_list_temp["result_dynamic_heat"]
                
                all_charts["totals"]["grand_total"] = safe_tolist(total_series)

                
                result_building_list_temp["yearly_data"] = all_charts["totals"]["grand_total"]
                result_building_list_temp["all_charts_data"] = all_charts

            except Exception as e:
                import traceback
                print(f"Failed to build all_charts_data: {e}")
                traceback.print_exc()
                result_building_list_temp["all_charts_data"] = {}
                result_building_list_temp["yearly_data"] = []
          
            global PDF_CHART_DATA
            result_building_list_temp["pdf_components"] = dict(PDF_CHART_DATA)
            PDF_CHART_DATA.clear() 
           
 
            result_building_list.append(result_building_list_temp)

    
    return result_building_list
        
        