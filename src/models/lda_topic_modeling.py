import time

from gensim import corpora, models


class Model():
    """LDA Topic Model.
    
    This class contains functions for creating, managing and evaluating topic models. 
    It is an LDA topic model, which is calculated using gensim.
    
    Attributes:
        text: A list of preprocessed text
        multicore: Number of processors that can be used for the calculations ( > 0 = ldamulticore)
    """
    def __init__(self, text, multicore):
        self.multicore = multicore
        self.text = text


    def build(self, **kwargs):
        """Build the LDA model.

        Calculates the LDA model. Depending on multicore, either method LdaModel or method 
        LdaMulticore is selected.

        Args:
            kwargs: Takes all common parameters and their values that can be passed to the 
            LdaMulticore function. Ex:
                num_topics, alpha, eta, passes

        Returns:
            lda_model: the calculated LDA model
            dictionary: the dictionary used
            int(start_time): used seed/random_state
            calculation_time: Time required for the calculation in minutes
        """
        dictionary = corpora.Dictionary(self.text) # create a dictionary/id2word
        corpus = [dictionary.doc2bow(text) for text in self.text] # create a corpus

        start_time = time.time()
        if self.multicore == 0:
            lda_model = models.LdaModel(corpus=corpus, id2word=dictionary, **kwargs, 
                                        random_state=int(start_time))
        else:
            lda_model = models.ldamulticore.LdaMulticore(corpus=corpus, id2word=dictionary, 
                                                         workers=self.multicore, **kwargs, 
                                                         random_state=int(start_time))    
        end_time = time.time()
        calculation_time = (end_time - start_time) / 60  # in minutes
        return lda_model, dictionary, int(start_time), calculation_time


    def evaluate(self, model, text, dictionary):
         """Calculates metrics for checking accuracy.

         Calculates the following metrics: Coherence Score, ...

         Args:
            model: LDA Model
            text: the text used to create the model
            dictionary: the dictionary used to create the model

         """
         # calculate coherence score
         coherence_model_lda = models.coherencemodel.CoherenceModel(model=model, texts=text, 
                                                                    dictionary=dictionary, coherence='c_v')
         coherence_score = coherence_model_lda.get_coherence()
         # todo: more metrics ...
         return coherence_score