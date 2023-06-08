#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This is the price module for QRDO

Created on Wed Jun  7 21:35:56 2023

@author: juanpablomadrigalcianci
"""

import numpy as np

class Price:
    def __init__(self, model: str, P0: float, drift: float = None, sigma: float = None, dt: float = 1/365):
        """
        Constructor of the Price class.
        
        model: The model to use ('constant' or 'gbm').
        P0: The initial price of the asset.
        drift: The expected return of the asset.
        sigma: The standard deviation of the asset returns.
        dt: The time step size.
        """
        if model == 'gbm' and (drift is None or sigma is None):
            raise ValueError("Drift and sigma must be provided for the GBM model")
        self.model = model
        self.drift = drift
        self.sigma = sigma
        self.price_list = [P0]
        self.dt = dt
    
    def update(self):
        """
        Update the asset price based on the chosen model.
        """
        if self.model == 'constant':
            self.price_list.append(self.price_list[-1])
        elif self.model == 'gbm':
            self.price_list.append(self._gbm())

    def _gbm(self):
        """
        Calculate the next price using the Geometric Brownian Motion model.
        """
        p0 = self.price_list[-1]
        drift = (self.drift - 0.5 * self.sigma ** 2.) * self.dt
        vol = self.dt ** 0.5 * self.sigma * np.random.standard_normal()
        return p0 * np.exp(drift + vol)
    
    def current_price(self):
        """
        Return the current asset price.
        """
        return self.price_list[-1]
    
        
if __name__=='__main__':
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 18})
    plt.figure(figsize=(16,9))
    # initialize the price with GBM model
    p = Price('gbm', P0=100, drift=0.5, sigma=0.2)
    
    # simulate the price for 1 year
    for _ in range(365):
        p.update()

    plt.plot(p.price_list,label='GBM')
    plt.title('Price models')
    plt.ylabel('Price')
    plt.xlabel('t')
    
    p = Price('constant', P0=100, drift=0.2, sigma=0.2)
    
    # simulate the price for 1 year
    for _ in range(365):
        p.update()

    plt.plot(p.price_list,label='Constant')
    plt.legend()
    
    
    