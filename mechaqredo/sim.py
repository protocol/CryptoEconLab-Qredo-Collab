import pickle
import itertools
import pandas as pd

from .params import validate_params_dict, default_params_dict
from .data_models import build_model_data_dict, build_model_data_dict_samples
from .supply import forecast_supply_stats


def run_param_sweep_sim(
    forecast_length: int,
    input_params_dict: dict,
    param_ranges_dict: dict,
    data_dict_n_samples: int = 1,
    data_dict_list_file: str = None,
) -> pd.DataFrame:
    # Validate input parameters
    params_dict = validate_params_dict(forecast_length, input_params_dict)
    # Generate/Load list of data dicts
    if data_dict_list_file is None:
        data_dict_list = build_model_data_dict_samples(
            data_dict_n_samples, forecast_length, params_dict
        )
    else:
        with open(data_dict_list_file, "rb") as fp:
            data_dict_list = pickle.load(fp)
    # Run params sweep
    sweep_df = pd.DataFrame()
    iter_tuple_list = list(itertools.product(*param_ranges_dict.values()))
    key_list = param_ranges_dict.keys()
    for iter_tuple in iter_tuple_list:
        # Build input parameters for sweep iteration
        iter_input_params_dict = input_params_dict.copy()
        for i, key in enumerate(key_list):
            iter_input_params_dict[key] = iter_tuple[i]
        # Validate input parameters
        params_dict = validate_params_dict(forecast_length, iter_input_params_dict)
        # For each data dict:
        for data_dict in data_dict_list:
            # Forecast supply stats
            supply_data_dict = forecast_supply_stats(
                forecast_length, params_dict, data_dict
            )
            # Build output dataframe
            iter_df = build_output_dataframe(data_dict, supply_data_dict)
            for i, key in enumerate(key_list):
                iter_df[key] = iter_tuple[i]
            # Append iter df to sweep df
            sweep_df = pd.concat([sweep_df, iter_df], ignore_index=True)
    return sweep_df


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
    df = run_single_sim(365, default_params_dict(365))
    stop = timeit.default_timer()
    print("Run time for single sim: ", stop - start)
    df.to_csv("sim_text.csv")
