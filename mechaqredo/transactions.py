#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transaction module for Qredo's tokenomic model
Created on Wed Jun  7 21:57:54 2023

@author: juanpablomadrigalcianci
"""

import numpy as np
import pandas as pd

class ServiceFees:
    def __init__(self, model: str,
                 A0: float, 
                 a: float = None, 
                 mu: float = None, 
                 sigma: float = None, 
                 dt: float = 1/365, 
                 order: tuple = None,
                 theta:float=None):
        """
        Constructor of the ServiceFees class.
        
        model: The model to use ('constant', 'linear', 'gbm', or 'ou')
            Here 'gbm' stands for Geometric Brownian Motion and 'ou' stands for Orhnstein-Uhllenbeck.  
        A0: The initial daily service fees.
        a: The daily rate of growth in service fees (required for 'linear' model).
        mu: The expected return of the service fees (required for 'gbm' model) OR expected service fees in OU process.
        sigma: The standard deviation of the service fees returns (required for 'gbm' model).
        dt: The time step size.

        data: dat to fit the arima model on
        """
        if model == 'linear' and a is None:
            raise ValueError("Growth rate 'a' must be provided for the linear model")
        if model == 'gbm' and (mu is None or sigma is None):
            raise ValueError("Mu and sigma must be provided for the GBM model")
        if model == 'ou' and (mu is None or sigma is None or theta is None):
            raise ValueError("Order and data must be provided for the OU model")
        self.model = model
        self.a = a
        self.mu = mu
        self.sigma = sigma
        self.fees_list = [A0]
        self.dt = dt
        self.theta=theta
            

    def update(self):
        """
        Update the service fees based on the chosen model.
        """
        if self.model == 'constant':
            self.fees_list.append(self.fees_list[-1])
        elif self.model == 'linear':
            self.fees_list.append(self.a * len(self.fees_list) + self.fees_list[0])
        elif self.model == 'gbm':
            self.fees_list.append(self._gbm())
        elif self.model == 'ou':
            self.fees_list.append(self._ou())
    
    def _gbm(self):
        """
        Calculate the next service fee using the Geometric Brownian Motion model.
        """
        A0 = self.fees_list[-1]
        drift = (self.mu - 0.5 * self.sigma ** 2.) * self.dt
        vol = self.dt ** 0.5 * self.sigma * np.random.standard_normal()
        return A0 * np.exp(drift + vol)
    
    def _ou(self):
        """
        Calculate the next service fee using the Ohrnstein Ullenbeck model.
        """
        x0=self.fees_list[-1]
        x1=x0+self.dt*(self.theta*(self.mu-x0))+self.sigma*self.dt**0.5*np.random.standard_normal()
        return x1
    
    def current_fees(self):
        """
        Return the current daily service fees.
        """
        return self.fees_list[-1]
    
    
        
if __name__=='__main__':
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 18})
    plt.figure(figsize=(16,9))
    # initialize the price with GBM model
    Af = ServiceFees('ou', A0=100, mu=100,sigma=10,theta=5)
    Af_gbm=ServiceFees('gbm', A0=100, mu=.300,sigma=.10,theta=5)
    Af_l=ServiceFees('linear', A0=100, a=0.05)
    # simulate the price for 1 year
    for _ in range(365):
        Af.update()
        Af_gbm.update()
        Af_l.update()

    plt.plot(Af.fees_list,label='OU')
    plt.plot(Af_gbm.fees_list,label='GBM')
    plt.plot(Af_l.fees_list,label='linear')
plt.hlines(100,0,365,label='Initial',color='C3',linestyles='dashed')
plt.legend() 
plt.title('Service fees models')
plt.xlabel('t')
plt.ylabel('USD')
    
        
