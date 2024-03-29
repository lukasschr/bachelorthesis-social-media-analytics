import time
import multiprocessing

from gensim import corpora, models
from src.utils import logger


class ModelNotBuildError(Exception):
    """Raises when the model has not yet been built"""

class LdaModel:
    """Super class for LDA Topic models.

    This class contains functions for creating, managing and evaluating topic models.
    Calculations and evaluations are made with gensim.

    Attributes:
        text: a list of preprocessed text
    """
    def __init__(self, text:list) -> None:
        logger.info('Initialize model; create dictionary and corpus...')
        self._text = text
        self._dictionary = corpora.Dictionary(self._text) # create a dictionary/id2word
        self._corpus = [self._dictionary.doc2bow(text) for text in self._text] # create a corpus
        self._model = None
        self._seed = int(time.time())

    def build(self, seed:int=None, **kwargs):
        """Builds the LDA model.

        Calculates an LDA model using gensim.

        Args:
            seed (int, optional): can be handed over for reproducibility
            **kwargs: all common parameters and their values that can be passed to the LdaModel function
        """
        if not seed == None:
            self._seed = int(seed)
        logger.info('calculate lda model... (this can take a while)')
        self._model = models.LdaModel(corpus=self._corpus, id2word=self._dictionary, **kwargs, 
                                       random_state=self._seed)
        logger.info(f'Done. Model calculated successfully!')
        return self._model
    
    # getter & setter
    def __get_text(self):
        return self._text

    def __get_dictionary(self):
        return self._dictionary

    def __get_corpus(self):
        return self._corpus
    
    def __get_model(self):
        if self._model is not None:
            return self._model
        else:
            raise ModelNotBuildError
        
    def __get_seed(self):
        return self._seed
        
    def __set_seed(self, v:int):
        self._seed = v

    text = property(__get_text)
    dictionary = property(__get_dictionary)
    corpus = property(__get_corpus)
    model = property(__get_model)
    seed = property(__get_seed, __set_seed)

class LdaMulticoreModel(LdaModel):
    """LDA Multicore Model

    In contrast to the super class, uses several CPU cores to calculate LDA models

    Attributes:
        text: a list of preprocessed text
    """
    def __init__(self, text:list) -> None:
        super().__init__(text)
        logger.info('enable multiprocessing...')
        self.cores = multiprocessing.cpu_count()-1 # max number of processor cores that can be used for the calculations

    def build(self, seed:int=None, **kwargs):
        """Builds the LDA model.

        Calculates an LDA model using gensim and multicore.

        Args:
            seed (int, optional): can be handed over for reproducibility
            **kwargs: all common parameters and their values that can be passed to the LdaModel function
        """
        if not seed == None:
            self._seed = int(seed)
        logger.info('calculate lda model...')
        self._model = models.ldamulticore.LdaMulticore(corpus=self._corpus, id2word=self._dictionary, 
                                                        workers=self.cores, **kwargs, 
                                                        random_state=seed) 
        logger.info(f'Done. Model calculated successfully!')
        return self._model


def evaluate(model, text, dictionary):
    """Evaluates existing LDA models

    Calculates metrics that can help evaluate LDA models.

    Args:
        model (gensim.models.LdaModel): Lda Model
        text (list): text used to create the model
        dictionary (dict): dictionary used to create the model
    """
    logger.info('calculate coherence score...')
    # calculate coherence score
    coherence_model = models.coherencemodel.CoherenceModel(model=model, texts=text, dictionary=dictionary, 
                                                            coherence='c_v')
    coherence_score = coherence_model.get_coherence()
    del coherence_model # reclaim memory
    logger.info(f'Done. Coherence score calculated successfully! Score: {coherence_score}')
    return coherence_score