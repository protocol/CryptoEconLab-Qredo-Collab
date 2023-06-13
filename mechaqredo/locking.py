import numpy as np
from typing import Tuple


def forecast_service_fee_locked_vec(
    parms_dict: dict,
    token_price_vec: np.array,
    service_fees_vec: np.array,
) -> np.array:
    # Forecast locked tokens from Service Fees tipped to the network
    staking_parms_dict = parms_dict["staking"]
    tipping_rate = staking_parms_dict["tipping_rate"]
    slippage = staking_parms_dict["slippage"]
    service_fee_locked_vec = (
        tipping_rate * service_fees_vec * (1 - slippage)
    ) / token_price_vec
    return service_fee_locked_vec


def forecast_released_vec(
    forecast_length: int,
    parms_dict: dict,
    burning_vec: np.array,
    staking_outflows_vec: np.array,
    ecosystem_fund_initial: float,
) -> np.array:
    # Set parameters
    protocol_funded_rate = parms_dict["staking"]["protocol_funded_rate"]
    # Get token releases from protocol fees covered by the protocol
    released_protocol_burn = protocol_funded_rate * burning_vec
    # Forecast ecosystem fund and token releases from staking rewards

    return None


def forecast_staking_rewards_and_ecosystem_fund(
    forecast_length: int,
    service_fee_locked_vec: np.array,
    released_protocol_burn: np.array,
    staking_inflows_vec: np.array,
    staking_outflows_vec: np.array,
    n_val_vec: np.array,
    ecosystem_fund_zero: float,
) -> Tuple[np.array, np.array]:
    staking_tvl_vec = staking_inflows_vec.cumsum() - staking_outflows_vec.cumsum()
    ecosystem_fund_list = [ecosystem_fund_zero]
    released_staking_rewards_list = []
    for i in range(forecast_length):
        # Compute released tokens
        curr_ecosystem_fund_value = ecosystem_fund_list[i]
        release_rate = release_rate_function(staking_tvl_vec[i], n_val_vec[i])
        curr_released_staking_rewards = release_rate * curr_ecosystem_fund_value
        released_staking_rewards_list.append(curr_released_staking_rewards)
        # Compute next ecosystem fund value
        next_ecosystem_fund_value = (
            curr_ecosystem_fund_value
            + service_fee_locked_vec[i]
            - released_protocol_burn[i]
            - curr_released_staking_rewards
        )
        ecosystem_fund_list.append(next_ecosystem_fund_value)
    released_staking_rewards_vec = np.array(released_staking_rewards_list)
    ecosystem_fund_vec = np.array(ecosystem_fund_list)
    return released_staking_rewards_vec, ecosystem_fund_vec


def release_rate_function(tvl: float, n_val: int) -> float:
    # TODO: design release rate function with tunnable parameters
    return 0.1
