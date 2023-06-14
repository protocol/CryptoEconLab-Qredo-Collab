import numpy as np
import datetime as dt


def default_params_dict(forecast_length: int) -> dict:
    # TODO: confirm default values
    ntxs_model_params_dict = {
        "model": "constant",
        "schedule": None,
        "distr": None,
        "fun": None,
        "rate": None,
        "N_trx_constant": 8000.0,
    }
    token_model_params_dict = {
        "model": "constant",
        "P0": 0.08,
        "drift": None,
        "sigma": None,
        "dt": 1 / 365,
    }
    service_model_params_dict = {
        "model": "constant",
        "A0": 25_000_000.0,
        "a": None,
        "mu": None,
        "sigma": None,
        "dt": 1 / 365,
        "theta": None,
    }
    n_val_model_params_dict = {
        "rate": (18 - 6) / 730,
        "constant_rate": None,
        "list_of_precomputed_arrivals": None,
        "initial_number": 6,
    }
    new_staker_inflow_params_dict = {
        "model": "constant",
        "init_stake_amt": 1000.0,
        "rate": None,
    }
    previous_funds_params_dict = {
        "seed": {
            "vest_period_days": 7,
            "vest_end_date": dt.datetime(2024, 7, 14),
            "vest_amount": 160_230.04,
        },
        "team_quarterly": {
            "vest_period_days": 91,
            "vest_end_date": dt.datetime(2026, 1, 14),
            "vest_amount": 1_976_405.65,
        },
        "investors_and_others": {
            "vest_period_days": 7,
            "vest_end_date": dt.datetime(2026, 1, 14),
            "vest_amount": 3_018_335.60,
        },
        "treasury": {
            "vest_period_days": 7,
            "vest_end_date": dt.datetime(2026, 1, 14),
            "vest_amount": 161_596.15,
        },
    }
    params_dict = {
        "sim_start_datetime": dt.datetime(2023, 7, 15),
        "ntxs_model": ntxs_model_params_dict,
        "token_price_model": token_model_params_dict,
        "service_fees_model": service_model_params_dict,
        "n_validators_model": n_val_model_params_dict,
        "new_staker_inflow_model": new_staker_inflow_params_dict,
        "previous_funds_vesting_spec": previous_funds_params_dict,
        "wallet_balances_vec": np.array([1000.0, 500.0]),  # Fix this!!!!
        "circ_supply_zero": 260_000_000.0,
        "protocol_fee_rate": 0.0005,
        "slippage": 0.005,
        "tipping_rate": 0.3,
        "protocol_funded_rate": 0.5,
        "min_stake_amount": 1.0,
        "min_stake_duration": 14,
        "initial_stake_convertion_rate": 0.7,
        "rewards_reinvest_rate": 0.5,
        "staking_renewal_rate": 0.8,
        "validator_reward_share": 0.5,
        "ecosystem_fund_zero": 110_000_000.0,  # we are assuming this fund gets an accelerated vesting!
        "public_goods_fund_size": 200_000_000,
        "staking_rewards_fund_size": 200_000_000,
        "staking_rewards_vesting_decay_rate": np.log(2) / (4.0 * 365),  # 4yrs half-life
        "treasury_refresh_size": 250_000_000,  # the "development fund"
        "burn_extra_vec": np.array([350_000_000] + [0] * (forecast_length - 1)),
    }
    return params_dict


def validate_params_dict(forecast_length: int, params_dict: dict) -> dict:
    # TODO: implement parameters validation function
    return params_dict
