import random
import time

from src.models import topic_modeling as tm
from src.utils import logger
import pandas as pd
import pickle
# import gc


def random_search(path:str, search_space:list):
    """Random Search Hyperparameter Tuning.

    Randomly selects a parameter constellation from a list of hyperparameters and calculates the model. 
    This process continues until the while loop is interrupted with a keyboard interrupt.

    Args:
        path (str): path to the .FEATHER file of the preprocessed dataframe
        list_parameter_combinations (list): list of parameter combinations. The combinations must be available as DICT

    Returns:
        pandas.DataFrame: a dataframe containing the results of the calculated models
    """
    text_data = pd.read_feather(path)['preprocessed_text']
    base_lda_model = tm.LdaMulticoreModel(text=text_data)
    random.shuffle(search_space)

    best_cs = 0
    results = []
    try:
        while True:
            dict_parameter_combination = search_space.pop()
            logger.info(f'Initialize random tuning; parameters: {str(dict_parameter_combination)}')
            
            start_time = time.time()

            m, s = base_lda_model.build(**dict_parameter_combination)

            cs = tm.evaluate(model=lda_model.model, text=lda_model.text, dictionary=lda_model.dictionary)
            if cs > best_cs:
                best_cs = cs
            _ = {**{'seed': s}, **dict_parameter_combination, **{'coherence_score': cs}}
            _cache_objects(_)
            results.append(_)
            # gc.collect() # python garbage collection

            calculation_time = round((time.time() - start_time) / 60, 2)

            logger.info(f'Done. (Model #{len(results)}); Calculation time: {calculation_time}; Currently best value: {best_cs}\n')
    except KeyboardInterrupt:
        pass

    return pd.DataFrame(results).astype(str)

def _cache_objects(obj):
    with open(f'cache_hyperparameter_tuning.pkl', 'ab') as f:
        pickle.dump(obj, f)