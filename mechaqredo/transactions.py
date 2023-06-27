#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transaction module for Qredo's tokenomic model
Created on Wed Jun  7 21:57:54 2023

@author: juanpablomadrigalcianci
"""

import numpy as np


class ServiceFees:
    def __init__(
        self,
        model: str,
        A0: float,
        a: float = None,
        drift: float = None,
        sigma: float = None,
        dt: float = 1 / 365,
        theta: float = None,
        defined_path: np.array = None,
    ):
        """
        Constructor of the ServiceFees class.

        model: The model to use ('constant', 'linear', 'gbm', or 'ou')
            Here 'gbm' stands for Geometric Brownian Motion and 'ou' stands for Orhnstein-Uhllenbeck.
        A0: The initial daily service fees.
        a: The daily rate of growth in service fees (required for 'linear' model).
        drift: The expected return of the service fees (required for 'gbm' model) OR expected service fees in OU process.
        sigma: The standard deviation of the service fees returns (required for 'gbm' model).
        dt: The time step size.
        theta: ???
        """
        # TODO: add description for the theta input
        if model == "linear" and a is None:
            raise ValueError("Growth rate 'a' must be provided for the linear model")
        if model == "gbm" and (drift is None or sigma is None):
            raise ValueError("drift and sigma must be provided for the GBM model")
        if model == "ou" and (drift is None or sigma is None or theta is None):
            raise ValueError(
                "Order and data must be provided for the OU model"
            )  # TODO: fix this warning!
        self.model = model
        self.a = a
        self.drift = drift
        self.sigma = sigma
        self.fees_list = []
        self.A0 = A0
        self.dt = dt
        self.theta = theta
        self.defined_path = defined_path

    def update(self):
        """
        Update the service fees based on the chosen model.
        """
        if self.model != "defined_path":
            if len(self.fees_list) == 0:
                self.fees_list.append(self.A0)
            else:
                if self.model == "constant":
                    self.fees_list.append(self.fees_list[-1])
                elif self.model == "linear":
                    self.fees_list.append(
                        self.a * len(self.fees_list) + self.fees_list[0]
                    )
                elif self.model == "gbm":
                    self.fees_list.append(self._gbm())
                elif self.model == "ou":
                    self.fees_list.append(self._ou())
        else:
            i = min(len(self.fees_list), len(self.defined_path))
            base_fee = self.defined_path[i]
            random_noise = self.sigma * np.random.standard_normal()
            self.fees_list.append(base_fee + random_noise)

    def _gbm(self):
        """
        Calculate the next service fee using the Geometric Brownian Motion model.
        """
        A0 = self.fees_list[-1]
        drift = (self.drift - 0.5 * self.sigma**2.0) * self.dt
        vol = self.dt**0.5 * self.sigma * np.random.standard_normal()
        return A0 * np.exp(drift + vol)

    def _ou(self):
        """
        Calculate the next service fee using the Ohrnstein Ullenbeck model.
        """
        x0 = self.fees_list[-1]
        x1 = (
            x0
            + self.dt * (self.theta * (self.drift - x0))
            + self.sigma * self.dt**0.5 * np.random.standard_normal()
        )
        return x1

    def current_fees(self):
        """
        Return the current daily service fees.
        """
        return self.fees_list[-1]


class NumTransactions:
    """
    The NumTransactions class is used to model the number fo transactions executed by the protocol.
    It provides several models to calculate the number fo transactions.
    """

    def __init__(
        self,
        model: str,
        schedule: np.ndarray = None,
        distr: callable = None,
        fun: callable = None,
        rate: float = None,
        N_trx_constant: float = 0.0,
    ):
        """
        Initializes the NumTransactions object with a specific model,
        schedule, distribution function, rate, or N_trx_constant constant.
        """
        assert model in [
            "constant",
            "linear",
            "scheduled",
            "poisson",
            "distr",
            "function",
        ], "Invalid model. Must be 'constant', 'linear', 'scheduled', 'function','poisson', or 'distr'."

        if model == "constant" and N_trx_constant is None:
            raise ValueError(
                "Number of arrivals must be provided for the constant model"
            )
        if model == "linear" and rate is None:
            raise ValueError("need rate for linear number of arrivals")
        if model == "scheduled" and schedule is None:
            raise ValueError("need schedule of arrivals for the scheduled model")
        if model == "poisson" and rate is None:
            raise ValueError("need rate for the Poisson model")
        if model == "distribution" and distr is None:
            raise ValueError("need disitrbution for distribution model")
        if model == "function" and fun is None:
            raise ValueError("need function for function model")

        self.model = model
        self.N_trx_list = []
        self.N_trx_constant = N_trx_constant
        self.rate = rate
        self.schedule = schedule
        self.distr = distr
        self.fun = fun

    def update(self):
        """
        Updates the no. transactions based on the chosen model.
        """
        if self.model == "constant":
            self.N_trx_list.append(self.N_trx_constant)
        elif self.model == "linear":
            self.N_trx_list.append(
                max(int(self.rate * len(self.N_trx_list) + self.N_trx_constant), 0)
            )
        elif self.model == "scheduled":
            self.N_trx_list.append(self.schedule[len(self.N_trx_list)])
        elif self.model == "poisson":
            self.N_trx_list.append(np.random.poisson(lam=self.rate))
        elif self.model == "distr":
            self.N_trx_list.append(self.distr())
        elif self.model == "function":
            t = len(self.N_trx_list)
            self.N_trx_list.append(self.fun(t))

    def current_transaction_count(self):
        """
        Returns the current number of daily transactions.
        """
        return self.N_trx_list[-1]


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 18})
    plt.figure(figsize=(16, 9))
    PROTOCOL_FEES = 0.1
    # initialize the service fees with GBM model
    Af = ServiceFees("ou", A0=100, mu=100, sigma=10, theta=5)
    Af_gbm = ServiceFees("gbm", A0=100, mu=0.300, sigma=0.10, theta=5)
    Af_l = ServiceFees("linear", A0=100, a=0.05)

    # initialize the daily transaction coutns
    T = 365
    schedule = 40 * np.sin(np.arange(T) / (30 * np.pi)) ** 2
    Bf_c = NumTransactions("constant", N_trx_constant=30)
    Bf_po = NumTransactions("poisson", rate=20)
    Bf_l = NumTransactions("linear", rate=0.1)
    Bf_s = NumTransactions("scheduled", schedule=schedule)
    Bf_f = NumTransactions("function", fun=lambda t: 20 + np.cos(t))

    # simulate the service fee volumes and transactipn counts for 1 year
    for _ in range(T):
        Af.update()
        Af_gbm.update()
        Af_l.update()

        Bf_c.update()
        Bf_l.update()
        Bf_po.update()
        Bf_s.update()
        Bf_f.update()

    # Plots
    plt.figure(figsize=(16, 9))
    plt.plot(Af.fees_list, label="OU")
    plt.plot(Af_gbm.fees_list, label="GBM")
    plt.plot(Af_l.fees_list, label="linear")
    plt.hlines(100, 0, 365, label="Initial", color="C3", linestyles="dashed")
    plt.legend()
    plt.title("Service fees models")
    plt.xlabel("t")
    plt.ylabel("USD")
    plt.show()

    plt.figure(figsize=(16, 9))
    plt.plot(Bf_po.N_trx_list, label="Poisson")
    plt.plot(Bf_l.N_trx_list, label="linear")
    plt.plot(Bf_c.N_trx_list, label="constant")
    plt.plot(Bf_s.N_trx_list, label="scheduled")
    plt.plot(Bf_f.N_trx_list, label="function")
    plt.legend()
    plt.title("Transaction counts models")
    plt.xlabel("t")
    plt.ylabel("QRDO")
    plt.show()
