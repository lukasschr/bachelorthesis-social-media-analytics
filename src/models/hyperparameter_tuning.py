import itertools
import random
import argparse
import logging
import os

from src.models import lda_topic_modeling
import pandas as pd


class RandomSearch():
    def __init__(self, limit=False):
        self.limit = limit
        self.df = pd.DataFrame(columns=['random_state', 'num_topics', 'alpha', 'eta', 'passes', 
                                        'calculation_time', 'coherence_score'])
        
        num_topics = [i for i in range(4, 74)]
        alpha = ['symmetric', 'asymmetric'] + [round(i*0.1, 1) for i in range(1, 10)]
        eta = ['symmetric', 'auto'] + [round(i*0.1, 1) for i in range(1, 10)]
        passes = [i for i in range(2, 10)]

        self.hyperparameters = list(itertools.product(num_topics, alpha, eta, passes))


    def search(self, cores=0):
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
            self.df.to_feather(f"{os.path.join(PROJECT_ROOT, 'models')}/hyperparameter_tuning_results.feather")
            
            avg_calculation_time = self.df['calculation_time'].mean()
            logging.info(f"""  ~  Done. Model {iteration} calculated successfully! Calculation time: {round(calculation_time, 4)} minutes; average calculation time: {round(avg_calculation_time, 4)}\n""")
            
            iteration += 1
            if not type(self.limit) == bool:
                if iteration >= self.limit:
                    break
        


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
    args = parser.parse_args()
    
    # load dataframe
    logging.info('  ~  load dataset ...')
    DF = pd.read_feather(path=args.path)

    if args.method == 'randomsearch':
        rs = RandomSearch()
        logging.warning('  ~  start random_search algorithm')
        rs.search(cores=10)
    elif args.method == 'gridsearch':
        pass # todo
    else:
        raise Exception # this exception should not occur due to 'choices'
    