import os
import pandas as pd
import numpy as np
from mechaqredo.params import default_params_dict
from mechaqredo.sim import run_param_sweep_sim
from generate_scenarios import generate_full_scenario

# Function to check and create the "data" folder if it doesn't exist
def create_data_folder(data_folder:str='data'):
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

# Check and create the "data" folder
DATA_FOLDER='data'
create_data_folder(DATA_FOLDER)

# Explanation: This script performs a parameter sweep simulation using the
# MechAQREDO framework. It loads wallet balances data, sets up simulation
# parameters, generates a full scenario, and runs the parameter sweep.

# Set up warnings
import warnings
warnings.filterwarnings('ignore')

# Set up file paths
code_dir = os.path.realpath(os.path.join(os.getcwd(), ".."))
file = os.path.realpath("../data/balances.csv")

# Load wallet balances data
wallet_df = pd.read_csv(file)

# Set up simulation parameters
N_sims = 2
forecast_length = 365 * 3
data_dict_n_samples = 3

# Set up parameter ranges for the parameter sweep
param_ranges_dict = {
    "tipping_rate": [0.05, 0.2, 0.4],
    "validator_reward_share": list(np.linspace(0, 1, 5)),
    "min_stake_amount": [
        wallet_df.quantile(0.01).values[0],
        wallet_df.quantile(0.05).values[0],
        wallet_df.quantile(0.1).values[0],
        wallet_df.quantile(0.2).values[0]
    ],
    "staking_rewards_vesting_decay_rate": [
        np.log(2) / (3.0 * 365),
        np.log(2) / (4.0 * 365),
        np.log(2) / (5.0 * 365)
    ],
    "min_stake_duration": [7 * 2, 7 * 4, 7 * 8]
}

# Load default parameters
params_dict = default_params_dict(forecast_length)
params_dict["wallet_balances_vec"] = wallet_df["balance"].values

# Generate full scenario based on scenario dictionary
#########################################################
#
#
#    CHANGE THIS !
#
#
########################################################
SCENARIO_DICT = {
    'service_fee_model': 'very bad',
    'price_model': 'very bad',
    'n_validators': 'very bad',
    'n_trx': 'very bad'
}

params_dict = generate_full_scenario(
    params_dict=params_dict,
    scenarios_dict=SCENARIO_DICT,
    forecast_length=forecast_length
)

# Run parameter sweep simulation
sweep_df = run_param_sweep_sim(
    forecast_length,
    params_dict,
    param_ranges_dict,
    data_dict_n_samples,
    save=True,
    output_dir=DATA_FOLDER,
    scenario='very_bad'
)
sweep_df.to_csv(DATA_FOLDER+'/agg_very_bad.csv')
