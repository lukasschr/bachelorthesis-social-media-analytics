import pickle

def safe_as_pkl(obj, filename:str, path:str):
    """Serial objects.

    Object is saved as a .pkl file in the specified location.

    Args:
        obj: the object to be serialized
        filename: name of the .pkl file
        path: location
    """
    with open(f'{path}/{filename}.pkl', 'wb') as f:
        pickle.dump(obj, f)

def load_pkl(path):
    """Load serialized objects.

    The file specified by path is de-serialized and returned.

    Args:
        path: path to .pkl file

    Returns:
        De-serialized object
    """
    with open(path, 'rb') as f:
        obj = pickle.load(f)
    return obj