import itertools
import random
import argparse
import logging
import multiprocessing
import os

from src.models import lda_topic_modeling
from src.utils import send_notification, shutdown
from tqdm import tqdm
import pandas as pd


CORES = multiprocessing.cpu_count() # determines the number of processor cores that can be used for the calculations


class RandomSearch():
    """Hyperparameter Tuning - Random Search method.
    
    This class defines the random search algorithm to find optimal hyperparameters. It is drawn from a very large pool 
    of parameter compositions to create LDA models. A results table is generated that measures the performance of the 
    selected parameters. This can limit the best composition of hyperparameters.

    Note: Since it is not assumed that all parameter compositions can be tried, the aim of this class is only to get 
    a first feel for the composition. A finer search should then be carried out with GridSearch algorithm.

    Attributes:
        limit: Indicates whether only a certain number of combinations should be executed - 
               otherwise the code runs endlessly.
    """
    def __init__(self, limit=False):
        self.limit = limit
        self.df = pd.DataFrame(columns=['random_state', 'num_topics', 'alpha', 'eta', 'passes', 
                                        'calculation_time', 'coherence_score'])
        
        num_topics = [i for i in range(4, 74)]
        alpha = ['symmetric', 'asymmetric'] + [round(i*0.1, 1) for i in range(1, 10)]
        eta = ['symmetric', 'auto'] + [round(i*0.1, 1) for i in range(1, 10)]
        passes = [i for i in range(2, 10)]

        self.hyperparameters = list(itertools.product(num_topics, alpha, eta, passes)) # combinations of all possible 
                                                                                       # parameters form compositions


    def search(self, cores=0):
        """Calculates LDA models and the metrics for evaluating the models.
        
        To do this, a combination of parameters is randomly drawn from list self.hyperparameters. The calculations are 
        then carried out for the drawn parameters. The results are appended to Table self.df.
        
        Args:
            cores: indicates how many processors can be used for the calculations
                   note: if cores > 0, multithreading is used for the calculation
        """
        iteration = 0
        while True:
            logging.info(f'  ~  calculate and evaluate lda model number {str(iteration)} ...')
            random_hyperparameter_choice = self.hyperparameters.pop(random.randrange(0,len(self.hyperparameters)-1))
            
            num_topics = random_hyperparameter_choice[0]
            alpha = random_hyperparameter_choice[1]
            eta = random_hyperparameter_choice[2]
            passes = random_hyperparameter_choice[3]

            topic_modeling = lda_topic_modeling.Model(text=DF['preprocessed_text'], multicore=cores)
            lda_model, dictionary, seed, calculation_time = topic_modeling.build(num_topics=num_topics, alpha=alpha, 
                                                                                 eta=eta, passes=passes)
            cs = topic_modeling.evaluate(model=lda_model, text=DF['preprocessed_text'], dictionary=dictionary)
            
            result = {
                'random_state': seed,
                'num_topics': num_topics,
                'alpha': str(alpha),
                'eta': str(eta),
                'passes': passes,
                'calculation_time': round(calculation_time, 4),
                'coherence_score': cs
            }

            self.df.loc[len(self.df)] = result
            self.df.to_feather(f"{os.path.join(PROJECT_ROOT, 'models')}/hyperparameter_tuning_results<_randomsearch.feather")
            
            avg_calculation_time = self.df['calculation_time'].mean()
            logging.info(f"""  ~  Done. Model {iteration} calculated successfully! Calculation time: {round(calculation_time, 4)} minutes; average calculation time: {round(avg_calculation_time, 4)}\n""")
            
            iteration += 1
            if not type(self.limit) == bool:
                if iteration >= self.limit:
                    break


