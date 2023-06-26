#!/usr/bin/env python
# coding: utf-8
import sys
import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from tqdm import tqdm
from multiprocessing import Pool
import warnings
matplotlib.use('Agg')
warnings.filterwarnings('ignore')
code_dir = os.path.realpath(os.path.join(os.getcwd(), ".."))
sys.path.append(code_dir)
from mechaqredo.params import default_params_dict
from mechaqredo.sim import estimate_sensitivity
from mechaqredo.generate_scenarios import generate_full_scenario
outfolder = os.path.realpath("../data/sensitivities")
matplotlib.use('Agg')

SIMULATION_LENGHT=365 * 2
Ntr=26

sd = {"service_fee_model": 'base', "price_model": 'base', "n_validators": 'base', "n_trx": 'base'}
list_of_params=['protocol_funded_rate',
 'initial_stake_convertion_rate',
  'rewards_reinvest_rate',
  'staking_renewal_rate',
  'tipping_rate',
  'protocol_fee_rate',
  'min_stake_amount',
  'validator_reward_share',
  'staking_rewards_vesting_decay_rate',
  'release_rate_a',
  'max_rate']

cols=['circ_supply',
      'staking_rewards_vested',
       'staking_rewards_ecosystem',
       'total_staking_rewards', 
       'validators_rewards', 
       'market_cap',
       'staking_tvl',
       'year_inflation',
       'apy', 
       'tvl_rate']


def compute_estimate_sensitivity(p, i,tr):
    params=default_params_dict(SIMULATION_LENGHT)
    params = generate_full_scenario(
    params_dict=params, scenarios_dict=sd, forecast_length=SIMULATION_LENGHT)
    params[p]=tr[i]

    return estimate_sensitivity(SIMULATION_LENGHT, with_respect_to=p, input_params_dict=params, N=20)

def main(debug=False):
    code_dir = os.path.realpath(os.path.join(os.getcwd(), ".."))
    sys.path.append(code_dir)
    outfolder = os.path.realpath("../data/sensitivities")

    for p in tqdm(list_of_params):
        if  p=='min_stake_amount':
            tr=10000*np.linspace(0,1,Ntr)
        elif p=='initial_stake_convertion_rate':
            tr=0.1*np.linspace(0,1,Ntr)
        else:
            tr=np.linspace(0,1,Ntr)

        time=np.arange(SIMULATION_LENGHT)
        derivatives=np.zeros((len(tr),len(time)))
 
        if debug==False:
            with Pool() as pool:
                df_list = pool.starmap(compute_estimate_sensitivity, [(p,i,tr) for i in range(Ntr)])
        
        else:
            df_list=[]
            for i in range(Ntr):
                df_list.append(compute_estimate_sensitivity(p,i,tr))
                
                
        
        
        for c in cols:
            derivatives = np.array([df_list[i][c].values for i in range(Ntr)])
            TR,TIME=np.meshgrid(tr,time)

            plt.figure(figsize=(16,9))
            plt.rcParams.update({'font.size': 22})
            pp=plt.contourf(TR,TIME,derivatives.T,60,cmap=cm.Spectral)
            plt.colorbar(pp)
            plt.tight_layout()
            plt.ylabel('time (days)')
            plt.xlabel(p.replace('_',' '))
            plt.xlim([0,tr[-1]])
            plt.ylim([0,SIMULATION_LENGHT])
            if c=='year_inflation':
                plt.ylim([SIMULATION_LENGHT/2,SIMULATION_LENGHT])

            plt.title(f'sensitivities_{c}_wrt_{p}'.replace('_',' '))
            plt.savefig(f'{outfolder}/sensitivities_{c}_wrt_{p}.png')

if __name__ == "__main__":
    main(debug=True)





