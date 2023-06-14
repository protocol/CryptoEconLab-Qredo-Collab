import numpy as np
from typing import Tuple


def forecast_service_fee_locked_vec(
    parms_dict: dict,
    token_price_vec: np.array,
    service_fees_vec: np.array,
) -> np.array:
    # Forecast locked tokens from Service Fees tipped to the network
    tipping_rate = parms_dict["tipping_rate"]
    slippage = parms_dict["slippage"]
    service_fee_locked_vec = (
        tipping_rate * service_fees_vec * (1 - slippage)
    ) / token_price_vec
    return service_fee_locked_vec
