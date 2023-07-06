import pandas as pd
from src.utils import logger
import xgboost as xgb
from sklearn.metrics import mean_absolute_error


class XGBoostModel2:

    def __init__(self, id:int, timeseries:pd.DataFrame) -> None:
        self._id = id
        self._timeseries = timeseries

        self.FEATURES = ['day', 'week', 'month', 'weekday']
        self.TARGET = 'count'

    @staticmethod
    def train_test_split(data:pd.DataFrame, train_size:float):
        split = int(train_size * len(data))
        data_train, data_test = data[:split], data[split:]
        return data_train, data_test
    
    def create_features(self, data:pd.DataFrame):
        data['day'] = data.index.day
        data['week'] = data.index.isocalendar().week.astype(int)
        data['month'] = data.index.month
        data['weekday'] = data.index.weekday
        return data

    def build(self, **kwargs):
        data_train_with_features = self.create_features(self._data_train.copy())
        data_test_with_features = self.create_features(self._data_test.copy())

        X_train = data_train_with_features[self.FEATURES]
        y_train = data_train_with_features[self.TARGET]

        X_test = data_test_with_features[self.FEATURES]
        y_test = data_test_with_features[self.TARGET]

        reg = xgb.XGBRegressor(**kwargs)
        reg.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=False)
        
        self._predictions = reg.predict(X_test)
        return self._predictions

    def evaluate(self):
        return mean_absolute_error(self._data_test[self.TARGET], self._predictions)
        
    def __get_id(self):
        return self._id
    
    def __get_timeseries(self):
        return self._timeseries

    def __get_label(self):
        return self._label
    
    def __set_label(self, v:str):
        self._label = v

    def __get_data_train(self):
        return self._data_train
    
    def __set_data_train(self, v:pd.DataFrame):
        self._data_train = v

    def __get_data_test(self):
        return self._data_test
    
    def __set_data_test(self, v:pd.DataFrame):
        self._data_test = v

    def __get_predictions(self):
        return self._predictions

    id = property(__get_id)
    timeseries = property(__get_timeseries)
    label = property(__get_label, __set_label)

    data_train = property(__get_data_train, __set_data_train)
    data_test = property(__get_data_test, __set_data_test)

    predictions = property(__get_predictions)


def process_to_timeseries(df_topic_assigned:pd.DataFrame):
    """Creates time series from the data.

    This counts how often tweets from a topic occur per day.

    Args:
        df_topic_assigned (pd.DataFrame): dataframe where a topic has been assigned to each entry
    
    Returns:
        df_topic_grouped_ts (pd.Dataframe): dataframe where a time series was created for each topic
    """
    logger.warning(f"{df_topic_assigned['topics'].isnull().sum()} tweets could not be assigned to a topic! -> Drop...")
    df_topic_assigned.dropna(inplace=True)

    # explode on the "topics" column to convert each combination of values into separate rows
    df_topic_assigned = df_topic_assigned.explode('topics')
    df_topic_assigned.rename(columns={'topics': 'topic'}, inplace=True)

    # resample the df to daily frequency, grouping by 'topics' and counting occurrences
    df_topic_assigned = df_topic_assigned.groupby('topic').resample('1D', on='date').size().rename('count').reset_index().set_index('date')

    # group the DataFrame by 'topics'
    df_topic_grouped_ts = df_topic_assigned.groupby('topic')
    return df_topic_grouped_ts