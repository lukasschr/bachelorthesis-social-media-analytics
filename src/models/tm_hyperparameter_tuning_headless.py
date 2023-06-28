import argparse
import os

from src.models import tm_hyperparameter_tuning as ht
from src.utils import load_pkl
import pandas as pd


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('--path_dataframe', required=True, help='')
    parser.add_argument('--path_params', required=True, help='')
    args, unknown = parser.parse_known_args()

    search_space = load_pkl(args.path_params)

    df = ht.random_search(args.path_dataframe, search_space)
    df.to_feather(os.path.join('data', 'modeling', 'ht_results_randomsearch.feather'))

# python tm_hyperparameter_tuning_headless.py --path_dataframe '../../data/processed/twitter_tweets_processed.feather' --path_params '../../data/modeling/tm_ht_search_space.pkl'