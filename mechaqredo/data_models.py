import numpy as np
from typing import List

from .transactions import NumTransactions, ServiceFees
from .price import Price
from .arrival import Arrival


def build_model_data_dict(forecast_length: int, params_dict: dict) -> dict:
    n_txs_vec = forecast_daily_trx_counts(forecast_length, params_dict)
    token_price_vec = forecast_token_price(forecast_length, params_dict)
    service_fees_vec = forecast_service_fees(forecast_length, params_dict)
    n_val_vec = forecast_num_validators(forecast_length, params_dict)
    data_dict = {
        "n_txs": n_txs_vec,
        "token_price": token_price_vec,
        "service_fees": service_fees_vec,
        "n_validators": n_val_vec,
    }
    return data_dict


def build_model_data_dict_samples(
    n_samples: int, forecast_length: int, params_dict: dict
) -> List[dict]:
    data_dict_list = []
    for _ in range(n_samples):
        data_dict = build_model_data_dict(forecast_length, params_dict)
        data_dict_list.append(data_dict)
    return data_dict_list


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
    for i in range(forecast_length - 1):
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
    for i in range(forecast_length - 1):
        fees_model.update()
    fees_vec = np.array(fees_model.fees_list)
    return fees_vec


def forecast_num_validators(forecast_length: int, params_dict: dict) -> np.array:
    n_val_params_dict = params_dict["n_validators_model"]
    n_val_model = Arrival(
        n_val_params_dict["rate"],
        n_val_params_dict["constant_rate"],
        n_val_params_dict["list_of_precomputed_arrivals"],
        n_val_params_dict["initial_number"],
    )
    for i in range(forecast_length):
        n_val_model.update()
    n_val_vec = np.array(n_val_model.arrival_list)
    return n_val_vec
