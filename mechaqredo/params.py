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
        "N_trx_constant": 1000.0,
    }
    token_model_params_dict = {
        "model": "constant",
        "P0": 0.095,  # price at 2023/06/15
        "drift": None,
        "sigma": None,
        "dt": 1 / 365,
    }
    service_model_params_dict = {
        "model": "constant",
        "A0": 3_000.0,
        "a": None,
        "drift": None,
        "sigma": None,
        "dt": 1 / 365,
        "theta": None,
        "defined_path": None,
    }
    n_val_model_params_dict = {
        "rate": (18 - 6) / 730,
        "constant_rate": None,
        "list_of_precomputed_arrivals": None,
        "initial_number": 6,
    }
    new_staker_inflow_params_dict = {
        "model": "constant",
        "init_stake_amt": 100_000.0,
        "rate": None,
    }
    previous_funds_params_dict = {
        "seed": {
            "vest_period_days": 7,
            "vest_end_date": dt.datetime(2024, 7, 14),
            "vest_amount": 160_230.04,
            "vest_zero": 0.0,
        },
        "team_quarterly": {
            "vest_period_days": 91,
            "vest_end_date": dt.datetime(2026, 1, 14),
            "vest_amount": 1_976_405.65,
            "vest_zero": 0.0,
        },
        "investors_and_others": {
            "vest_period_days": 7,
            "vest_end_date": dt.datetime(2026, 1, 14),
            "vest_amount": 3_018_335.60,
            "vest_zero": 0.0,
        },
        "treasury": {
            "vest_period_days": 7,
            "vest_end_date": dt.datetime(2026, 1, 14),
            "vest_amount": 161_596.15,
            "vest_zero": 0.0,
        },
    }
    new_funds_params_dict = {
        "public_goods": {
            "vest_period_days": None,
            "vest_end_date": None,
            "vest_amount": None,
            "vest_zero": 50_000_000,
        },
        "treasury_refresh": {  # the "development fund"
            "vest_period_days": None,
            "vest_end_date": None,
            "vest_amount": None,
            "vest_zero": 250_000_000,
        },
    }
    params_dict = {
        "sim_start_datetime": dt.datetime(2023, 6, 15),
        # User model params
        "ntxs_model": ntxs_model_params_dict,
        "token_price_model": token_model_params_dict,
        "service_fees_model": service_model_params_dict,
        "n_validators_model": n_val_model_params_dict,
        "new_staker_inflow_model": new_staker_inflow_params_dict,
        # Data params
        "previous_funds_vesting_spec": previous_funds_params_dict,
        "wallet_balances_vec": np.array([95_000_000.0]),
        "circ_supply_zero": 339_000_000.0,
        "ecosystem_fund_zero": 55_000_000.0,  # we are assuming this fund gets an accelerated vesting!
        # User behavior params
        "protocol_funded_rate": 0.5,
        "initial_stake_convertion_rate": 0.7,
        "rewards_reinvest_rate": 0.5,
        "staking_renewal_rate": 0.8,
        "slippage": 0.005,
        # Tokenomic params:
        "tipping_rate": 0.3,
        "protocol_fee_rate": 0.0005,
        "min_stake_amount": 1.0,
        "min_stake_duration": 14,
        "validator_reward_share": 0.5,
        "staking_rewards_vesting_decay_rate": np.log(2) / (4.0 * 365),  # 4yrs half-life
        # Tokenomic params for the release rate function
        "release_rate_a": 0.5,
        "release_rate_b": 1,
        "max_validators": 50,
        "max_TVL": (2000 - 140 - 160) * 0.7,
        "release_rate_max": 0.0008,  # (1-max_rate)**(2*365)>0.5, i.e. two max to half the fund value
        # Allocation params
        "new_funds_vesting_spec": new_funds_params_dict,
        "staking_rewards_fund_size": 250_000_000,
        "ecosystem_refresh_size": 290_000_000,
        "burn_extra_vec": np.array([160_000_000] + [0] * (forecast_length - 1)),
    }
    return params_dict


def validate_params_dict(forecast_length: int, params_dict: dict) -> dict:
    # TODO: implement parameters validation function
    return params_dict
