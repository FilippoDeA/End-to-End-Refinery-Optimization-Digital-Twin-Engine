import pandas as pd
import math
import clr
import sys
from scipy.optimize import linprog

# =====================================================================
# SECTION 1: DWSIM INITIALIZATION & PROPERTY EXTRACTION
# =====================================================================
print("1. Initializing DWSIM Headless Engine...")
dwsim_path = r"C:\Users\user_name\AppData\Local\DWSIM"
sys.path.append(dwsim_path)

clr.AddReference("DWSIM.Automation")
from DWSIM.Automation import Automation3

interf = Automation3()
flowsheet_path = r"C:\Users\...\Blending_Model.dwxmz"
flowsheet = interf.LoadFlowsheet(flowsheet_path)

print("2. Flowsheet loaded. Simulating stream properties...")
interf.CalculateFlowsheet2(flowsheet)

naphtha = flowsheet.GetFlowsheetSimulationObject("Straight-run Naphtha").GetAsObject()
reformate = flowsheet.GetFlowsheetSimulationObject("Reformate").GetAsObject()
alkylate = flowsheet.GetFlowsheetSimulationObject("Alkylate").GetAsObject()
butane = flowsheet.GetFlowsheetSimulationObject("Butane").GetAsObject()

def get_stream_rvp(stream_obj, default_psi):
    try:
        rvp_pascal = stream_obj.GetPhase("Mixture").Properties.reid_vapor_pressure
        return round(rvp_pascal * 0.000145038, 2)
    except Exception:
        return default_psi

def get_stream_ron(stream_obj, default_ron):
    try:
        return round(stream_obj.GetPropertyValue("ResearchOctaneNumber"), 1)
    except Exception:
        return default_ron

assay_rvp_psi = [
    get_stream_rvp(naphtha, 11.5),
    get_stream_rvp(reformate, 3.2),
    get_stream_rvp(alkylate, 1.8),
    get_stream_rvp(butane, 52.0)
]

ron_specs = [
    get_stream_ron(naphtha, 65.0),
    get_stream_ron(reformate, 98.5),
    get_stream_ron(alkylate, 94.0),
    get_stream_ron(butane, 94.0)
]

# =====================================================================
# SECTION 2: READ DAILY TIME-SERIES PRICES
# =====================================================================
prices_df = pd.read_csv(r"C:\Users\...\live_prices.csv")
prices_df['Date'] = pd.to_datetime(prices_df['Date'])

# =====================================================================
# SECTION 3: OPTIMIZER ENGINE (SciPy)
# =====================================================================
rvp_indices = [math.pow(rvp, 1.25) for rvp in assay_rvp_psi]

def run_blending_optimizer(prices, ron_specs, rvp_idx, inventories, batch_size, target_ron=87.0, target_rvp_max=9.0):
    c = prices
    target_rvp_index = target_rvp_max ** 1.25
    A_ub = [[-ron for ron in ron_specs], rvp_idx]
    b_ub = [-target_ron, target_rvp_index]
    A_eq = [[1.0] * len(prices)]
    b_eq = [1.0]
    
    bounds = [(0, min(1.0, inv/batch_size)) for inv in inventories]
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if result.success: 
        return {"cost_per_barrel": round(result.fun, 2), "volumes": [round(x, 4) for x in result.x]}
    else: 
        return {"cost_per_barrel": sum(prices)/len(prices), "volumes": [0.25, 0.25, 0.25, 0.25]}

# =====================================================================
# SECTION 4: POWER BI LOOP WITH CONTINUOUS SINEWAVE RVP
# =====================================================================
destinations_list = ['PADD1_NY', 'ARA_Rotterdam', 'Mexico_Tuxpan', 'Brazil_Santos', 'WAF_Lagos', 'Singapore', 'AG_Fujairah']
components = ['Straight-run Naphtha', 'Reformate', 'Alkylate', 'Butane']
batch_size = 100000.0
inventories = [80000.0, 40000.0, 70000.0, 20000.0]

fact_commercial_trades = []
fact_refinery_tanks = []


