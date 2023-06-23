import os
import itertools
import pandas as pd
from typing import List
from tqdm import tqdm
import numpy as np
from .params import validate_params_dict, default_params_dict
from .data_models import build_model_data_dict, build_model_data_dict_samples
from .supply import forecast_supply_stats


def run_param_sweep_sim(
    forecast_length: int,
    input_params_dict: dict,
    param_ranges_dict: dict,
    data_dict_n_samples: int = 1,
    data_dict_list: List[dict] = None,
    output_dir: str = "data",
    save: bool = False,
    file_name: str = None,
) -> pd.DataFrame:
    # Validate input parameters
    params_dict = validate_params_dict(forecast_length, input_params_dict)
    # Generate/Load list of data dicts
    if data_dict_list is None:
        data_dict_list = build_model_data_dict_samples(
            data_dict_n_samples, forecast_length, params_dict
        )
    # Initialize sweep DataFrame
    sweep_df_list = []
    iter_tuple_list = list(itertools.product(*param_ranges_dict.values()))
    key_list = param_ranges_dict.keys()
    for iter_tuple in tqdm(iter_tuple_list):
        # Build input parameters for sweep iteration
        iter_input_params_dict = input_params_dict.copy()
        for i, key in enumerate(key_list):
            iter_input_params_dict[key] = iter_tuple[i]
        # Validate input parameters
        iter_params_dict = validate_params_dict(forecast_length, iter_input_params_dict)
        # For each data dict:
        ii = 0
        for data_dict in data_dict_list:
            # Forecast supply stats
            supply_data_dict = forecast_supply_stats(
                forecast_length, iter_params_dict, data_dict
            )
            # Build output dataframe
            iter_df = build_output_dataframe(data_dict, supply_data_dict)
            for i, key in enumerate(key_list):
                iter_df[key] = iter_tuple[i]
            # Append iter df to sweep df list
            sweep_df_list.append(iter_df)
            # Save item_df to a file
            if save:
                item_df_filename = f"{file_name}_{iter_tuple}_sim_{ii}.csv"
                item_df_filepath = os.path.join(output_dir, item_df_filename)
                iter_df.to_csv(item_df_filepath, index=False)
            ii += 1
    sweep_df = pd.concat(sweep_df_list, ignore_index=True)
    return sweep_df



def get_single_derivative(forecast_length: int,
                          with_respect_to:str,
                          input_params_dict: dict,
                          seed:int,
                          h:float=None) -> pd.DataFrame:
    ''' gets an evaluation of a derivative using finite differences'''
    
    if h is None:
        h=input_params_dict[with_respect_to]*0.01
    
    np.random.seed(seed)
    df0=run_single_sim(forecast_length, input_params_dict)
    np.random.seed(seed)
    input_params_dict[with_respect_to]+=h
    df1=run_single_sim(forecast_length, input_params_dict)
    single_derivative=(df1-df0)/h
    input_params_dict[with_respect_to]+=-h
    return single_derivative


def estimate_sensitivity(forecast_length: int,
                          with_respect_to:str,
                          input_params_dict: dict,
                          h:float=None,
                          N=100) -> pd.DataFrame:
    ''' computes the monte carlo estimate of the sensitivity'''
    

    d=get_single_derivative(forecast_length,
                              with_respect_to,
                              input_params_dict,0,h)
    print(f'Estimating sensitivity wrt {with_respect_to}')
    for i in range(1,N+1):
        d+=get_single_derivative(forecast_length,
                                  with_respect_to,
                                  input_params_dict,i,h)
    
    return d/N
        
    
    



def run_single_sim(forecast_length: int, input_params_dict: dict) -> pd.DataFrame:
    # Validate input parameters
    params_dict = validate_params_dict(forecast_length, input_params_dict)
    # Build Data dict
    data_dict = build_model_data_dict(forecast_length, params_dict)
    # Forecast supply stats
    supply_data_dict = forecast_supply_stats(forecast_length, params_dict, data_dict)
    # Build output dataframe
    df = build_output_dataframe(data_dict, supply_data_dict)
    return df


def build_output_dataframe(data_dict: dict, supply_data_dict: dict) -> pd.DataFrame:
    data_df = pd.DataFrame(data_dict)
    supply_data_df = pd.DataFrame(supply_data_dict)
    df = pd.concat([supply_data_df, data_df], axis=1)
    df["day_inflation"] = df["circ_supply"].pct_change(periods=1)
    df["year_inflation"] = df["circ_supply"].pct_change(periods=365)
    return df


if __name__ == "__main__":
    import timeit

    start = timeit.default_timer()
    df = run_single_sim(365 * 2, default_params_dict(365 * 2))
    stop = timeit.default_timer()
    print("Run time for single sim: ", stop - start)
