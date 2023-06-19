import numpy as np


def forecast_staking_stats(
    forecast_length: int,
    params_dict: dict,
    n_val_vec: np.array,
    service_fee_locked_vec: np.array,
    released_protocol_burn_vec: np.array,
    staking_vesting_rewards_vec: np.array,
) -> dict:
    # Get params and data
    rewards_reinvest_rate = params_dict["rewards_reinvest_rate"]
    staking_renewal_rate = params_dict["staking_renewal_rate"]
    staker_reward_share = 1 - params_dict["validator_reward_share"]
    min_stake_duration = params_dict["min_stake_duration"]
    new_staker_inflow_vec = forecast_new_staker_inflow_vec(forecast_length, params_dict)
    # Initialise variables
    initial_staking_value = compute_initial_staking_value(params_dict)
    staking_inflows_list = [initial_staking_value]
    staking_outflows_list = [0.0]
    staking_tvl_list = [initial_staking_value]
    ecosystem_fund_list = [params_dict["ecosystem_fund_zero"]]
    staking_released_rewards_list = [0.0]
    total_staking_rewards_list = [0.0]
    available_for_outflow_vec = [0.0]
    # Run for loop
    for i in range(1, forecast_length):
        # Compute staking inflows
        stakers_previous_rewards = (
            staker_reward_share * total_staking_rewards_list[i - 1]
        )
        new_staker_inflow = new_staker_inflow_vec[i]
        staking_inflows = (
            rewards_reinvest_rate * stakers_previous_rewards + new_staker_inflow
        )
        # Compute staking outflows
        if i >= min_stake_duration:
            available_for_outflow = (
                available_for_outflow_vec[-1]
                + staking_inflows_list[i - min_stake_duration]
                - staking_outflows_list[-1]
            )
        else:
            available_for_outflow = 0.0
        staking_outflows = (1 - staking_renewal_rate) * available_for_outflow
        # Update flow lists
        available_for_outflow_vec.append(available_for_outflow)
        staking_inflows_list.append(staking_inflows)
        staking_outflows_list.append(staking_outflows)
        staking_tvl = staking_tvl_list[-1] + staking_inflows - staking_outflows
        staking_tvl_list.append(staking_tvl)
        # Compute reward distribution
        release_rate = release_rate_function(staking_tvl, n_val_vec[i], params_dict)
        staking_released_rewards = release_rate * ecosystem_fund_list[i - 1]
        total_staking_rewards = (
            staking_released_rewards + staking_vesting_rewards_vec[i]
        )
        staking_released_rewards_list.append(staking_released_rewards)
        total_staking_rewards_list.append(total_staking_rewards)
        # Update ecosystem fund value
        ecosystem_fund = (
            ecosystem_fund_list[-1]
            + service_fee_locked_vec[i]
            - released_protocol_burn_vec[i]
            - staking_released_rewards
        )
        ecosystem_fund_list.append(ecosystem_fund)
    # Build output dict
    staking_stat_dict = {
        "staking_inflows_vec": np.array(staking_inflows_list),
        "staking_outflows_vec": np.array(staking_outflows_list),
        "staking_released_rewards_vec": np.array(staking_released_rewards_list),
        "total_staking_rewards_vec": np.array(total_staking_rewards_list),
        "ecosystem_fund_vec": np.array(ecosystem_fund_list),
        "staking_tvl": np.array(staking_tvl_list),
    }
    return staking_stat_dict


def compute_initial_staking_value(params_dict: dict) -> float:
    wallet_balances_vec = params_dict["wallet_balances_vec"]
    min_stake_amount = params_dict["min_stake_amount"]
    initial_stake_convertion_rate = params_dict["initial_stake_convertion_rate"]
    available_wallet_balances_vec = wallet_balances_vec[
        wallet_balances_vec >= min_stake_amount
    ]
    available_stake = sum(available_wallet_balances_vec)
    initial_stake = initial_stake_convertion_rate * available_stake
    return initial_stake


def release_rate_function(tvl: float, n_val: int, params_dict: dict) -> float:
    # Get parameters
    release_params_dict = params_dict["release_rate_function"]
    function_type = release_params_dict["release_rate_function_type"]
    a = release_params_dict["release_rate_a"]
    b = release_params_dict["release_rate_b"]
    V_max = release_params_dict["max_validators"]
    T_max = release_params_dict["max_TVL"]
    # Compute rate
    if function_type == "linear":
        r = a * tvl / T_max + (1 - a) * n_val / V_max
    elif function_type == "sigmoid":
        r = 2 * (1 / (1 + np.exp(-a * tvl - b * n_val)) - 0.5) * (tvl > 0) * (n_val > 0)
    elif function_type == "fractional":
        r = (tvl**a + b * n_val**a) / (T_max**a + b * V_max**a)
    elif function_type == "fractional_convex":
        term1 = (tvl / T_max) ** a
        term2 = (n_val / V_max) ** b
        r = 0.5 * term1 + 0.5 * term2
    return r


def forecast_new_staker_inflow_vec(forecast_length: int, params_dict: dict) -> np.array:
    model = params_dict["new_staker_inflow_model"]["model"]
    init_stake_amt = params_dict["new_staker_inflow_model"]["init_stake_amt"]
    rate = params_dict["new_staker_inflow_model"]["rate"]
    if model == "constant":
        return np.array([init_stake_amt] * forecast_length)
    elif model == "linear":
        return np.array([rate * t + init_stake_amt for t in range(forecast_length)])
    else:
        raise ValueError("Model provided is not valid")
