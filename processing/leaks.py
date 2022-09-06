from datetime import datetime
import numpy as np
from pickle import dump as p_dump
import json
from pandas import merge
from processing.outputs import clean_sim_df, agg_flatten


def process(sim_outputs, CACHE_DIR, p_baseline):
    meta_cols = [
        {'in': 'NRd', 'out': 'NRd', 'type': int},
        {'in': 'start_date', 'out': 'prog_start_date', 'type': datetime},
    ]
    params = [
        {'in': 'leak_ID', 'out': 'leak_ID', 'type': str},
        {'in': 'facility_ID', 'out': 'facility_ID', 'type': str},
        {'in': 'days_active', 'out': 'days_active', 'type': int},
        {'in': 'date_began', 'out': 'date_began'},
        {'in': 'date_repaired', 'out': 'date_repaired'},
        {'in': 'init_detect_by', 'out': 'init_detect_by'},
        {'in': 'volume', 'out': 'volume_kg'},
        {'in': 'estimated_volume', 'out': 'estimated_volume_kg'},
        {'in': 'estimated_volume_b', 'out': 'estimated_volume_kg_b'},
        {'in': 'rate', 'out': 'rate_kg_day', 'type': float, 'xfac': 86.4},
    ]
    prog_leaks = clean_sim_df(sim_outputs, 'leaks', index='leak_ID',
                              params=params, aggregate=False, add_meta_cols=meta_cols)

    # Remove emissions from leaks prior to to start of program
    prog_leaks['prog_leak_start_dif'] = (
        prog_leaks['date_began']-prog_leaks['prog_start_date']).dt.days
    prog_leaks['days_active'] = np.where(
        prog_leaks['prog_leak_start_dif'] < 0,
        prog_leaks['days_active'] + prog_leaks['prog_leak_start_dif'],
        prog_leaks['days_active'])
    prog_leaks.drop(columns=['prog_leak_start_dif', 'prog_start_date'])

    # --- Total Leak volume and mitigated emissions volume ---
    prog_leaks['volume_kg'] = prog_leaks['rate_kg_day'] * \
        prog_leaks['days_active']

    # Calculate the leak emissions in absense of formal LDAR and the mitigated emissions from
    # Formal LDAR.
    natural = prog_leaks[prog_leaks['program_name'] == p_baseline][
        ["leak_ID", "sim", 'volume_kg']] \
        .rename(columns={'volume_kg': 'nat_volume_kg'})
    prog_leaks = merge(prog_leaks, natural, how='left', on=["leak_ID", "sim"])
    prog_leaks['mit_volume_kg'] = prog_leaks['nat_volume_kg'] - \
        prog_leaks['volume_kg']
    prog_leaks['init_detect_by'] = prog_leaks['init_detect_by'].replace([
                                                                        None], 'active')
    
    json.dump(prog_leaks.to_json(), open(CACHE_DIR / "leaks.json", "w"))

    response_companies = list(prog_leaks['init_detect_by'].unique())


    # ---- Get Method Level mitigatied emissions ----
    for comp in response_companies:
        prog_leaks[comp] = np.where(prog_leaks.init_detect_by == comp,
                                    prog_leaks['mit_volume_kg'], np.nan)
   
    # Should Replace this to consider indivual sims
    return prog_leaks
