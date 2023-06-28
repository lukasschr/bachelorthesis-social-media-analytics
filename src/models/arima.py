import pandas as pd

class ArimaModel:
    def __init__(self) -> None:
        self._topic_id = None
        self._label = None
        self._data = None
        self._data_train = None
        self._data_test = None
        self._stationary = None
        self._model = None

    # Getter & Setter

    def __get_topic_id(self):
        return self._topic_id
    
    def __set_topic_id(self, v:int):
        self._topic_id = v

    def __get_label(self):
        return self._label
    
    def __set_label(self, v:str):
        self._label = v

    def __get_data(self):
        return self._data

    def __set_data(self, v:pd.DataFrame):
        self._data = v

    def __get_data_train(self):
        return self._data_train
    
    def __set_data_train(self, v:pd.DataFrame):
        self._data_train = v

    def __get_data_test(self):
        return self._data_test
    
    def __set_data_test(self, v:pd.DataFrame):
        self._data_test = v

    def __get_stationary(self):
        return self._stationary
    
    def __set_stationary(self, v:dict):
        self._stationary = v

    def __get_model(self):
        return self._model
    
    def __set_model(self, v):
        self._model = v

    topic_id = property(__get_topic_id, __set_topic_id)
    label = property(__get_label, __set_label)
    data = property(__get_data, __set_data)
    data_train = property(__get_data_train, __set_data_train)
    data_test = property(__get_data_test, __set_data_test)
    stationary = property(__get_stationary, __set_stationary)
    model = property(__get_model, __set_model)

