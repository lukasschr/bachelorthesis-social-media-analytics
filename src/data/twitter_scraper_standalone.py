from dataclasses import dataclass
import argparse
import datetime
import math
import pickle
import logging
import time

from tqdm import tqdm
import snscrape.modules.twitter as sntwitter
import pandas as pd



@dataclass
class Tweet:
    url:str
    date:str
    rawContent:str
    lang:str
    replyCount:int
    retweetCount:int
    likeCount:int


@dataclass
class Recovery:
    IDENTIFICATION_KEY:str
    querystring:str
    since:datetime.datetime
    until:datetime.datetime
    limit:int


class Logger:
    """
    A custom logger class for logging messages with various log levels.

    Attributes:
        logger (logging.Logger): The logger object responsible for handling log messages.
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # define the format of the log messages
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # create a StreamHandler that outputs the messages to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        # add the StreamHandler to the logger
        self.logger.addHandler(console_handler)


def get_tweets(querystring:str, since:datetime.datetime, until:datetime.datetime, limit:int):
    """
    """
    tweets_to_collect_per_day = math.ceil(limit / ((until - since).days)) # aufrunden
    iteration_date = since
    
    tweets_collected_total = 0
    while iteration_date < until:
        query = f'{querystring} since:{iteration_date.strftime("%Y-%m-%d")} until:{(iteration_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")}'
        logger.info(f'collecting ~ {tweets_to_collect_per_day}: {iteration_date.strftime("%Y-%m-%d")} - {(iteration_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")}')

        list_of_collected_tweets = []
        for i, tweet in tqdm(enumerate(sntwitter.TwitterSearchScraper(query).get_items()), total=tweets_to_collect_per_day):
            if i > tweets_to_collect_per_day:
                break
            else:
                t = Tweet(tweet.url, 
                          tweet.date,
                          tweet.renderedContent,
                          tweet.lang,
                          tweet.replyCount,
                          tweet.retweetCount,
                          tweet.likeCount)
                list_of_collected_tweets.append(t)
        
        logger.info('collection completed successfully!')
        _save_collected_tweets(list_of_collected_tweets)
        tweets_collected_total += len(list_of_collected_tweets)
        del list_of_collected_tweets
        iteration_date += datetime.timedelta(days=1)
        _update_recovery(querystring, iteration_date, until, (limit - tweets_collected_total))
        logger.info('Done.\n')


def transform_to_dataframe(path:str):
    list_of_tweets = []
    with open(path, 'rb') as f:
        while True:
            try:
                obj = pickle.load(f)
            except EOFError:
                break
            list_of_tweets.append(obj)

    dict_of_tweets =  [{'url': tweet.url, 'date': tweet.date, 'rawContent': tweet.rawContent, 'lang': tweet.lang, 'replyCount': tweet.replyCount, 'retweetCount': tweet.retweetCount, 'likeCount': tweet.likeCount} for tweet in list_of_tweets]
    return pd.DataFrame(dict_of_tweets)


def _save_collected_tweets(list_of_collected_tweets:list):
    logger.info('secure collected data')
    for tweet in list_of_collected_tweets:
        with open(f'data_{IDENTIFICATION_KEY}.pkl', 'ab') as f:
            pickle.dump(tweet, f)


def _update_recovery(querystring, since, until, limit):
    logger.info('update recovery file')
    r = Recovery(IDENTIFICATION_KEY, querystring, since, until, limit)
    with open(f'recovery_{IDENTIFICATION_KEY}.pkl', 'wb') as f:
        pickle.dump(r, f)


if __name__ == '__main__':
    logger = Logger().logger # initialize logger

    parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('mode', choices=['scraper', 'recovery'], help='')
    args, unknown = parser.parse_known_args()

    if args.mode == 'scraper':
        scraper_parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
        scraper_parser.add_argument('-q', '--querystring', required=True, help='')
        scraper_parser.add_argument('-t', '--period', nargs=2, required=True, help='Start- und Endzeitpunkt Y-m-d ')
        scraper_parser.add_argument('-l', '--limit', required=True, help='')       
        scraper_args, scraper_unknown = scraper_parser.parse_known_args(unknown)

        IDENTIFICATION_KEY = str(int(datetime.datetime.now().timestamp()))
        
        logger.info(f'IDENTIFICATION_KEY: {IDENTIFICATION_KEY}\n')
        logger.warning(f"\n\nStart Scraper with the following parameters: \nquerystring: {str(scraper_args.querystring)}\nsince: {datetime.datetime.strptime(scraper_args.period[0], '%Y-%m-%d')}\nuntil: {datetime.datetime.strptime(scraper_args.period[1], '%Y-%m-%d')}\nlimit: {str(scraper_args.limit)}\nIf your entries are incorrect, cancel the program within the next 10 seconds!\n")
        time.sleep(15)

        logger.info('start collecting the tweets...')
        get_tweets(
            querystring = str(scraper_args.querystring),
            since = datetime.datetime.strptime(scraper_args.period[0], '%Y-%m-%d'),
            until = datetime.datetime.strptime(scraper_args.period[1], '%Y-%m-%d'),
            limit = int(scraper_args.limit)
        )
        logger.info('Scraping successfully completed!')

    elif args.mode == 'recovery':
        recovery_parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
        recovery_parser.add_argument('file', help='')
        recovery_parser, recovery_unknown = recovery_parser.parse_known_args(unknown)

        with open(recovery_parser.file , 'rb') as f:
            recovery = pickle.load(f)

        IDENTIFICATION_KEY = recovery.IDENTIFICATION_KEY

        get_tweets(
            querystring = recovery.querystring,
            since = recovery.since,
            until = recovery.until,
            limit = recovery.limit
        )

    else:
        raise Exception # this exception should not occur due to 'choices'

        
# TEST: python twitter_scraper_standalone.py scraper -q '(#technology OR #tech OR #innovation) min_faves:1 lang:en' -t 2023-05-26 2023-06-26 -l 777
# PRODUCTION: python twitter_scraper_standalone.py scraper -q '(#technology OR #tech OR #innovation) min_faves:1 lang:en' -t 2018-04-01 2023-04-01 -l 1000000