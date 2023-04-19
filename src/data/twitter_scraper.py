from datetime import datetime
import argparse
import os

from src import utils
from tqdm import tqdm
import snscrape.modules.twitter as sntwitter
import pandas as pd


class IncorrectNumberOfPostsCollected(Exception):
    """Raises if either too many posts have been collected or posts are missing."""


def get_twitter_posts(query:str, limit:int=500_000):
    """Collects Twitter posts.

    Searches for Twitter posts according to the query passed and saves them.

    Args:
        query: search parameters for the scraper
        limit: number of twitter posts to be searched

    Returns:
        List of all found posts
    """
    caching_token = f'_{get_twitter_posts.__name__}_{str(int(datetime.now().timestamp()))}'
    _list_of_tweets = []
    for i, tweet in tqdm(enumerate(sntwitter.TwitterSearchScraper(query).get_items()), total=limit):
        if i > limit:
            break
        else:
            _ = {
                'url': tweet.url,
                'date': tweet.date,
                'rawContent': tweet.rawContent,
                'renderedContent': tweet.renderedContent,
                'id': tweet.id,
                'user': tweet.user,
                'replyCount': tweet.replyCount,
                'retweetCount': tweet.retweetCount,
                'likeCount': tweet.likeCount,
                'quoteCount': tweet.quoteCount,
                'conversationId': tweet.conversationId,
                'lang': tweet.lang,
                'source': tweet.source,
                'sourceUrl': tweet.sourceUrl,
                'sourceLabel': tweet.sourceLabel,
                'links': tweet.links,
                'media': tweet.media,
                'retweetedTweet': tweet.retweetedTweet,
                'quotedTweet': tweet.quotedTweet,
                'inReplyToTweetId': tweet.inReplyToTweetId,
                'inReplyToUser': tweet.inReplyToUser,
                'mentionedUsers': tweet.mentionedUsers,
                'coordinates': tweet.coordinates,
                'place': tweet.place,
                'hashtags': tweet.hashtags,
                'cashtags': tweet.cashtags,
                'card': tweet.card,
                'viewCount': tweet.viewCount,
                'vibe': tweet.vibe
            }
            _list_of_tweets.append(_)
            # posts that have already been collected are regularly cached
            if (i+1)%(limit/10)==0:
                utils.cache(obj=_list_of_tweets, caching_token=caching_token)
                # the list is deleted and recreated to save memory
                del _list_of_tweets
                _list_of_tweets = []
    
    # load cached posts to merge them
    cache = utils.load_pkl(f'../.cache/{caching_token}.pkl')
    
    number_of_tweets = 0
    for cached_list_of_tweets in cache:
        number_of_tweets += len(cached_list_of_tweets)
    
    if number_of_tweets == limit:
        list_of_tweets = []
        for cached_list_of_tweets in cache:
            for tweet in cached_list_of_tweets:
                list_of_tweets.append(tweet)
        os.remove(f'../.cache/{caching_token}.pkl')
    else:
        raise IncorrectNumberOfPostsCollected
    
    # transform posts into a dataframe
    df = pd.DataFrame(list_of_tweets)

    # export dataframe
    utils.safe_as_pkl(obj=df, filename='twitter_tweets_raw', path=os.path.join(PROJECT_ROOT, 'data', 'raw'))
    df.to_csv(f"{os.path.join(PROJECT_ROOT, 'data', 'raw')}/twitter_tweets_raw.csv", index=False)

    return df


if __name__ == '__main__':
    # setup cli with argparse
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    parser = argparse.ArgumentParser(description='Collects Twitter posts for the given quary.', 
                                    epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('query')
    parser.add_argument('-l', '--limit', help='number of tweets to collect')
    parser.add_argument('-s', '--shutdown', help='shuts down the system after successful execution',
                        action='store_true')
    args = parser.parse_args()

    if args.limit:
        get_twitter_posts(query=args.query, limit=int(args.limit))
        if args.shutdown:
            utils.send_notification()
            utils.shutdown()
    else:
        get_twitter_posts(query=args.query)
        if args.shutdown:
            utils.send_notification()
            utils.shutdown()