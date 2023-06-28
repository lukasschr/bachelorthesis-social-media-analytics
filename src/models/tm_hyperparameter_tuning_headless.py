import argparse
import os

from src.models import tm_hyperparameter_tuning as ht
from src.utils import load_pkl
import pandas as pd


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('search_method', choices=['random', 'grid'], help='')
    parser.add_argument('--path_dataframe', required=True, help='')
    parser.add_argument('--path_params', required=True, help='')
    parser.add_argument('--multicore', action='store_true', help='')
    args, unknown = parser.parse_known_args()

    list_parameter_combinations = load_pkl(args.path_params)

    if args.search_method == 'random':
        df = ht.random_search(args.path_dataframe, list_parameter_combinations, args.multicore)
        df.to_feather(os.path.join('data', 'modeling', 'ht_results_randomsearch.feather'))
    
    elif args.search_method == 'grid':
        df = ht.grid_search(args.path_dataframe, list_parameter_combinations, args.multicore)
        df.to_feather(os.path.join('data', 'modeling', 'ht_results_gridsearch.feather'))