for index, row in prices_df.iterrows():
    date_obj = row['Date']
    date_str = date_obj.strftime('%Y-%m-%d')
    current_wti = row['WTI_Crude']
    current_rbob = row['RBOB_Gasoline']
    
    day_of_year = date_obj.dayofyear
            
    dynamic_spot_prices = [
        round(current_wti * 1.05, 2),   
        round(current_rbob * 1.08, 2),  
        round(current_rbob * 1.12, 2),  
        round(current_wti * 0.60, 2)    
    ]
    
    # Calculate daily pricing margins for global markets
    market_dynamics = {
        'PADD1_NY':      {'base': current_rbob * 1.044, 'wave_speed': 2.0, 'offset': 0.0, 'volatility': 4.5, 'freight': 0.51, 'rvp_offset': 0},
        'ARA_Rotterdam': {'base': current_rbob * 1.024, 'wave_speed': 1.8, 'offset': 1.5, 'volatility': 5.2, 'freight': 1.33, 'rvp_offset': 0},
        'Mexico_Tuxpan': {'base': current_rbob * 1.072, 'wave_speed': 2.2, 'offset': 0.7, 'volatility': 3.0, 'freight': 0.12, 'rvp_offset': 0},
        'Brazil_Santos': {'base': current_rbob * 1.084, 'wave_speed': 1.5, 'offset': 2.3, 'volatility': 6.0, 'freight': 1.23, 'rvp_offset': math.pi},
        'WAF_Lagos':     {'base': current_rbob * 1.078, 'wave_speed': 2.0, 'offset': 3.1, 'volatility': 4.0, 'freight': 1.47, 'rvp_offset': 0},
        'Singapore':     {'base': current_rbob * 1.032, 'wave_speed': 2.5, 'offset': 4.2, 'volatility': 5.5, 'freight': 2.81, 'rvp_offset': 0},
        'AG_Fujairah':   {'base': current_rbob * 1.028, 'wave_speed': 2.1, 'offset': 3.8, 'volatility': 5.0, 'freight': 2.45, 'rvp_offset': 0}
    }
    
    for dest in destinations_list:
        cfg = market_dynamics[dest]

        # CONTINUOUS COSINE RVP WAVE: 
        # Perfectly seamless at year-end boundaries, peaks in winter (~13.8), troughs in summer (~7.8)
        days_in_year = 366.0 if date_obj.is_leap_year else 365.0
        angle = (2.0 * math.pi * day_of_year) / days_in_year + cfg['rvp_offset']
        target_rvp_max = round(10.8 + 3.0 * math.cos(angle), 2)
        
        # Solve daily blend math
        optimal_mix = run_blending_optimizer(
            dynamic_spot_prices, 
            ron_specs, 
            rvp_indices, 
            inventories,
            batch_size,
            target_ron=87.0, 
            target_rvp_max=target_rvp_max
        )

        # Clean continuous multi-year destination price waves using index
        market_price = round(cfg['base'] + (math.sin((index * cfg['wave_speed']) / 58.0 + cfg['offset']) * cfg['volatility']), 2)
        # 1. Populate Trades Fact Table (1 row per Date/Dest)
        fact_commercial_trades.append([
            date_str, dest, market_price, cfg['freight'], optimal_mix['cost_per_barrel'], target_rvp_max
        ])

        # 2. Populate Tanks Fact Table (4 rows per Date/Dest)
        for comp, frac, cap, comp_price in zip(components, optimal_mix['volumes'], inventories, dynamic_spot_prices):
            used_bbl = frac * batch_size
            utilization_pct = round(used_bbl / cap, 4)
            is_constrained = 1 if utilization_pct >= 0.99 else 0
            
            fact_refinery_tanks.append([
                date_str, dest, comp, comp_price, used_bbl, cap, frac, utilization_pct, is_constrained
            ])

df_fact_trades = pd.DataFrame(
    fact_commercial_trades, 
    columns=['Date', 'Destination', 'Market_Spot_Price_bbl', 'Freight_Cost_bbl', 'Optimized_Blend_Cost_bbl', 'Target_RVP_Limit']
)

df_fact_tanks = pd.DataFrame(
    fact_refinery_tanks, 
    columns=['Date', 'Destination', 'Component', 'Component_Spot_Price_bbl', 'Used_Volume_bbl', 'Tank_Capacity_bbl', 'Volume_Fraction', 'Capacity_Utilization_Pct', 'Is_Bottleneck']
)

# Optional: Export to CSV for Power BI Import
# df_fact_trades.to_csv('fact_commercial_trades.csv', index=False)
# df_fact_tanks.to_csv('fact_refinery_tanks.csv', index=False)
