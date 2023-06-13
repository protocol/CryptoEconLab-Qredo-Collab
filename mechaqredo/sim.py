import pandas as pd

from params import validate_params_dict
from data_models import build_model_data_dict
from supply import forecast_supply_stats


def run_single_sim(forecast_length: int, input_params_dict: dict) -> pd.DataFrame:
    # Validate input parameters
    params_dict = validate_params_dict(input_params_dict)
    # Build
    data_dict = build_model_data_dict(forecast_length, params_dict)
    # Forecast supplt stats
    supply_data_dict = forecast_supply_stats(forecast_length, params_dict, data_dict)
    # Build output dataframe
    df = build_output_dataframe(data_dict, supply_data_dict)
    return df


def build_output_dataframe(data_dict: dict, supply_data_dict: dict) -> pd.DataFrame:
    data_df = pd.DataFrame(data_dict)
    supply_data_df = pd.DataFrame(supply_data_dict)
    df = pd.concat([supply_data_df, data_df], axis=1)
    return df
