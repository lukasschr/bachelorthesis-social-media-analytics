from dataclasses import dataclass

import pandas as pd
from tqdm import tqdm
from src.utils import logger


@dataclass
class TimeSeries:
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
    
    data_train_features:pd.DataFrame = None
    data_test_features:pd.DataFrame = None

    data_test_features_predictions:pd.DataFrame = None

    model = None

    def train_test_split(self, train_size:float):
        split = int(train_size * len(self.data))
        self.data_train, self.data_test = self.data[:split], self.data[split:]
        return self.data_train, self.data_test


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