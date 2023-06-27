import numpy as np
import datetime as dt


def forecast_vested_vec_from_previous_allocation(
    forecast_length: int, params_dict: dict
) -> np.array:
    sim_start = params_dict["sim_start_datetime"]
    vested_vec = build_linear_vesting_vec(
        sim_start, forecast_length, params_dict["previous_funds_vesting_spec"]
    )
    return vested_vec


def forecast_vested_vec_from_staking(forecast_length: int, params_dict: dict):
    fund_size = params_dict["staking_rewards_fund_size"]
    vesting_decay_rate = params_dict["staking_rewards_vesting_decay_rate"]
    cum_vesting_list = [
        fund_size * (1 - np.exp(-vesting_decay_rate * day))
        for day in range(forecast_length)
    ]
    cum_vesting_vec = np.array([0.0] + cum_vesting_list)
    vested_vec = np.diff(cum_vesting_vec)
    return vested_vec


def forecast_vested_vec_from_new_allocation(
    forecast_length: int, params_dict: dict
) -> np.array:
    sim_start = params_dict["sim_start_datetime"]
    vested_vec = build_linear_vesting_vec(
        sim_start, forecast_length, params_dict["new_funds_vesting_spec"]
    )
    return vested_vec


def build_linear_vesting_vec(
    sim_start: dt.datetime, forecast_length: int, fund_params_dict: dict
) -> np.array:
    known_vest_vec = np.zeros(forecast_length, dtype=float)
    for fund_name in fund_params_dict:
        fund_spec_dict = fund_params_dict[fund_name]
        fund_vesting_vec = linear_vest(forecast_length, sim_start, fund_spec_dict)
        known_vest_vec += fund_vesting_vec
    return known_vest_vec


def linear_vest(
    forecast_length: int,
    sim_start: dt.datetime,
    fund_spec_dict: dict,
) -> np.array:
    vest_period_days = fund_spec_dict["vest_period_days"]
    vest_end_date = fund_spec_dict["vest_end_date"]
    vest_amount = fund_spec_dict["vest_amount"]
    vest_zero = fund_spec_dict["vest_zero"]
    vesting_days = (vest_end_date - sim_start).days
    vest_vec = np.zeros(forecast_length, dtype=float)
    vest_vec[0] = vest_zero
    if vest_amount is not None:
        for i in range(vesting_days, 0, -vest_period_days):
            if i < forecast_length:
                vest_vec[i] = vest_amount
    return vest_vec
