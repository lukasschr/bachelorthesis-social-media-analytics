import requests
import datetime
import os
import argparse
import logging

from tqdm import tqdm
from src import utils
import praw
import pandas as pd

"""
q: Query term for comments and submissions
after: Restrict results to those made after this epoch time
before: Restrict results to those made before this epoch time
sort_type: 	Parameter used for sort (Accepted: "score", "num_comments", "created_utc")
sort: direction of results ("asc" or "desc")
limit:max 1000
"""

class MinimalPushshiftAPIWrapper():
    def __init__(self, endpoint:str='submission'):
        if endpoint == 'submission':
            self._base_url = 'https://api.pushshift.io/reddit/search/submission?'
        elif endpoint == 'comment':
            # warning
            self._base_url = 'https://api.pushshift.io/reddit/search/comment?' # not tested
        else:
            raise Exception

    def search(self, after:datetime.datetime, before:datetime.datetime, limit_per_day:int=1000, **kwargs):
        logging.warning('  ~  start pushshift search algorithm')
        caching_token = f'cache_reddit_scraper_v2_{str(int(datetime.datetime.now().timestamp()))}'
        num_iterations = ((before - after).days)
        posts_to_collect = ((before - after).days) * limit_per_day
        
        logging.info('  ~  query data from pushshift api... \n')
        pbar = tqdm(total=num_iterations)
        iteration_date = after
        while iteration_date < before:
            # berechne zeitraum
            _after = iteration_date
            _before = (iteration_date + datetime.timedelta(days=1)) - datetime.timedelta(seconds=1)
            # wandle zeitraum in timestamps und int um
            ts_after = int(_after.timestamp())
            ts_before = int(_before.timestamp())
            # zeitraum den restlichen parametern übergeben
            kwargs.update({'after': ts_after, 'before': ts_before, 'limit': limit_per_day})
            #
            data_json = self.request_pushshift_api(base_url=self._base_url, parameters=kwargs)
            utils.cache(PROJECT_ROOT, obj=data_json, caching_token=caching_token)
            
            pbar.update(1)
            iteration_date += datetime.timedelta(days=1)
        pbar.close()
        # 
        list_of_posts = self.get_cached_posts(path=f"{os.path.join(PROJECT_ROOT, '.cache')}/{caching_token}.pkl")
        print('\n')
        logging.info('  ~  collecting completed | Done.')
        return list_of_posts

    @staticmethod
    def request_pushshift_api(base_url, parameters:dict):
        r = requests.get(base_url, params=parameters)
        data_json = r.json()
        return data_json


    @staticmethod
    def get_reddit_data_pushshift(list_of_posts:list):
        """
        Hinweis: Diese Funktion gibt nur die für dieses Projekt notwendigen Daten aus! 
        Es können jedoch noch viele weitere Daten ausgelesen werden. Erweitern Sie die Funktion
        daher eigenständig ODER verwenden Sie die Funktion get_reddit_data_praw()
        """
        logging.warning('  ~  start pushshift data algorithm \n')
        list_of_posts_data = []
        for post in tqdm(list_of_posts):
            _ = {
                'url': f"https://reddit.com{post['permalink']}",
                'date': post['utc_datetime_str'],
                'title': post['title'],
                'selftext': post['selftext'] if post['selftext'] != '' else None
            }
            list_of_posts_data.append(_)
        logging.info('  ~  collecting completed | Done.')
        # 
        df = pd.DataFrame(list_of_posts_data)
        utils.safe_as_pkl(obj=df, filename='reddit_posts_raw_ps', path=os.path.join(PROJECT_ROOT, 'data', 'raw'))
        return df

    @staticmethod
    def get_cached_posts(path):
        cache = utils.load_pkl(path=path)
        list_of_posts = []
        for dataset in cache:
            for post in dataset['data']:
                list_of_posts.append(post)
        return list_of_posts

    @staticmethod
    def get_post_ids(list_of_posts:list):
        list_of_post_ids = []
        for post in list_of_posts:
            list_of_post_ids.append(post['id'])
        return list_of_post_ids



