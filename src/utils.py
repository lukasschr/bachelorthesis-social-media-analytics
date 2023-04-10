import pickle
import os

def safe_as_pkl(obj, filename:str, path:str):
    """Serial object.

    Object is saved as a .pkl file in the specified location.

    Args:
        obj: the object to be serialized
        filename: name of the .pkl file
        path: location
    """
    with open(f'{path}/{filename}.pkl', 'wb') as f:
        pickle.dump(obj, f)


def cache(obj, caching_token:str):
    """Serial multiple objects.

    Opens a .pkl file and appends the given object

    Args:
        obj: the object to be serailized and appended
        caching_token: path of the .pkl file
    """
    if not os.path.exists('../.cache'):
        os.mkdir('../.cache')
    with open(f'../.cache/{caching_token}.pkl', 'ab') as f:
        pickle.dump(obj, f)


def load_pkl(path):
    """Load serialized objects.

    The serialized objects within the file are de-serialized and returned as a list

    Args:
        path: path to .pkl file

    Returns:
        List of de-serialized objects
    """
    objs = []
    with open(path, 'rb') as f:
        while True:
            try:
                obj = pickle.load(f)
            except EOFError:
                break
            objs.append(obj)
    return objs