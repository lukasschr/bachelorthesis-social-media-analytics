from dataclasses import dataclass

import pandas as pd
from src.utils import logger
import xgboost as xgb


@dataclass
class TopicTimeSeriesData:
    """"""
    id: int
    data: pd.DataFrame
    label: str = None


@dataclass
class XGBoostModel:
    id:int
    label:str
    data:pd.DataFrame
    
    data_train:pd.DataFrame = None
    data_test:pd.DataFrame = None

    FEATURES:list = None
    TARGET:str = None
    
    data_train_features:pd.DataFrame = None
    data_test_features:pd.DataFrame = None

    data_test_features_predictions:pd.DataFrame = None

    model = None
    mae_before_ht = None

    def train_test_split(self, train_size:float):
        split = int(train_size * len(self.data))
        self.data_train, self.data_test = self.data[:split], self.data[split:]
        return self.data_train, self.data_test
    
    def build(self, **kwargs):
        X_train = self.data_train_features[self.FEATURES]
        y_train = self.data_train_features[self.TARGET]
        X_test = self.data_test_features[self.FEATURES]
        y_test = self.data_test_features[self.TARGET]

        # Modell erstellen und trainieren
        reg = xgb.XGBRegressor(**kwargs)
        reg.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=False)
        self.model = reg

        self.data_test_features_predictions = self.data_test_features.assign(predictions=reg.predict(X_test))

        return self.model
        


def process_to_timeseries(df_topic_assigned:pd.DataFrame):
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