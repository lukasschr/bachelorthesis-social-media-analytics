import argparse
import logging
import os

from src import utils
import pandas as pd


PERIOD_OF_COLLECTED_POSTS_START='2023-01-01'
PERIOD_OF_COLLECTED_POSTS_END='2023-03-31'


def _creation_date_in_period(raw_df):
    _ = raw_df.copy()
    _['date'] = pd.to_datetime(_.date).dt.tz_localize(None)
    if _.query(
        f'date < "{str(PERIOD_OF_COLLECTED_POSTS_START)}" or date > "{str(PERIOD_OF_COLLECTED_POSTS_END)}"').empty:
        return True
    else:
        return False

def _text_without_null_values(raw_df):
    if raw_df['rawContent'].isnull().any():
        return False
    else:
        return True

def _no_duplicates(raw_df):
    if raw_df['rawContent'].duplicated().any():
        return False
    else:
        return True

def _all_texts_in_english(raw_df):
    if raw_df['lang'].eq('en').all():
        return True
    else:
        return False


def clean(raw_df):
    """Cleans a RAW Dataframe.
    
    Checks whether the dataframe meets the requirements and cleans up errors.

    Args:
        raw_df: pandas Dataframe in RAW state (as it results from twitter_scraper.py)
    
    Returns:
        Cleaned pandas dataframe
    """
    logging.warning('Start cleaning process...')
    if not _text_without_null_values(raw_df):
        logging.warning('There are entries without text data! ~ clean...')
        raw_df.dropna(subset=['rawContent'], inplace=True)
    
    if not _creation_date_in_period(raw_df):
        logging.warning('There are entries that were created outside of the specified period! ~ clean...')
        posts_not_in_period = raw_df.query(
            f'date < "{str(PERIOD_OF_COLLECTED_POSTS_START)}" or date > "{str(PERIOD_OF_COLLECTED_POSTS_END)}"')
        raw_df.drop(index=posts_not_in_period.index, inplace=True)

    if not _all_texts_in_english(raw_df):
        logging.warning('There are entries which are not in English! ~ clean...')
        non_english_posts = raw_df.query('lang != "en"')
        raw_df.drop(index=non_english_posts.index, inplace=True)

    if not _no_duplicates(raw_df):
        logging.warning('There are duplicate text entries! ~ clean...')
        raw_df.drop_duplicates(subset=['rawContent'], inplace=True)

    # format date
    logging.info('Format date')
    raw_df['date'] = pd.to_datetime(raw_df['date']).dt.tz_localize(None)

    # delete irrelevant columns
    logging.info('Delete irrelevant columns')
    raw_df.drop(columns=['renderedContent', 'id', 'user', 'replyCount', 'retweetCount', 'likeCount', 
                     'quoteCount', 'conversationId', 'lang', 'source', 'sourceUrl', 'sourceLabel', 
                     'links', 'media', 'retweetedTweet', 'quotedTweet', 'inReplyToTweetId', 'inReplyToUser', 
                     'mentionedUsers', 'coordinates', 'place', 'hashtags', 'cashtags', 'card', 'viewCount', 
                     'vibe'], inplace=True)
    
    raw_df.set_index('url', inplace=True)
    raw_df.reset_index(inplace=True)
    logging.info('Cleaning process complete!')
    return raw_df


if __name__ == '__main__':
    # setup logging
    logging.basicConfig(
        format='%(levelname)s %(message)s',
        level=logging.INFO
    )

    # setup cli with argparse
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    parser = argparse.ArgumentParser(description='Cleans a pandas dataframe.', 
                                    epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('path', help='Path to a .PKL file containing a pandas dataframe')
    parser.add_argument('-sd', '--startdate', help='PERIOD_OF_COLLECTED_POSTS_START')
    parser.add_argument('-ed', '--enddate', help='PERIOD_OF_COLLECTED_POSTS_END')
    args = parser.parse_args()

    if args.startdate:
        PERIOD_OF_COLLECTED_POSTS_START=args.startdate
    if args.enddate:
        PERIOD_OF_COLLECTED_POSTS_END=args.enddate

    # load raw dataframe
    logging.info('Load dataset...')
    raw_df = utils.load_pkl(path=args.path)[0]
    
    cleaned_df = clean(raw_df=raw_df)
    cleaned_df.to_feather(
        f"{os.path.join(PROJECT_ROOT, 'data', 'intermediate')}/twitter_tweets_intermediate.feather")