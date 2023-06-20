#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 17:11:14 2023

@author: juanpablomadrigalcianci
"""
from typing import Dict, Any

# Constants
SCENARIOS = [
    "very bad",
    "bad",
    "base",
    "good",
    "very good",
    "pessimistic",
    "optimistic",
]
# Define type hints for the params_dict
ParamsDict = Dict[str, Any]


def generate_params_dict_for_scenario(
    params_dict: dict, token_scenario: str, usage_scenario: str, staking_scenario: str
) -> ParamsDict:
    # Copy params_dict
    new_params_dict = params_dict.copy()
    # Update token scenario
    new_params_dict = generate_price_or_fee_scenario(
        params_dict=new_params_dict,
        scenario=token_scenario,
        model_name="token_price_model",
    )
    # Update usage scenario
    new_params_dict = generate_price_or_fee_scenario(
        params_dict=new_params_dict,
        scenario=usage_scenario,
        model_name="service_fees_model",
    )
    new_params_dict = generate_n_trx_scenario(new_params_dict, usage_scenario)
    # Update staking scenario
    new_params_dict = generate_staking_scenario(new_params_dict, staking_scenario)
    return new_params_dict


def generate_staking_scenario(
    params_dict: dict,
    scenario: str,
) -> ParamsDict:
    assert scenario in SCENARIOS, f"Invalid scenario. Expected one of: {SCENARIOS}"
    new_params_dict = params_dict.copy()
    if scenario == "very bad":
        new_params_dict["initial_stake_convertion_rate"] = 0.1
        new_params_dict["rewards_reinvest_rate"] = 0.0
        new_params_dict["staking_renewal_rate"] = 0.3
    elif scenario == "bad":
        new_params_dict["initial_stake_convertion_rate"] = 0.3
        new_params_dict["rewards_reinvest_rate"] = 0.3
        new_params_dict["staking_renewal_rate"] = 0.6
    elif scenario == "base":
        new_params_dict["initial_stake_convertion_rate"] = 0.5
        new_params_dict["rewards_reinvest_rate"] = 0.5
        new_params_dict["staking_renewal_rate"] = 0.8
    elif scenario == "good":
        new_params_dict["initial_stake_convertion_rate"] = 0.7
        new_params_dict["rewards_reinvest_rate"] = 0.7
        new_params_dict["staking_renewal_rate"] = 0.8
    elif scenario == "really good":
        new_params_dict["initial_stake_convertion_rate"] = 0.9
        new_params_dict["rewards_reinvest_rate"] = 1.0
        new_params_dict["staking_renewal_rate"] = 0.9
    elif scenario == "pessimistic":
        new_params_dict["initial_stake_convertion_rate"] = 0.3
        new_params_dict["rewards_reinvest_rate"] = 0.0
        new_params_dict["staking_renewal_rate"] = 0.5
        new_params_dict["new_staker_inflow_model"]["init_stake_amt"] = 0.0
    elif scenario == "optimistic":
        new_params_dict["initial_stake_convertion_rate"] = 0.9
        new_params_dict["rewards_reinvest_rate"] = 1.0
        new_params_dict["staking_renewal_rate"] = 1.0
        new_params_dict["new_staker_inflow_model"]["init_stake_amt"] = 1_000_000.0
    return new_params_dict


def generate_n_trx_scenario(
    params_dict: dict,
    scenario: str,
) -> ParamsDict:
    """
    Generate transactions scenario based on the given scenario.

    Args:
        params_dict (dict): The dictionary containing the parameters.
        scenario (str): The scenario for generating transactions.
        sim_length (int): Length of the simulation.

    Returns:
        ParamsDict: Updated params_dict with the generated transactions scenario.
    """
    assert scenario in SCENARIOS, f"Invalid scenario. Expected one of: {SCENARIOS}"
    N_trx_constant = params_dict["ntxs_model"]["N_trx_constant"]
    params_dict["ntxs_model"]["model"] = "linear"
    rates = {
        "very bad": -0.75 * N_trx_constant / 365,
        "bad": -0.25 * N_trx_constant / 365,
        "base": N_trx_constant,
        "good": N_trx_constant / 365,
        "very good": 2 * N_trx_constant / 365,
        "pessimistic": -0.75 * N_trx_constant / 365,
        "optimistic": 2 * N_trx_constant / 365,
    }
    params_dict["ntxs_model"]["rate"] = rates[scenario]
    if scenario == "base":
        params_dict["ntxs_model"]["model"] = "poisson"
    return params_dict


def generate_arrival_rate_scenario(
    params_dict: dict,
    scenario: str,
    VALIDATOR_JOINING_RATES: dict = {
        "very bad": 1 / 365,
        "bad": 1 / 180,
        "base": 1 / 90,
        "good": 1 / 30,
        "very good": 1 / 30,
    },
) -> ParamsDict:
    """
    Generate validators arrival rate scenario based on the given scenario.

    Args:
        params_dict (dict): The dictionary containing the parameters.
        scenario (str): The scenario for generating the arrival rate.

    Returns:
        ParamsDict: Updated params_dict with the generated arrival rate scenario.
    """
    assert scenario in SCENARIOS, f"Invalid scenario. Expected one of: {SCENARIOS}"
    params_dict["n_validators_model"]["rate"] = VALIDATOR_JOINING_RATES[scenario]
    return params_dict


def generate_price_or_fee_scenario(
    params_dict: dict,
    model_name: str,
    scenario: str,
    max_drift: float = 0.8,
    volatility: float = 0.4,
) -> ParamsDict:
    """
    Generate price or service fee scenario based on the given scenario and volatility.

    Args:
        params_dict (dict): The dictionary containing the parameters.
        model_name (str): The model name for which the scenario is generated.
        scenario (str): The scenario for generating the price or service fee.
        max_drift (float): The maximum drift value for the GBM model.
        volatility (float): The volatility value for the token price model.

    Returns:
        ParamsDict: Updated params_dict with the generated price scenario.
    """
    assert scenario in SCENARIOS, f"Invalid scenario. Expected one of: {SCENARIOS}"
    assert model_name in [
        "token_price_model",
        "service_fees_model",
    ], "Invalid model_name. Expected one of: ['token_price_model', 'service_fees_model']"
    drifts = {
        "very bad": -max_drift,
        "bad": -max_drift / 2,
        "base": 0.0,
        "good": max_drift / 2,
        "very good": max_drift,
        "pessimistic": -2.0,
        "optimistic": 1,
    }
    params_dict[model_name]["sigma"] = volatility
    params_dict[model_name]["model"] = "gbm"
    params_dict[model_name]["drift"] = drifts[scenario]
    return params_dict


def generate_full_scenario(
    params_dict: dict, scenarios_dict: dict, forecast_length: int
) -> ParamsDict:
    """
    Generate a full scenario based on the given scenario dictionary.

    Args:
        params_dict (dict): The dictionary containing the parameters.
        scenarios_dict (dict): The dictionary containing the scenarios for different models.
        forecast length (int): number of steps in the simulation

    Returns:
        ParamsDict: Updated params_dict with the generated full scenario.
    """
    # Generate the scenarios for each model
    params_dict = generate_price_or_fee_scenario(
        params_dict=params_dict,
        scenario=scenarios_dict["service_fee_model"],
        model_name="service_fees_model",
    )
    params_dict = generate_price_or_fee_scenario(
        params_dict=params_dict,
        scenario=scenarios_dict["price_model"],
        model_name="token_price_model",
    )
    params_dict = generate_arrival_rate_scenario(
        params_dict=params_dict, scenario=scenarios_dict["n_validators"]
    )
    params_dict = generate_n_trx_scenario(
        params_dict=params_dict,
        scenario=scenarios_dict["n_trx"],
        sim_length=forecast_length,
    )
    return params_dict


if __name__ == "__main__":
    import os
    import pandas as pd
    from mechaqredo.params import default_params_dict
    from mechaqredo.sim import run_single_sim
    import sys
    import matplotlib.pyplot as plt
    import warnings

    warnings.filterwarnings("ignore")
    FORECAST_LENGTH = 365 * 3
    FILE_PATH = "../data/balances.csv"
    CODE_DIR = os.path.realpath(os.path.join(os.getcwd(), ".."))
    sys.path.append(CODE_DIR)
    # Load the wallet data
    wallet_df = pd.read_csv(FILE_PATH)
    params_dict = default_params_dict(FORECAST_LENGTH)
    params_dict["wallet_balances_vec"] = wallet_df["balance"].values
    for s in SCENARIOS:
        plt.figure(figsize=(16, 16))
        plt.suptitle(s + " scenario")
        # generates the scenarios

        sd = {"service_fee_model": s, "price_model": s, "n_validators": s, "n_trx": s}

        params_dict = generate_full_scenario(
            params_dict=params_dict, scenarios_dict=sd, forecast_length=FORECAST_LENGTH
        )

        plt.subplot(2, 2, 1)
        df = run_single_sim(FORECAST_LENGTH, params_dict)
        df["token_price"].plot()
        plt.title("Price")
        plt.subplot(2, 2, 2)
        df["service_fees"].plot()
        plt.title("service fee")
        plt.subplot(2, 2, 3)
        df["n_validators"].plot()
        plt.title("N validators")
        plt.subplot(2, 2, 4)
        df["n_txs"].plot()
        plt.title("N trx")
        plt.tight_layout()
        plt.show()
