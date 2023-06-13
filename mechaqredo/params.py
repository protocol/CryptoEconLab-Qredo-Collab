import numpy as np


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
        "A0": 25000000.0,
        "a": None,
        "mu": None,
        "sigma": None,
        "dt": 1 / 365,
        "theta": None,
    }
    params_dict = {
        "ntxs_model": ntxs_model_params_dict,
        "token_price_model": token_model_params_dict,
        "service_fees_model": service_model_params_dict,
        "burn_extra_vec": np.zeros(forecast_length),
        "protocol_fee_rate": 0.0005,
        "ecosystem_fund_zero": 44423076.0,
        "circ_supply_zero": 260000000.0,
        "slippage": 0.005,
        "tipping_rate": 0.3,
        "protocol_funded_rate": 0.5,
    }
    return params_dict


def validate_params_dict(forecast_length: int, params_dict: dict) -> dict:
    # TODO: implement parameters validation function
    return params_dict