class GridSearch():
    """Hyperparameter Tuning - Random Search method.
    
    This class defines the grid search algorithm to find optimal hyperparameters. For this purpose, all possible 
    hyperparameter combinations are calculated. 
    
    Note: Too many parameters should not be passed, as this increases the calculation time enormously. For a constraint, 
    use the RandomSearch algorithm.
    
    Attributes:
        num_topics: a list of all possible numbers for the topic count
        alpha: a list of all possible values for the alpha value
        eta: a list of all possible values for the eta value
        passes: a list of all possible numbers for the passes value
    """
    def __init__(self, num_topics:list, alpha:list, eta:list, passes:list=[5]):
        self.df = pd.DataFrame(columns=['random_state', 'num_topics', 'alpha', 'eta', 'passes', 
                                        'calculation_time', 'coherence_score'])
        
        num_topics = num_topics
        alpha = self._assign_correct_types(alpha)
        eta = self._assign_correct_types(eta)
        passes = passes

        self.hyperparameters = list(itertools.product(num_topics, alpha, eta, passes))
        
    def search(self, cores=0, server_execution=False):
        """Calculates LDA models and the metrics for evaluating the models.
        
        To do this, a combination of parameters is pulled one by one from the self.hyperparameters list. The 
        calculations are then carried out for the parameters. The results are appended to Table self.df.
        
        Args:
            cores: indicates how many processors can be used for the calculations
                   note: if cores > 0, multithreading is used for the calculation
            server_execution: if the script is running on a server, it might be worth setting this value to True
        """
        for iteration, hyperparameter_combination in tqdm(enumerate(self.hyperparameters), total=len(self.hyperparameters)):
            num_topics = hyperparameter_combination[0]
            alpha = hyperparameter_combination[1]
            eta = hyperparameter_combination[2]
            passes = hyperparameter_combination[3]
            
            topic_modeling = lda_topic_modeling.Model(text=DF['preprocessed_text'], multicore=cores)
            lda_model, dictionary, seed, calculation_time = topic_modeling.build(num_topics=int(num_topics), alpha=alpha, 
                                                                                 eta=eta, passes=passes)
            cs = topic_modeling.evaluate(model=lda_model, text=DF['preprocessed_text'], dictionary=dictionary)
            
            result = {
                'random_state': seed,
                'num_topics': num_topics,
                'alpha': str(alpha),
                'eta': str(eta),
                'passes': passes,
                'calculation_time': round(calculation_time, 4),
                'coherence_score': cs
            }

            self.df.loc[len(self.df)] = result
            self.df.to_feather(f"{os.path.join(PROJECT_ROOT, 'models')}/hyperparameter_tuning_results_gridsearch.feather")
        
        if server_execution:
            send_notification()
            shutdown()


    def _assign_correct_types(self, lst):
        _ = []
        for element in lst:
            try:
                _.append(float(element))
            except ValueError:
                _.append(element)
        return _


if __name__ == '__main__':
    # setup logging
    logging.basicConfig(
        format='%(levelname)s %(message)s',
        level=logging.INFO
    )
    logging.getLogger('gensim').setLevel(logging.ERROR) # prevent gensim from logging

    # setup cli with argparse
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    parser = argparse.ArgumentParser(description='Searches best parameters for LDA model', 
                                     epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('method', choices=['randomsearch', 'gridsearch'], help='select the search method')
    parser.add_argument('path', help="""Path to a .FEATHER file with column 'preprocessed_text'.
                                        This column must contain preprocessed text as lists""")
    # add optional arguments only for grid search
    if parser.parse_known_args()[0].method == 'gridsearch':
        parser.add_argument('--num_topics', nargs='+', help='a list of all possible numbers for the topic count')
        parser.add_argument('--alpha', nargs='+', help='a list of all possible values for the alpha value')
        parser.add_argument('--eta', nargs='+', help='a list of all possible values for the eta value')
        parser.add_argument('--passes', nargs='*', help='a list of all possible numbers for the passes value')
    args = parser.parse_args()
    
    # load dataframe
    logging.info('  ~  load dataset ...')
    DF = pd.read_feather(path=args.path)

    if args.method == 'randomsearch':
        rs = RandomSearch()
        logging.warning('  ~  start random_search algorithm')
        rs.search(cores=CORES) # cores = 0 for simple LDA calculation
    elif args.method == 'gridsearch':
        num_topics=args.num_topics
        alpha=args.alpha
        eta=args.eta
        passes=args.passes
        q = input(f'\nPlease check your entries:\n   num_topics: {num_topics}\n   alpha: {alpha}\n   eta: {eta}\n   passes: {passes}\nAre your entries correct? (y/n): ')
        if q.lower() == 'y':
            if args.passes:
                gs = GridSearch(num_topics=num_topics, alpha=alpha, eta=eta, passes=passes)
            else:
                gs = GridSearch(num_topics=num_topics, alpha=alpha, eta=eta)
            print('')
            logging.warning('  ~  start grid_search algorithm')
            gs.search(cores=CORES, server_execution=True) # cores = 0 for simple LDA calculation
        else:
            print('Please restart the script and check your entries :)\n')
    else:
        raise Exception # this exception should not occur due to 'choices'