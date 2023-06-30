#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This is the price module for QRDO

Created on Wed Jun  7 21:35:56 2023

@author: juanpablomadrigalcianci
"""

import numpy as np
import yfinance as yf

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

    

def download_data(ticker, period):
    '''
    Downloads the historical price data for the given ticker.
    :param ticker: Ticker symbol for the asset
    :param period: The number of days in the past to download data for
    :return: Returns a Pandas Series of the 'Close' price data
    '''
    end = datetime.today().strftime('%Y-%m-%d')
    start = (datetime.today() - timedelta(days=period)).strftime('%Y-%m-%d')
    data = yf.download(ticker, start, end)
    return data['Close']

def gbm_parameters(price_data):
    '''
    Calculates the parameters for geometric Brownian motion.
    :param price_data: Pandas Series of price data
    :return: (mu, sigma) which are the drift and volatility of the asset
    '''
    returns = price_data.pct_change()
    mu = 365**0.5*returns.mean()
    sigma = 365**0.5*returns.std()
    return mu, sigma

        
if __name__=='__main__':
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    import pandas as pd
    # Downloading the data
    ticker = 'QRDO-USD'  # Substitute with your asset's ticker
    X_days = 183  # Substitute with your desired number of days
    price_data = download_data(ticker, X_days)
    T=120
    Nsim=100
    mean_price=np.zeros(T+1)
    # Getting the GBM parameters
    mu, sigma = gbm_parameters(price_data)
    #initialises
    simulation_dates = pd.date_range(start=price_data.index[-1], periods=T + 2, closed='right')
    plt.figure(figsize=(16,9))
    plt.plot(price_data, label='Historical')

    for n in range(Nsim):
        p = Price('gbm', P0=price_data[-1], drift=mu, sigma=sigma)

        for i in range(T):
            p.update()
        mean_price+=p.price_list
        if n==0:
            plt.plot(simulation_dates,p.price_list,label='realisation', alpha=0.3,color='C1')
        else:
            plt.plot(simulation_dates,p.price_list,alpha=0.3,color='C1')
    plt.plot(simulation_dates,mean_price/Nsim,label='mean price',color='C2')
    plt.title(f'QRDO price, drift {round(mu,2)}, vol {round(sigma,2)}')
    plt.xticks(rotation=45)
    
    
    
    
    
    
    # plt.rcParams.update({'font.size': 18})
    # plt.figure(figsize=(16,9))
    # # initialize the price with GBM model
    
    # # simulate the price for 1 year
    # for _ in range(365):
    #     p.update()

    # plt.plot(p.price_list,label='GBM')
    # plt.title('Price models')
    # plt.ylabel('Price')
    # plt.xlabel('t')
    
    # p = Price('constant', P0=100, drift=0.2, sigma=0.2)
    
    # # simulate the price for 1 year
    # for _ in range(365):
    #     p.update()

    # plt.plot(p.price_list,label='Constant')
    # plt.legend()
    
    
    