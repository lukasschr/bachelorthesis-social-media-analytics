import snscrape.modules.twitter as sntwitter

def search_similar_hashtags(hashtags:list, limit:int=100):
    """Search for similar hashtags.
    
    Searches for hashtags that users frequently use in connection with the passed hashtags.

    Args:
        hastags: list of predefined hashtags. this must be specified in order to find other similar 
            ones.
        limit: number of twitter posts to be searched for similar hashtags.

    Returns:
        List of all found hashtags
    """
    query = '('
    last_element = hashtags.pop()
    for hashtag in hashtags:
        query = query+f'{str(hashtag)}, OR '
    query = query+f'{str(last_element)})'

    list_of_hashtags = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= limit:
            break
        else:
            for hashtag in tweet.hashtags:
                list_of_hashtags.append(hashtag)
    return list_of_hashtags