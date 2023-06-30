from dataclasses import dataclass

import pandas as pd
from src.utils import logger
import xgboost as xgb


@dataclass
class TopicTimeSeriesData:
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
        """Splits the data into a training and test data set.

        Based on train_size the dataset is split.

        Args:
            train_size (float): size of the training data set in percent

        Returns:
            data_train (pd.DataFrame): training data
            data_test (pd.DataFrame): test data
        """
        split = int(train_size * len(self.data))
        self.data_train, self.data_test = self.data[:split], self.data[split:]
        return self.data_train, self.data_test
    
    def build(self, **kwargs):
        """Builds the XGB Model.

        Uses XGRRegressor to compute the models.

        Args:
            **kwargs: all common parameters and their values that can be passed

        Returns:
            model (xgb.XGBRegressor): the computed model
        """
        X_train = self.data_train_features[self.FEATURES]
        y_train = self.data_train_features[self.TARGET]
        X_test = self.data_test_features[self.FEATURES]
        y_test = self.data_test_features[self.TARGET]

        # create and train the model
        reg = xgb.XGBRegressor(**kwargs)
        reg.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=False)
        self.model = reg

        # predict
        self.data_test_features_predictions = self.data_test_features.assign(predictions=reg.predict(X_test))

        return self.model
        

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