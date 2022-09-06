
import fnmatch
from numpy import median
from pickle import dump as p_dump
import json
from processing.outputs import add_ts_ref, clean_sim_df, agg_flatten


def process(sim_outputs, sim_params, CACHE_DIR):

    cost_col_filt = "*_cost"
    travel_col_filt = "*_travel_time"
    survey_col_filt = "*_survey_time"
    cost_cols = set()
    travel_cols = set()
    survey_cols = set()
    for sim in sim_outputs:
        cost_cols.update(fnmatch.filter(
            list(sim['timeseries'].columns), cost_col_filt))
        travel_cols.update(fnmatch.filter(
            list(sim['timeseries'].columns), travel_col_filt))
        survey_cols.update(fnmatch.filter(
            list(sim['timeseries'].columns), survey_col_filt))
    cost_params = [{'in': col, 'out': col, 'type': float}
                   for col in cost_cols if col != 'total_daily_cost']
    survey_params = [{'in': col, 'out': col, 'type': float}
                     for col in survey_cols if col != 'total_daily_cost']
    travel_params = [{'in': col, 'out': col, 'type': float}
                     for col in travel_cols if col != 'total_daily_cost']

    prog_ts = clean_sim_df(sim_outputs, 'timeseries', index='ts', params=[
        {'in': 'daily_emissions_kg', 'out': 'emis_kg_day', 'type': float},
        {'in': 'active_leaks', 'out': 'active_leaks_day', 'type': float},
        {'in': 'total_daily_cost', 'out': 'cost_day', 'type': float},
    ] + cost_params + survey_params + travel_params, aggregate=False)

    prog_ts = add_ts_ref(prog_ts, sim_params['baseline_program'], suffix='none',
                         ref_cols=['emis_kg_day', 'cost_day'],
                         merge_on=['ts', 'sim'], calcs=['dif'])

    json.dump(prog_ts.to_json(), open(CACHE_DIR / "timeseries.json", "w"))
    return prog_ts
