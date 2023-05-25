import pickle
import logging


def safe_as_pkl(obj, path:str):
    """Serial object.

    Object is saved as a .pkl file in the specified location.

    Args:
        obj: the object to be serialized
        path: location
    """
    with open(f'{path}', 'wb') as f:
        pickle.dump(obj, f)


def load_pkl(path):
    """Load serialized objects.

    The serialized objects within the file are de-serialized and returned as a list.
    Note: If only one object is de-serialized, then only the object is returned instead of a list

    Args:
        path: path to .pkl file

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
logger = Logger().logger