import pickle
import logging

from tqdm import tqdm


class Logger:
    """
    A custom logger class for logging messages with various log levels.

    Attributes:
        logger (logging.Logger): The logger object responsible for handling log messages.
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # define the format of the log messages
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # create a StreamHandler that outputs the messages to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        
        # add the StreamHandler to the logger
        self.logger.addHandler(console_handler)
logger = Logger().logger # initialize logger


def safe_as_pkl(obj, path:str):
    """Serial object.

    Object is saved as a .pkl file in the specified location.

    Args:
        obj (object): the object to be serialized
        path (str): location
    """
    with open(f'{path}', 'wb') as f:
        pickle.dump(obj, f)


def load_pkl(path):
    """Load serialized objects.

    The serialized objects within the file are de-serialized and returned as a list.
    Note: If only one object is de-serialized, then only the object is returned instead of a list

    Args:
        path (str): path to .pkl file

    Returns:
        List of de-serialized objects OR de-serialized object
    """
    objs = []
    with open(path, 'rb') as f:
        while True:
            try:
                obj = pickle.load(f)
            except EOFError:
                break
            objs.append(obj)
    if len(objs) > 1:
        return objs
    else:
        return objs[0]
    

def tweet_topic_assignment(lda_model, topic_minimum_probability:float=0.4):
    # iterate over each document in the corpus and assign it the most likely topic
    topics = []
    for doc in tqdm(lda_model.corpus, total=len(lda_model.corpus)):
        doc_topics = lda_model.model.get_document_topics(doc, minimum_probability=topic_minimum_probability)
        # check if a topic was found with sufficient probability (minimum_probability)
        if doc_topics:
            doc_topics = [int(_[0]) for _ in doc_topics] # transform to list of topics
        else:
            doc_topics = None
        topics.append(doc_topics)
    
    return topics