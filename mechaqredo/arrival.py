#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 21:53:10 2023
"""

import numpy as np


class Arrival:
    def __init__(
        self,
        rate: int = None,
        constant_rate: float = None,
        list_of_precomputed_arrivals: np.ndarray = None,
        initial_number: int = 0,
    ):
        """
        Constructor of the Arrival class.

        rate: A constant arrival rate.
        constant_rate: A constant arrival rate. If provided, rate will be ignored.
        list_of_precomputed_arrivals: A precomputed list of arrivals. If provided, it will override both rate and constant_rate.
        initial_number: The initial number of arrivals.
        """
        self.rate = rate
        self.constant_rate = constant_rate
        self.list_of_precomputed_arrivals = list_of_precomputed_arrivals
        self.initial_number = initial_number
        self.arrival_list = []
        self.interarrival_times = [0]
        self.counter = 0

    def update(self):
        """
        Update the arrival process based on the specified rate or precomputed arrivals.
        """
        if len(self.arrival_list) == 0:
            num_arrivals = self.initial_number
        else:
            if self.list_of_precomputed_arrivals is not None:
                if len(self.arrival_list) < len(self.list_of_precomputed_arrivals):
                    num_arrivals = self.list_of_precomputed_arrivals[
                        len(self.arrival_list)
                    ]
            else:
                if self.rate is not None:
                    num_arrivals = np.random.poisson(self.rate)

                if self.constant_rate is not None:
                    # This is to include rates <1
                    if self.constant_rate < 1:
                        if self.counter < int(1 / self.constant_rate):
                            num_arrivals = 0
                            self.counter += 1
                        else:
                            num_arrivals = 1
                            self.counter = 0
                    else:
                        num_arrivals = self.constant_rate

                if num_arrivals < 1:
                    self.interarrival_times[-1] += 1

        self.arrival_list.append(np.floor(self.arrival_list[-1] + num_arrivals))

        if num_arrivals == 0:
            self.interarrival_times[-1] += 1
        else:
            self.interarrival_times.append(0)

    def current_arrivals(self):
        """
        Return the current number of arrivals.
        """
        return self.arrival_list[-1]


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 18})
    plt.figure(figsize=(16, 9))

    precomputed_arrivals = [0 if np.random.random() < 0.7 else 1 for _ in range(365)]

    # Initialize the arrival process with a Poisson rate
    a1 = Arrival(rate=1 / 5)
    # Initialize the arrival process with a constant rate
    a2 = Arrival(constant_rate=1 / 7)
    # Initialize the arrival process with a vector of arrivals
    a3 = Arrival(list_of_precomputed_arrivals=precomputed_arrivals)
    # Simulate the arrival process for 1 year
    for _ in range(365):
        a1.update()
        a2.update()
        a3.update()

    plt.plot(np.arange(len(a2.arrival_list)), a2.arrival_list, label="Constant Rate")
    plt.plot(np.arange(len(a1.arrival_list)), a1.arrival_list, label="Poisson arrival")
    plt.plot(np.arange(len(a3.arrival_list)), a3.arrival_list, label="Precomputed")

    plt.title("Arrival Process")
    plt.ylabel("Number of Arrivals")
    plt.xlabel("t")
    plt.legend()
    plt.ylim([0, 120])
    plt.show()
