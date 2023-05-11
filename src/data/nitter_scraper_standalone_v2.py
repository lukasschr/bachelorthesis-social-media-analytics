from dataclasses import dataclass
import datetime
import time
import pickle
import os
import argparse
import logging
import urllib.parse

# import dependencies: selenium, bs4 & tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium

from bs4 import BeautifulSoup

from tqdm import tqdm


# - Exception classes
class NextPageNotFound(Exception):
    """Raises when no other page with tweets can be found for the current search parameters"""


# - Data classes
@dataclass
class Tweet:
    """A data class for Twitter tweets."""
    url:str
    date:str
    rawContent:str


class TweetScraper():
    """Web scraper for the nitter.net website
    
    A scraper that can collect and save Twitter posts from nitter.net

    Attributes:
        ratelimit: limits the request speed (in seconds)
    """
    def __init__(self, ratelimit=0.5) -> None:
        self.ratelimit = ratelimit
        self.__id = int(datetime.datetime.now().timestamp())
        self.driver = webdriver.Firefox() # Warning: Selected browser must be installed on the system!
        self._base_url = 'https://nitter.net/search?f=tweets'

    def collect_tweets(self, nitter_html_source):
        """Parses HTML source for Twitter data.

        Uses bs4 to search the HTML source for the relevant data. 
        The data found are added to a list as Tweets. Finally, the tweets are saved in a file.
        
        Args:
            nitter_html_source: webdriver.page_source object

        Returns:
            list_of_collected_tweets: list of collected tweets
        """
        soup = BeautifulSoup(nitter_html_source, 'html.parser')
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

        self.__save_collected_tweets(list_of_collected_tweets)
        return list_of_collected_tweets

    def search(self, q:str, since:datetime.datetime, until:datetime.datetime, limit:int):
        """Search for tweets that match the search parameters.

        The search continues until the number of tweets specified in limit has been collected.
        Note: Depending on the search parameters, it may happen that the requested number of tweets is not collected.

        Args:
            q: search string (url encoded)
            since: start time of the search
            until: end time of the search
            limit: number of tweets to collect
        """
        # load first page in driver browser
        start_page = self._base_url + f'&q={q}&since={str(since.date())}&until={str(until.date())}&near='
        self.driver.get(start_page)

        # collect tweets until limit reached
        number_of_collected_tweets = 0
        with tqdm(total=limit, leave=False) as pbar:
            while number_of_collected_tweets <= limit:
                try:
                    time.sleep(self.ratelimit) # ratelimit
                    # preload next nitter page and collect tweets on current page
                    collected_tweets = self.collect_tweets(nitter_html_source=self.__request_next_nitter_site())
                except NextPageNotFound:
                    logging.warning('The requested number of tweets could not be collected completely (NextPageNotFound)')
                    break
                number_of_collected_tweets += len(collected_tweets)
                pbar.update(len(collected_tweets))
                self.next_page.click() # go to the next nitter page
            pbar.close()

    @staticmethod
    def load_collected_tweets(path):
        """Load serialized Tweet objects.

        The serialized Tweet objects within the file are returned as a list.

        Args:
            path: path to .pkl file

        Returns:
            tweets: list of Tweet objects
        """
        tweets = []
        with open(path, 'rb') as f:
            while True:
                try:
                    obj = pickle.load(f)
                except EOFError:
                    break
                tweets.append(obj)
        return tweets
           
    def __request_next_nitter_site(self):
        # preload next nitter page
        try:
            self.next_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="show-more"]')))
        except selenium.common.exceptions.TimeoutException:
            raise NextPageNotFound
        # return current html source
        nitter_html_source = self.driver.page_source
        return nitter_html_source

    def __save_collected_tweets(self, list_of_collected_tweets):
        # creates required folders
        path = f'./.nss/{self.id}'
        if not os.path.exists(path):
            os.makedirs(path)
        # save every tweet in list_of_collected_tweets
        for tweet in list_of_collected_tweets:
            with open(f'{path}/data.pkl', 'ab') as f:
                pickle.dump(tweet, f)


    def __get_id(self):
        return self.__id
    
    def __set_id(self, value):
        self.__id = value

    id = property(__get_id, __set_id)


