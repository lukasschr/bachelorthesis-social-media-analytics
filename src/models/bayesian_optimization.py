import argparse
import time

import pandas as pd
from hyperopt import fmin, tpe
from sklearn.metrics import mean_absolute_error

from src.models import topic_modeling as tm
from src.models import time_series_forecasting as tsf
from src.utils import logger, load_pkl


def optimize_topic_modeling(path_tweets_processed:pd.DataFrame, search_space:dict, max_evals:int):

    def _target_function(parameter_combination:dict):
        logger.info(f'Model #{len(result_df)}/{max_evals-1}; parameters: {str(parameter_combination)}')

        start_time = time.time()

        lda_model.build(seed=int(time.time()), **parameter_combination)
        cs = tm.evaluate(model=lda_model.model, text=lda_model.text, dictionary=lda_model.dictionary)

        result_df.loc[len(result_df)] = {**{'seed': lda_model.seed}, **{k: str(v) for k, v in parameter_combination.items()}, **{'coherence_score': cs}}
        result_df.to_feather('tm_ht_results.feather')

        calculation_time = round((time.time() - start_time) / 60, 2)
        logger.info(f'Calculation time: {calculation_time} min')

        best_coherence_score = result_df['coherence_score'].max()
        logger.info(f'Currently best value: {best_coherence_score}\n')

        return -cs# value to optimize; negate for maximization

    logger.info('Initialize bayesian optimization')
    text_data = pd.read_feather(path_tweets_processed)['preprocessed_text']
    lda_model = tm.LdaMulticoreModel(text=text_data)

    logger.info('create result dataframe...')
    result_df = pd.DataFrame(columns=['seed'] + list(search_space.keys()) + ['coherence_score'])

    logger.warning('start bayesian optimization algorithm... \n')
    optimized_parameters = fmin(fn=_target_function, space=search_space, algo=tpe.suggest, max_evals=max_evals, verbose=False)
    
    return result_df, optimized_parameters


def optimize_xgb_modeling(xgb_model:tsf.XGBoostModel, search_space:dict, max_evals:int):

    def _target_function(parameter_combination:dict):
        xgb_model.build(**parameter_combination)
        mae = mean_absolute_error(xgb_model.data_test_features[xgb_model.TARGET], xgb_model.data_test_features_predictions['predictions'])
        return mae

    logger.info(f'Start bayesian optimization algorithm for XGB-Model: {xgb_model.label}')
    optimized_parameters = fmin(fn=_target_function, space=search_space, algo=tpe.suggest, max_evals=max_evals)
    logger.info(f'Done. Optimized parameters: {str(optimized_parameters)}')
    
    return optimized_parameters


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('--path_dataframe', required=True, help='')
    parser.add_argument('--path_params', required=True, help='')
    parser.add_argument('--max_evals', required=True, help='')
    args, unknown = parser.parse_known_args()

    search_space = load_pkl(args.path_params)

    optimize_topic_modeling(args.path_dataframe, search_space, int(args.max_evals))

# python bayesian_optimization.py --path_dataframe '../../data/processed/twitter_tweets_processed.feather' --path_params '../../data/modeling/tm_ht_search_space.pkl' --max_evals 200
