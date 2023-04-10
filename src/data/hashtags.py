import snscrape.modules.twitter as sntwitter
from tqdm import tqdm
from datetime import date, timedelta

def search_similar_hashtags(hashtags:list, since=date.today()-timedelta(weeks=4), until=date.today(),
                            limit:int=9999):
    """Search for similar hashtags.

    Searches for hashtags that users frequently use in connection with the passed hashtags.

    Args:
        hastags: list of predefined hashtags. this must be specified in order to find other similar 
            ones.
        since: start date for searching similar hashtags (default value: last four weeks)
        until: end date for searching similar hashtags  (default value: last four weeks)
        limit: number of twitter posts to be searched for similar hashtags.

    Returns:
        List of all found hashtags
    """
    query = '('
    last_element = hashtags.pop()
    for hashtag in hashtags:
        query = query+f'{str(hashtag)}, OR '
    query = query+f'{str(last_element)}) '+f'until:{until} since:{since}'

    list_of_hashtags = []
    for i, tweet in tqdm(enumerate(sntwitter.TwitterSearchScraper(query).get_items()), total=limit):
        if i >= limit:
            break
        else:
            for hashtag in tweet.hashtags:
                list_of_hashtags.append(hashtag)
    return list_of_hashtags