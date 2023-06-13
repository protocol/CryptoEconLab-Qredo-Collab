import numpy as np

from vesting import forecast_vested_vec
from locking import (
    forecast_service_fee_locked_vec,
    forecast_staking_rewards_and_ecosystem_fund,
)


def forecast_supply_stats(
    forecast_length: int, params_dict: dict, data_dict: dict
) -> dict:
    # Get inputs from data dict
    n_txs_vec = data_dict["n_txs_vec"]
    token_price_vec = data_dict["token_price_vec"]
    service_fees_vec = data_dict["service_fees_vec"]
    staking_inflows_vec = data_dict["staking_inflows_vec"]
    staking_outflows_vec = data_dict["staking_outflows_vec"]
    n_val_vec = data_dict["n_val_vec"]
    # Forecast burned tokens
    burn_extra_vec = params_dict["burn_extra_vec"]
    protocol_fee_rate = params_dict["protocol_fee_rate"]
    burn_fees_vec = protocol_fee_rate * n_txs_vec
    burned_vec = burn_extra_vec + burn_fees_vec
    # Forecast vested tokens
    vested_vec = forecast_vested_vec(forecast_length, params_dict)
    # Forecast locked tokens
    service_fee_locked_vec = forecast_service_fee_locked_vec(
        params_dict,
        token_price_vec,
        service_fees_vec,
    )
    locked_vec = service_fee_locked_vec + staking_inflows_vec
    # Forecast released tokens
    protocol_funded_rate = params_dict["protocol_funded_rate"]
    ecosystem_fund_zero = params_dict["ecosystem_fund_zero"]
    #   Get token releases from protocol fees covered by the protocol
    released_protocol_burn_vec = protocol_funded_rate * burned_vec
    #   Get token releases from staking rewards
    (
        released_staking_rewards_vec,
        ecosystem_fund_vec,
    ) = forecast_staking_rewards_and_ecosystem_fund(
        forecast_length,
        service_fee_locked_vec,
        released_protocol_burn_vec,
        staking_inflows_vec,
        staking_outflows_vec,
        n_val_vec,
        ecosystem_fund_zero,
    )
    #   Bring all releases together
    released_vec = (
        released_protocol_burn_vec + released_staking_rewards_vec + staking_outflows_vec
    )
    # Compute circulating supply
    circ_supply_zero = params_dict["circ_supply_zero"]
    circ_supply = (
        circ_supply_zero
        - burned_vec.cumsum()
        + vested_vec.cumsum()
        - locked_vec.cumsum()
        + released_vec.cumsum()
    )
    # Put tofether output dict
    output_dict = {
        "iteration": np.arange(0, forecast_length, 1),
        "circ_supply": circ_supply,
        "day_burned_vec": burned_vec,
        "day_vested_vec": vested_vec,
        "day_locked_vec": locked_vec,
        "day_released_vec": released_vec,
        "day_inflation": np.diff(circ_supply) / circ_supply[:-1],
        "market_cap": circ_supply * token_price_vec,
        "day_burn_fees_vec": burn_fees_vec,
        "day_service_fee_locked_vec": service_fee_locked_vec,
        "ecosystem_fund_vec": ecosystem_fund_vec,
    }
    return output_dict
