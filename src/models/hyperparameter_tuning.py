import random

from src.models import topic_modeling as tm
from src.utils import logger
import pandas as pd
from tqdm import tqdm


def random_search(path:str, list_parameter_combinations:list, multicore:bool=False):
    """Random Search Hyperparameter Tuning.

    Randomly selects a parameter constellation from a list of hyperparameters and calculates the model. 
    This process continues until the while loop is interrupted with a keyboard interrupt.

    Args:
        path (str): path to the .FEATHER file of the preprocessed dataframe
        list_parameter_combinations (list): list of parameter combinations. The combinations must be available as DICT
        multicore (bool, optional): determines whether multiprocessing should be used for the calculations

    Returns:
        pandas.DataFrame: a dataframe containing the results of the calculated models
    """
    text_data = pd.read_feather(path)['preprocessed_text']
    random.shuffle(list_parameter_combinations)

    results = []
    try:
        while True:
            dict_parameter_combination = list_parameter_combinations.pop()
            logger.info(f'Initialize tuning; parameters: {str(dict_parameter_combination)}')
            
            if multicore:
                lda_model = tm.LdaMulticoreModel(text=text_data)
                lda_model.build(**dict_parameter_combination)
            else:
                lda_model = tm.LdaModel(text=text_data)
                lda_model.build(**dict_parameter_combination)

            cs = tm.evaluate(model=lda_model.model, text=lda_model.text, dictionary=lda_model.dictionary)
            _ = {**{'seed': lda_model.seed}, **dict_parameter_combination, **{'coherence_score': cs}}
            del lda_model
            results.append(_)
            logger.info('Done. \n')
    except KeyboardInterrupt:
        pass

    return pd.DataFrame(results)


def grid_search(path:str, list_parameter_combinations:list, multicore:bool=False):
    """Grid Search Hyperparameter Tuning.

    Iterates over each possible parameter constellation from a given list and calculates the model. 
    The process can be aborted with a keyboard interrupt, but it shouldn't be

    Args:
        path (str): path to the .FEATHER file of the preprocessed dataframe
        list_parameter_combinations (list): list of parameter combinations. The combinations must be available as DICT
        multicore (bool, optional): determines whether multiprocessing should be used for the calculations

    Returns:
        pandas.DataFrame: a dataframe containing the results of the calculated models
    """
    text_data = pd.read_feather(path)['preprocessed_text']

    results = []
    try:
        for dict_parameter_combination in tqdm(list_parameter_combinations, total=len(list_parameter_combinations)):
            logger.info(f'Initialize tuning; parameters: {str(dict_parameter_combination)}')
            
            if multicore:
                lda_model = tm.LdaMulticoreModel(text=text_data)
                lda_model.build(**dict_parameter_combination)
            else:
                lda_model = tm.LdaModel(text=text_data)
                lda_model.build(**dict_parameter_combination)

            cs = tm.evaluate(model=lda_model.model, text=lda_model.text, dictionary=lda_model.dictionary)
            _ = {**{'seed': lda_model.seed}, **dict_parameter_combination, **{'coherence_score': cs}}
            del lda_model
            results.append(_)
            logger.info('Done. \n')
    except KeyboardInterrupt:
        pass

    return pd.DataFrame(results)