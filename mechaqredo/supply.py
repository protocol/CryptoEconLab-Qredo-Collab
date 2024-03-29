import numpy as np

from .vesting import (
    forecast_vested_vec_from_previous_allocation,
    forecast_vested_vec_from_new_allocation,
    forecast_vested_vec_from_staking,
)
from .staking import forecast_staking_stats
from .locking import forecast_service_fee_locked_vec


def forecast_supply_stats(
    forecast_length: int, params_dict: dict, data_dict: dict
) -> dict:
    # Get inputs from data dict
    n_txs_vec = data_dict["n_txs"]
    token_price_vec = data_dict["token_price"]
    service_fees_vec = data_dict["service_fees"]
    n_val_vec = data_dict["n_validators"]
    # Forecast burned tokens
    burn_extra_vec = params_dict["burn_extra_vec"]
    protocol_fee_rate = params_dict["protocol_fee_rate"]
    burn_fees_vec = protocol_fee_rate * n_txs_vec
    burned_vec = burn_extra_vec + burn_fees_vec
    # Forecast vested tokens
    vested_vec_from_previous = forecast_vested_vec_from_previous_allocation(
        forecast_length, params_dict
    )
    vested_vec_from_new = forecast_vested_vec_from_new_allocation(
        forecast_length, params_dict
    )
    vested_vec_from_staking = forecast_vested_vec_from_staking(
        forecast_length, params_dict
    )
    vested_ecosystem_fund_zero = (
        params_dict["ecosystem_fund_zero"] + params_dict["ecosystem_refresh_size"]
    )
    vested_vec = (
        vested_vec_from_previous + vested_vec_from_new + vested_vec_from_staking
    )
    # Need to vest the burn extra and the ecosystem fund
    vested_vec[0] += vested_ecosystem_fund_zero + burn_extra_vec.sum()
    # Forecast locked tokens from service fees
    service_fee_locked_vec = forecast_service_fee_locked_vec(
        params_dict,
        token_price_vec,
        service_fees_vec,
    )
    # Forecast token releases from protocol fees covered by the protocol
    protocol_funded_rate = params_dict["protocol_funded_rate"]
    released_protocol_burn_vec = protocol_funded_rate * burned_vec
    # Forecast staking stats
    staking_stat_dict = forecast_staking_stats(
        forecast_length,
        params_dict,
        n_val_vec,
        service_fee_locked_vec,
        released_protocol_burn_vec,
        vested_vec_from_staking,
    )
    staking_inflows_vec = staking_stat_dict["staking_inflows_vec"]
    staking_outflows_vec = staking_stat_dict["staking_outflows_vec"]
    staking_released_rewards_vec = staking_stat_dict["staking_released_rewards_vec"]
    ecosystem_fund_vec = staking_stat_dict["ecosystem_fund_vec"]
    # Compute total locked tokens
    # Get ecosystem fund size at zero
    ecosystem_lock_vec = np.zeros(forecast_length, dtype="float")
    ecosystem_lock_vec[0] = (
        params_dict["ecosystem_fund_zero"] + params_dict["ecosystem_refresh_size"]
    )
    locked_vec = service_fee_locked_vec + staking_inflows_vec + ecosystem_lock_vec
    # Compute total released tokens
    released_vec = (
        released_protocol_burn_vec + staking_released_rewards_vec + staking_outflows_vec
    )
    # Compute circulating supply
    circ_supply = (
        params_dict["circ_supply_zero"]
        - burned_vec.cumsum()
        + vested_vec.cumsum()
        - locked_vec.cumsum()
        + released_vec.cumsum()
    )
    # Put together output dict
    total_staking_rewards_vec = staking_stat_dict["total_staking_rewards_vec"]
    validator_reward_share = params_dict["validator_reward_share"]
    output_dict = {
        "iteration": np.arange(0, forecast_length, 1),
        "circ_supply": circ_supply,
        "day_burned": burned_vec,
        "day_vested": vested_vec,
        "day_locked": locked_vec,
        "day_released": released_vec,
        "staking_rewards_vested": vested_vec_from_staking,
        "staking_rewards_ecosystem": staking_stat_dict["total_staking_rewards_vec"]
        - vested_vec_from_staking,
        "total_staking_rewards": staking_stat_dict["total_staking_rewards_vec"],
        "validators_rewards": validator_reward_share * total_staking_rewards_vec,
        "market_cap": circ_supply * token_price_vec,
        "day_burn_fees": burn_fees_vec,
        "day_service_fee_locked": service_fee_locked_vec,
        "ecosystem_fund": ecosystem_fund_vec,
        "staking_tvl": staking_stat_dict["staking_tvl"],
    }
    return output_dict
