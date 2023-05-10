"""
Author: Lukas Schroeder
Version: 0.1
"""

from dataclasses import dataclass
import datetime
import time
import pickle
import os
import argparse
import logging
import json
import urllib.parse

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup


@dataclass
class Tweet:
    url:str
    date:str
    rawContent:str


class Scraper():
    def __init__(self, ratelimit:int=1) -> None:
        self.ratelimit = ratelimit
        self.wkdir = None

    def _setup(self, id, q:str, since:datetime.datetime, until:datetime.datetime, limit:int, iteration_search):
        logging.info('  ~  create ./.nss folder and create .info, .recovery and data files')
        self.wkdir = f'./.nss/{id}'
        if not os.path.exists(self.wkdir):
            os.makedirs(self.wkdir)
        
        with open(f'{self.wkdir}/.info', 'w') as f:
            json.dump({
                'id': id,
                'q': urllib.parse.unquote(q),
                'period_of_time': f'{str(since)} - {str(until)}',
                'limit': limit
            }, f)
        
        with open(f'{self.wkdir}/.recovery', 'w') as f:
            json.dump({
                'params': {
                    'q': q,
                    'since': str(since),
                    'until': str(until),
                    'limit': limit
                },
                'iteration_search': iteration_search,
            }, f)
        
        with open(f'{self.wkdir}/data.pkl', 'wb') as f:
            pickle.dump([], f)
        logging.info('  ~  Done.')

    @staticmethod
    def load_data(path:str):
        tweets = []
        with open(path, 'rb') as f:
            while True:
                try:
                    obj = pickle.load(f)
                except EOFError:
                    break
                tweets.append(obj)
        return tweets


class TweetScraper(Scraper):
    def __init__(self, ratelimit:int=1) -> None:
        super().__init__(ratelimit=ratelimit)
        self._base_url = 'https://nitter.net/search?f=tweets'

    def search(self, q:str, since:datetime.datetime, until:datetime.datetime, limit:int=100):
        if self.wkdir == None:
            self.wkdir = input('wkdir: ')
        
        _since, _until = str(since.date()), str(until.date())
        search_url = f'{self._base_url}&q={q}&since={_since}&until={_until}&near='
        
        try:
            driver = webdriver.Firefox()
        except:
            try:
                driver.quit()
            except:
                pass
            time.sleep(10)
            driver = webdriver.Firefox()
        driver.get(search_url)

        number_of_collected_tweets = 0
        while number_of_collected_tweets <= limit:
            logging.info(f'  ~  ({_since} - {_until}): {number_of_collected_tweets} / {limit}')
            time.sleep(self.ratelimit)
            try:
                next_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="show-more"]')))
            except selenium.common.exceptions.TimeoutException:
                logging.warning('  ~  the requested data could not be collected completely')
                logging.info('  ->  break loop')
                break

            current_page_source = driver.page_source
            
            soup = BeautifulSoup(current_page_source, 'html.parser')
            tweet_containers = soup.find_all("div", class_="timeline-item")

            list_of_collected_tweets = []
            for tweet in tweet_containers:
                try:
                    tweet_url = f"https://twitter.com{tweet.find('a', class_='tweet-link')['href']}"
                    tweet_date = tweet.find('span', class_='tweet-date').find('a')['title']
                    tweet_content = tweet.find('div', class_='tweet-content').text.strip()

                    _ = Tweet(tweet_url, tweet_date, tweet_content)
                    
                    list_of_collected_tweets.append(_)
                except:
                    pass
            
            for tweet in list_of_collected_tweets: # cache / save
                with open(f'{self.wkdir}/data.pkl', 'ab') as f:
                    pickle.dump(tweet, f)

            number_of_collected_tweets += len(list_of_collected_tweets)
            del list_of_collected_tweets

            next_page.click()

        driver.quit()
        return since, until, number_of_collected_tweets

    def iteration_search(self, intervall, **kwargs):
        if intervall == 'daily':
            since = kwargs['since']
            until = kwargs['until']

            posts_to_be_collected_per_day = kwargs['limit'] // ((until - since).days)
            total_number_of_tweets_collected = 0

            iteration_date = until
            while iteration_date > since:
                self.search(
                    q=kwargs['q'], 
                    since=iteration_date - datetime.timedelta(days=1), 
                    until=iteration_date,
                    limit=posts_to_be_collected_per_day)

                iteration_date -= datetime.timedelta(days=1)
                with open(f'{self.wkdir}/.recovery', 'w') as f:
                    json.dump({
                        'params': {
                            'q': kwargs['q'],
                            'since': str(since),
                            'until': str(iteration_date),
                            'limit': kwargs['limit'] - len(Scraper.load_data(path=f'{self.wkdir}/data.pkl'))
                        },
                        'iteration_search': 'daily'
                    }, f)


