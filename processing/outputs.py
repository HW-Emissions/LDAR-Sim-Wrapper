from datetime import datetime
from pandas import concat, merge, DataFrame


def clean_sim_df(sim_results, df,  index='index', params=[], aggregate=True, add_meta_cols=[]):
    p_arr = []
    meta_cols = [
        {'in': 'simulation', 'out': 'sim', 'type': int},
        {'in': 'program_name', 'out': 'program_name', 'type': str},
    ] + add_meta_cols
    if len(params) > 0:
        p_cols = [c['in'] for c in params]
    # in_cols = [m['in'] for m in params]
    for sim in sim_results:
        if len(params) > 0:
            copy_cols = set(list(sim[df].columns)).intersection(set(p_cols))
            p_obj = sim[df].copy()[copy_cols]
        else:
            p_obj = sim[df].copy()
        if index not in p_obj.columns:
            p_obj[index] = p_obj.index
        p_obj = p_obj.set_index(index)
        # --- Add metadata --
        for col in meta_cols:
            if col['type'] == datetime:
                p_obj[col['out']] = datetime(*sim['meta'][col['in']])
            else:
                p_obj[col['out']] = col['type'](sim['meta'][col['in']])

        p_arr.append(p_obj)
    # combine and condition all simulation outputs
    prog_objs = concat(p_arr).reset_index()
    prog_objs = prog_objs.astype({obj['in']: obj['type'] for obj in params if 'type' in obj})
    prog_objs = prog_objs.rename(columns={obj['in']: obj['out'] for obj in params})
    for m in params:
        if 'xfac' in m and m['xfac'] != 1:
            prog_objs[m['out']] = prog_objs[m['out']]*m['xfac']
    prog_objs = prog_objs.astype({obj['out']: obj['type'] for obj in params if 'type' in obj})
    if aggregate:
        # This will average values from different sims
        prog_objs = prog_objs.groupby([index, 'program_name']).mean().reset_index()
    # split up dataframe into list of dataframs by program name
    return prog_objs


def add_ts_ref(ts_df, ref_program, suffix, ref_cols, merge_on, calcs=None):
    ref_df = ts_df[ts_df['program_name'] == ref_program][ref_cols + merge_on] \
        .rename(columns={col: "{}_{}".format(col, suffix) for col in ref_cols}) \
        .reset_index(drop=True)
    ref_df["{}_prog".format(suffix)] = ref_program
    progs_df = ts_df.reset_index(drop=True)
    progs_df = merge(ref_df, progs_df, on=["ts", "sim"])
    if calcs is not None:
        for col in ref_cols:
            for calc in calcs:
                if calc == 'dif':
                    progs_df["{}_{}_{}".format(col, calc, suffix)] \
                        = progs_df["{}_{}".format(col, suffix)] - progs_df[col]
                if calc == 'rat':
                    progs_df["{}_{}_{}".format(col, calc, suffix)] \
                        = progs_df[col].divide(progs_df["{}_{}".format(col, suffix)])
                if calc == 'p_dif':
                    progs_df["{}_{}_{}".format(col, calc, suffix)] \
                        = (progs_df["{}_{}".format(col, suffix)] - progs_df[col]) \
                        .divide(progs_df["{}_{}".format(col, suffix)])
    return progs_df


def agg_flatten(df, group_by, agg_cols=None, agg_types=["mean"],
                prefix=None, include_col_name=True, include_agg_name=False):
    """Aggregate and flatten a dataframe. Flattening will handle the indexes
       and column names when this function is called with multipe agg_types
       and with multiple agg columns. Allows multiple aggregation methods defined
       by three parameters (incude_col_name, include_agg_name and prefix).

        example:
        data = [
            {'cat': 1, 'type', 1 'value': '5'},
            {'cat': 1, 'type', 2 'value': '4'},
            {'cat': 2, 'type', 1 'value': '10'},
            {'cat': 2, 'type', 2 'value': '9'},
            {'cat': 3, 'type', 1 'value': '1'},
            {'cat': 3, 'type', 2 'value': '0'},
            ]

        df = pd.DataFrame.from_records(data)

        x = agg_flatten(df, ['cat', agg_cols=['value'], agg_types=["mean"],
                prefix='fun', include_col_name=True, include_agg_name=True)

        x =     cat     fun_val_mean
                 1          4.5
                 2          9.5
                 3          0.5


    Args:
        df (Pandas Dataframe): Target Dataframe
        group_by (list): list of columnns to groupby (see pandas .group_by function)
        agg_cols (list): list of columns to perform aggregation on.
        agg_types (list): list of functions used for aggregation.(see pandas .agg function)
                            - common functions 'mean', numpy.median, 'sum', 'count'
        prefix (string, optional): A prefix that is assigned to all agg_cols. Defaults to None.
                                    ie. if agg_cols = ['ID', 'shape'] and prefix = 'fun' then
                                    the output columns will include 'fun_ID', 'fun_shape'.
                                    does not apply on the group by columns
        include_col_name (bool, optional): Include original column name. Defaults to True.
        include_agg_name (bool, optional): Include the aggregation name. Defaults to False.


    Returns:
        Pandas Dataframe: aggregated and flattened df.
    """
    if agg_cols is not None:
        out_df = DataFrame(df[group_by+agg_cols]) \
            .groupby(group_by) \
            .aggregate(agg_types)
    else:
        out_df = df.groupby(group_by).aggregate(agg_types)
    if include_col_name and not include_agg_name:
        out_df.columns = [col[0] for col in out_df.columns]
    elif include_col_name and include_agg_name:
        out_df.columns = ['_'.join(col) for col in out_df.columns]
    elif not include_col_name and include_agg_name:
        out_df.columns = out_df.columns.droplevel(0)
    tmp_cols = []
    if prefix is not None:
        for col in out_df.columns:
            if col not in group_by:
                tmp_cols.append("{}_{}".format(prefix, col))
            else:
                tmp_cols.append(col)
        out_df.columns = tmp_cols
    return out_df.reset_index(group_by)
