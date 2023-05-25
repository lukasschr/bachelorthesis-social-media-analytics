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
        logger.info('initialize pipeline and load & transform list of tweets in raw dataframe...')
        self.df = self._get_raw_df(path=path)

    def run(self):
        """Execute the cleaning pipeline.

        Returns:
            df (pandas.DataFrame): the cleaned dataframe.
        """
        logger.warning('starting data cleaning...')
        logger.info('formating date...')
        self.df['date'] = self.df['date'].apply(lambda x: datetime.datetime.strptime(x, "%b %d, %Y · %I:%M %p %Z"))

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

        self.df.drop(columns=['lang'], inplace=True)
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
        if self.df.query('date < "2022-10-01" or date > "2023-03-31"').empty:
            return True
        else:
            return False
        
    def _no_duplicates(self):
        if self.df['rawContent'].duplicated().any():
            return False
        else:
            return True
        
    def _all_texts_in_english(self):
        def _detect_language():
            logger.warning('determine language for each entry...')
            def __detect_language(text):
                try:
                    lang = detect(text)
                except:
                    lang = None
                return lang
            tqdm.pandas()
            # determine the language for each tweet
            self.df['lang'] = self.df['rawContent'].progress_apply(__detect_language)
        
        _detect_language()
        if self.df['lang'].eq('en').all():
            return True 
        else:
            return False


    def _get_raw_df(self, path):
        list_of_tweets = TweetScraper.load_collected_tweets(path=path)
        dict_of_tweets =  [{"url": tweet.url, "date": tweet.date, "rawContent": tweet.rawContent} for tweet in list_of_tweets]
        return pd.DataFrame(dict_of_tweets)
