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
    


class BurnFees:
    """
    The BurnFees class is used to model the burn fees of a protocol. 
    It provides several models to calculate the burn fees.
    """
    
    def __init__(self, model: str, protocol_fees: float,
                 scheduled: np.ndarray = None,
                 Bextra: np.ndarray = None,
                 distr: callable = None,
                 rate: float = None,
                 Bf_constant: float = 0.):
        """
        Initializes the BurnFees object with a specific model, protocol fees, 
        schedule, extra burn fees, distribution function, rate, and burn fee constant.
        """
        assert model in ['constant', 'linear', 'scheduled', 'poisson', 'distr'], \
            "Invalid model. Must be 'constant', 'linear', 'scheduled', 'poisson', or 'distr'."
        
        if model == 'constant' and Bf_constant is None:
            raise ValueError("Number of arrivals must be provided for the constant model")
        if model =='linear' and rate is None:
            raise ValueError("need rate for linear number of arrivals")
        if model =='scheduled' and scheduled is None:
            raise ValueError("need schedule of arrivals for the scheduled model")
        if model =='poisson' and rate is None:
            raise ValueError("need rate for the Poisson model")
        if model =='distribution' and distr is None:
            raise ValueError("need disitrbution for distribution model")
        

        self.burns_list= [Bf_constant* protocol_fees]
            
        self.protocol_fees = protocol_fees
        self.model = model
        self.Bextra_list = Bextra 
        self.Bfees_list = [0]
        self.Bf_constant = Bf_constant
        self.rate = rate
        self.scheduled = scheduled
        self.distr = distr

    def update(self):
        """
        Updates the service fees based on the chosen model.
        """
        if self.Bextra_list is not None:
        
            be = self.Bextra_list[len(self.burns_list)-1]
        else:
         be=0
        f=self.protocol_fees
        if self.model == 'constant':
            self.Bfees_list.append(f*self.Bf_constant)
        elif self.model == 'linear':
            self.Bfees_list.append(f*int(self.rate * len(self.burns_list) + self.burns_list[0]))
        elif self.model == 'scheduled':
            self.Bfees_list.append(f*self.scheduled[len(self.burns_list)-1])
        elif self.model == 'poisson':
            self.Bfees_list.append(f*np.random.poisson(lam=self.rate))
        elif self.model == 'distr':
            self.Bfees_list.append(f*self.distr())

        # Adds both sources
        self.burns_list.append(be + self.Bfees_list[-1])
    
    def current_burns(self):
        """
        Returns the current daily service fees.
        """
        return self.burns_list[-1]


    
        
if __name__=='__main__':
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 18})
    plt.figure(figsize=(16,9))
    PROTOCOL_FEES=0.1
    # initialize the price with GBM model
    Af = ServiceFees('ou', A0=100, mu=100,sigma=10,theta=5)
    Af_gbm=ServiceFees('gbm', A0=100, mu=.300,sigma=.10,theta=5)
    Af_l=ServiceFees('linear', A0=100, a=0.05)
    
    #
    Bf_c = BurnFees('constant', protocol_fees=PROTOCOL_FEES,Bf_constant=30)
    Bf_po=BurnFees('poisson', protocol_fees=PROTOCOL_FEES,rate=20)
    Bf_l=BurnFees('linear', protocol_fees=PROTOCOL_FEES,rate=0.1)
    # simulate the price for 1 year
    for _ in range(365):
        Af.update()
        Af_gbm.update()
        Af_l.update()

        Bf_c.update()
        Bf_l.update()
        Bf_po.update()
    
    plt.plot(Af.fees_list,label='OU')
    plt.plot(Af_gbm.fees_list,label='GBM')
    plt.plot(Af_l.fees_list,label='linear')
    plt.hlines(100,0,365,label='Initial',color='C3',linestyles='dashed')
    plt.legend() 
    plt.title('Service fees models')
    plt.xlabel('t')
    plt.ylabel('USD')
    
    plt.show()
    
    plt.figure(figsize=(16,9))

    plt.plot(Bf_po.burns_list,label='Poisson')
    plt.plot(Bf_l.burns_list,label='linear')
    plt.plot(Bf_c.burns_list,label='constant')
    plt.legend() 
    plt.title('Protocol fees models')
    plt.xlabel('t')
    plt.ylabel('QRDO')
    
        