def get_reddit_data_praw(list_of_posts:list):
    # will not work: needs a limiter
    logging.warning('  ~  start praw data algorithm \n')
    list_of_post_ids = MinimalPushshiftAPIWrapper.get_post_ids(list_of_posts)
    try:
        logging.info('  ~  connect to reddit api with credentials...')
        api_praw = praw.Reddit(
            client_id=os.environ.get('REDDIT_CLIENT_ID'),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
            username=os.environ.get('REDDIT_USER'),
            password=os.environ.get('REDDIT_PASS'),
            user_agent=f"{os.environ.get('OS').lower()}:bt-sma-reddit (by u/icarus2612)"
        )
        api_praw.user.me()
        logging.info('  ~  login successful | Done. \n')
    except:
        logging.critical('  ~  login failed')
        # fehlerbehandlung todo
    
    logging.info('  ~  query data from reddit api... \n')
    list_of_posts_data = []
    for id in tqdm(list_of_post_ids):
        post = api_praw.submission(id=id) #api request
        _ = {
            'author': post.author,
            'author_flair_text': post.author_flair_text,
            'comments': post.comments,
            'created_utc': post.created_utc,
            'distinguished': post.distinguished,
            'edited': post.edited,
            'id': post.id,
            'is_original_content': post.is_original_content,
            'link_flair_text': post.link_flair_text,
            'locked': post.locked,
            'name': post.name,
            'num_comments': post.num_comments,
            'over_18': post.over_18,
            'permalink': post.permalink,
            'score': post.score,
            'selftext': post.selftext,
            'spoiler': post.spoiler,
            'stickied': post.stickied,
            'subreddit': post.subreddit,
            'title': post.title,
            'upvote_ratio': post.upvote_ratio,
            'url': post.url
        }
        list_of_posts_data.append(_)
    
    logging.info('  ~  collecting completed | Done.')
    # 
    df = pd.DataFrame(list_of_posts_data)
    utils.safe_as_pkl(obj=df, filename='reddit_posts_raw_v2', path=os.path.join(PROJECT_ROOT, 'data', 'raw'))

    return df



if __name__ == '__main__':
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # setup logging
    logging.basicConfig(
        format='%(levelname)s %(message)s',
        level=logging.INFO
    )

    # setup cli with argparse
    parser = argparse.ArgumentParser(description='', epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('mode', choices=['search', 'praw', 'pushshift'], help='')
    
    # add arguments only for search
    if parser.parse_known_args()[0].mode == 'search':
        parser.add_argument('endpoint', choices=['submission', 'comment'], help='')
        parser.add_argument('after', help='')
        parser.add_argument('before', help='')
        parser.add_argument('parameters', type=str, help='')
        parser.add_argument('--df', choices=['praw', 'pushshift'], help='')
    # add arguments only for praw
    if parser.parse_known_args()[0].mode == 'praw' or parser.parse_known_args()[0].mode == 'pushshift':
        parser.add_argument('path', help='to cache file')
    args = parser.parse_args()

    if args.mode == 'search':
        if args.endpoint == 'submission':
            api_pushshift = MinimalPushshiftAPIWrapper(endpoint='submission')
        if args.endpoint == 'comment':
            api_pushshift = MinimalPushshiftAPIWrapper(endpoint='comment')
        after = datetime.datetime.strptime(args.after, '%Y-%m-%d')
        before = datetime.datetime.strptime(args.before, '%Y-%m-%d')
        _param = eval(args.parameters)
        if args.df == 'praw':
            list_of_posts = api_pushshift.search(after, before, **_param)
            get_reddit_data_praw(list_of_posts)
        elif args.df == 'pushshift':
            list_of_posts = api_pushshift.search(after, before, **_param)
            MinimalPushshiftAPIWrapper.get_reddit_data_pushshift(list_of_posts)
        else:
            api_pushshift.search(after, before, **_param)

    elif args.mode == 'praw':
        list_of_posts = MinimalPushshiftAPIWrapper.get_cached_posts(path=args.path)
        get_reddit_data_praw(list_of_posts)

    elif args.mode == 'pushshift':
        list_of_posts = MinimalPushshiftAPIWrapper.get_cached_posts(path=args.path)
        MinimalPushshiftAPIWrapper.get_reddit_data_pushshift(list_of_posts)

    else:
        raise Exception # this exception should not occur due to 'choices'
    
    # python reddit_scraper.py search submission '2023-1-1' '2023-4-1' "{'subreddit':'technology', 'sort':{'score':'desc'}}"
    # python reddit_scraper.py search submission '2023-1-1' '2023-4-1' "{'subreddit':'technology', 'sort':{'score':'desc'}}" --df praw
    # python reddit_scraper.py search submission '2023-1-1' '2023-4-1' "{'subreddit':'technology', 'sort':{'score':'desc'}}" --df pushshift
    # python reddit_scraper.py praw '.\.cache\reddit_scraper_v2.pkl'
    # python reddit_scraper.py pushshift '.\.cache\reddit_scraper_v2.pkl'