class RecoveryFile():
    """Manages the recovery file.

    Contains static methods to manage the .recovery file. 
    This can be used to continue the script where it left off
    """
    @staticmethod
    def read(path):
        """Reads the .recovery as a PKL file and returns the recovery_data."""
        with open(path , 'rb') as f:
            recovery_data = pickle.load(f)
        return recovery_data

    @staticmethod
    def write(path, recovery_data:dict):
        """Writes the .recovery as a PKL file"""
        with open(path, 'wb') as f:
            pickle.dump(recovery_data, f)


def scrape(q:str, since:datetime.datetime, until:datetime.datetime, limit:int, id=None):
    """Collects tweets over a period of time

    Collects the required number of tweets between the start and end times each day to reach the limit.

    Args:
        q: search string (url encoded)
        since: start time of the search
        until: end time of the search
        limit: number of tweets to collect    
    """
    ts = TweetScraper()
    if id:
        ts.id = id
    number_of_tweets_per_day = limit // ((until - since).days)
    iteration_date = until
    while iteration_date > since:
        logging.info(f'\ncollect ~ {number_of_tweets_per_day} tweets : {iteration_date - datetime.timedelta(days=1)} - {iteration_date}')
        ts.search(
            q=q,
            since=iteration_date - datetime.timedelta(days=1),
            until=iteration_date,
            limit=number_of_tweets_per_day
        )
        logging.info('tweet collection is complete!')
        iteration_date -= datetime.timedelta(days=1)
        logging.info('update recovery file')
        RecoveryFile.write(
            path=f'./.nss/{ts.id}/.recovery', 
            recovery_data={'id': ts.id, 
                           'q': q, 
                           'since': since, 
                           'until': iteration_date, 
                           'limit': limit - len(ts.load_collected_tweets(path=f'./.nss/{ts.id}/data.pkl'))}
        )
        logging.info('Done.')


if __name__ == '__main__':
    # setup logging
    logging.basicConfig(
        format='%(levelname)s   %(message)s',
        level=logging.INFO
    )
    # setup cli with argparse
    parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('mode', choices=['scraper', 'recovery'], help='')
    args, unknown = parser.parse_known_args()

    if args.mode == 'scraper':
        scraper_parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
        scraper_parser.add_argument('-q', '--querystring', required=True, help='')
        scraper_parser.add_argument('-t', '--period', nargs=2, required=True, help='Start- und Endzeitpunkt')
        scraper_parser.add_argument('-l', '--limit', required=True, help='')       
        scraper_args, scraper_unknown = scraper_parser.parse_known_args(unknown)

        i = input(
f'''
Welcome! Please check and confirm your entries for the scraper.

Query: {urllib.parse.unquote(scraper_args.querystring)}
Period of time: {str(datetime.datetime.strptime(scraper_args.period[0], '%Y-%m-%d'))} - {str(datetime.datetime.strptime(scraper_args.period[1], '%Y-%m-%d'))}
Total number of tweets to be collected: {scraper_args.limit}

Are these entries correct? (y/n): '''
)
        if i.lower() == 'y':
            print('')
            scrape(
                q=str(scraper_args.querystring),
                since=datetime.datetime.strptime(scraper_args.period[0], '%Y-%m-%d'),
                until=datetime.datetime.strptime(scraper_args.period[1], '%Y-%m-%d'),
                limit=int(scraper_args.limit)
            )
            logging.info('Scraping successfully completed!')
        else:
            print('Please restart the script and check your entries :)\n')
    
    elif args.mode == 'recovery':
        recovery_parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
        recovery_parser.add_argument('path', help='')
        recovery_parser, recovery_unknown = recovery_parser.parse_known_args(unknown)

        logging.info('load parameters from recovery file')
        params = RecoveryFile.read(recovery_parser.path)
        logging.info('parameters loaded successfully. continue scraping...')
        scrape(q=params['q'], since=params['since'], until=params['until'], limit=params['limit'], id=params['id'])

    else:
        raise Exception # this exception should not occur due to 'choices'