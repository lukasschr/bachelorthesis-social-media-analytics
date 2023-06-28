import datetime

from langdetect import detect
from tqdm import tqdm
import pandas as pd

from src.data.nitter_scraper_standalone_v2 import Tweet, TweetScraper
from src.utils import logger


class CleaningPipeline:
    """Data cleaning pipeline for tweet data.

    Note: The data must be in the form of a list of Tweet objects in a PKL file!

    Attributes:
        path: path to twitter_tweets_raw.pkl
    """
    def __init__(self, path) -> None:
        logger.info('initialize pipeline and load raw dataframe...')
        self.df = pd.read_feather(path)

    def run(self):
        """Execute the cleaning pipeline.

        Returns:
            df (pandas.DataFrame): the cleaned dataframe.
        """
        logger.warning('starting data cleaning...')
        logger.info('formating date...')
        self.df['date'] = pd.to_datetime(self.df['date']).dt.tz_localize(None)

        if not self._text_without_null_values():
            logger.warning('entries without text data were found!')
            logger.info('clean _text_without_null_values...')
            self.df.dropna(subset=['rawContent'], inplace=True)
        
        if not self._creation_date_in_period():
            logger.warning('entries that were created outside of the specified period were found!')
            logger.info('clean _creation_date_in_period...')
            posts_not_in_period = self.df.query('date < "2022-10-01" or date > "2023-03-31"')
            self.df.drop(index=posts_not_in_period.index, inplace=True)

        if not self._no_duplicates():
            logger.warning('duplicate entries were found!')
            logger.info('clean _no_duplicates...')
            self.df.drop_duplicates(subset=['rawContent'], inplace=True)

        if not self._all_texts_in_english():
            logger.warning('entries which are not in english were found!')
            logger.info('clean _all_texts_in_english...')
            non_english_posts = self.df.query('lang != "en"')
            self.df.drop(index=non_english_posts.index, inplace=True)

        self.df.drop(columns=['lang', 'replyCount', 'retweetCount', 'likeCount'], inplace=True)
        self.df.set_index('url', inplace=True)
        self.df.reset_index(inplace=True)
        logger.info('data cleaning completed successfully!')
        return self.df
    

    def _text_without_null_values(self):
        if self.df['rawContent'].isnull().any():
            return False
        else:
            return True
        
    def _creation_date_in_period(self):
        if self.df.query('date < "2018-04-01" or date > "2023-04-01"').empty:
            return True
        else:
            return False
        
    def _no_duplicates(self):
        if self.df['rawContent'].duplicated().any():
            return False
        else:
            return True
        
    def _all_texts_in_english(self):
        if self.df['lang'].eq('en').all():
            return True
        else:
            return False