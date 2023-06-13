import numpy as np


def forecast_vested_vec(forecast_length: int, params_dict: dict) -> np.array:
    # TODO: Improve vesting module
    total_to_vest = 1600000000
    vesting_days = 365 * 3
    daily_vest = total_to_vest / vesting_days
    return np.ones(forecast_length) * daily_vest
