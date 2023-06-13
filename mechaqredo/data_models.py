import numpy as np

from transactions import NumTransactions, ServiceFees
from price import Price


def build_model_data_dict(forecast_length: int, params_dict: dict) -> dict:
    n_txs_vec = forecast_daily_trx_counts(forecast_length, params_dict)
    token_price_vec = forecast_token_price(forecast_length, params_dict)
    service_fees_vec = forecast_service_fees(forecast_length, params_dict)
    staking_inflows_vec = np.array(
        [1.0] * forecast_length
    )  # TODO: implement staking inflows
    staking_outflows_vec = np.array(
        [0.0] + [0.5] * (forecast_length - 1)
    )  # TODO: implement staking outflows
    n_val_vec = (
        np.arrange(4, 12, 8 / forecast_length).round().astype(int)
    )  # TODO: implement model for no. of validators
    data_dict = {
        "n_txs_vec": n_txs_vec,
        "token_price_vec": token_price_vec,
        "service_fees_vec": service_fees_vec,
        "staking_inflows_vec": staking_inflows_vec,
        "staking_outflows_vec": staking_outflows_vec,
        "n_val_vec": n_val_vec,
    }
    return data_dict


def forecast_daily_trx_counts(forecast_length: int, params_dict: dict) -> np.array:
    model_params_dict = params_dict["ntxs_model"]
    n_txs_model = NumTransactions(
        model_params_dict["model"],
        model_params_dict["schedule"],
        model_params_dict["distr"],
        model_params_dict["fun"],
        model_params_dict["rate"],
        model_params_dict["N_trx_constant"],
    )
    for i in range(forecast_length):
        n_txs_model.update()
    n_txs_vec = np.array(n_txs_model.N_trx_list)
    return n_txs_vec


def forecast_token_price(forecast_length: int, params_dict: dict) -> np.array:
    token_params_dict = params_dict["token_price_model"]
    price_model = Price(
        token_params_dict["model"],
        token_params_dict["P0"],
        token_params_dict["drift"],
        token_params_dict["sigma"],
        token_params_dict["dt"],
    )
    for i in range(forecast_length):
        price_model.update()
    price_vec = np.array(price_model.price_list)
    return price_vec


def forecast_service_fees(forecast_length: int, params_dict: dict) -> np.array:
    fees_params_dict = params_dict["service_fees_model"]
    fees_model = ServiceFees(
        fees_params_dict["model"],
        fees_params_dict["A0"],
        fees_params_dict["a"],
        fees_params_dict["mu"],
        fees_params_dict["sigma"],
        fees_params_dict["dt"],
        fees_params_dict["theta"],
    )
    for i in range(forecast_length):
        fees_model.update()
    fees_vec = np.array(fees_model.fees_list)
    return fees_vec