class UserScraper(Scraper):
    def __init__(self, ratelimit:int=1) -> None:
        super().__init__(ratelimit=ratelimit)
        # to do


if __name__ == '__main__':
    # setup logging
    logging.basicConfig(
        format='%(levelname)s %(message)s',
        level=logging.INFO
    )

    # setup cli with argparse
    parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('mode', choices=['scraper', 'recovery'], help='')
    args, unknown = parser.parse_known_args()

    if args.mode == 'scraper':
        scraper_parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
        scraper_parser.add_argument('scraper', choices=['tweet-scraper', 'user-scraper'], help='')
        scraper_args, scraper_unknown = scraper_parser.parse_known_args(unknown)
    
        if scraper_args.scraper == 'tweet-scraper':
            tweet_parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
            tweet_parser.add_argument('-q', '--querystring', required=True, help='')
            tweet_parser.add_argument('-t', '--period', nargs=2, required=False, help='Start- und Endzeitpunkt')
            tweet_parser.add_argument('-l', '--limit', required=False, help='')
            tweet_parser.add_argument('--iteration_search', choices=['daily'], help='')        
            tweet_args, tweet_unknown = tweet_parser.parse_known_args(unknown)

            scraper = TweetScraper()
            params = {}

            params.update({'q': tweet_args.querystring})

            if tweet_args.period:
                since = datetime.datetime.strptime(tweet_args.period[0], '%Y-%m-%d')
                until = datetime.datetime.strptime(tweet_args.period[1], '%Y-%m-%d')
            else:
                since = until = datetime.datetime.now()
            params.update({'since': since, 'until': until})

            if tweet_args.limit:
                limit = tweet_args.limit
                params.update({'limit': int(limit)})

            if tweet_args.iteration_search:
                if not tweet_args.period and not tweet_args.limit:
                    raise Exception
                scraper._setup(
                    id=int(datetime.datetime.now().timestamp()),
                    **params,
                    iteration_search=tweet_args.iteration_search)
                logging.warning('  ~  start nitter_scraper iteration search algorithm... \n')
                scraper.iteration_search(tweet_args.iteration_search, **params)
            else:
                scraper._setup(
                    id=int(datetime.datetime.now().timestamp()),
                    **params,
                    iteration_search=None)
                logging.warning('  ~  start nitter_scraper search algorithm... \n')
                scraper.search(**params)
                
        elif args.scraper == 'user-scraper':
            raise NotImplementedError

        else:
            raise Exception # this exception should not occur due to 'choices'
        
    elif args.mode == 'recovery':
        recovery_parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
        recovery_parser.add_argument('path', help='')
        recovery_args, recovery_unknown = recovery_parser.parse_known_args(unknown)

        with open(recovery_args.path) as f:
            rec = json.load(f)

        params = rec['params']
        params['since'] = datetime.datetime.strptime(params['since'], '%Y-%m-%d %H:%M:%S')
        params['until'] = datetime.datetime.strptime(params['until'], '%Y-%m-%d %H:%M:%S')
        
        scraper = TweetScraper()

        if rec['iteration_search']:
            logging.warning('  ~  start nitter_scraper iteration search algorithm... \n')
            scraper.iteration_search(rec['iteration_search'], **params)
        else:
            logging.warning('  ~  start nitter_scraper search algorithm... \n')
            scraper.search(**rec['params'])

    else:
        raise Exception # this exception should not occur due to 'choices'