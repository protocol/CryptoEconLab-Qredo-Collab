#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 23:07:28 2023
@author: juanpablomadrigalcianci
"""

class CircSupply:
    def __init__(self, initial_circulating_supply:float, initial_price:float):
        # Initializing circulating supply, inflation rate, and market capitalization lists
        self.circ_supply_list = [initial_circulating_supply]
        self.inflation_rate_list = [0]
        self.market_capitalization_list = [initial_circulating_supply * initial_price]
        
    def update(self, vesting, burns, staking, price):
        """Update supply, market capitalization, and inflation rate.
            Here, vesting, burns,staking and price are the modules 
            that represent these actions
        """
        self.circ_supply_list.append(self._updateSupply(vesting, burns, staking))
        self.market_capitalization_list.append(self._updateMarketCap(price))
        self.inflation_rate_list.append(self._updateInflationRate())

    def current_supply(self):
        """Return the current supply."""
        return self.circ_supply_list[-1]
    
    def _updateSupply(self, vesting, burns, staking):
        """Update the new supply."""
        new_supply = self.current_supply()
        new_supply += -burns.current_burn() + staking.current_out()
        new_supply += -staking.current_in() + vesting.current_vesting()
        return new_supply
    
    def _updateMarketCap(self, price):
        """Update the market capitalization."""
        return price.current_price() * self.current_supply()
    
    def _updateInflationRate(self):
        """Update the inflation rate."""
        return (self.current_supply() - self.circ_supply_list[-2]) / self.circ_supply_list[-2]



    