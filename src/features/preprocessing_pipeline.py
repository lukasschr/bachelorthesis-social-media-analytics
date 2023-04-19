import logging
import argparse
import os

import pandas as pd
import contractions
import nltk
import string
import emoji
import re

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# download required nltk packages
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def tokenize(dataframe, c):
    """Converts text/strings to tokens.

    Converts any text in any column of a dataframe to 1-gram tokens.

    Args:
        dataframe: pandas Dataframe (best in INTERMEDIATE state)
        c: column in dataframe to apply the function to
    
    Returns:
        updated dataframe and column name to which function was applied
    """
    tokenize = nltk.tokenize.word_tokenize
    if c == '':
        dataframe[f'{c}_tokenized'] = dataframe['rawContent'].apply(tokenize)
    else:
        dataframe[f'{c}_tokenized'] = dataframe[c].apply(tokenize)
    try:
        del df[c]
    except KeyError:
        pass
    return dataframe, f'{c}_tokenized'

def lowercase(dataframe, c):
    """Lowercase each token.

    Lowercase the tokens for each token list in the dataframe.
    WARNING: tokenization must have been carried out beforehand!

    Args:
        dataframe: pandas Dataframe (best in INTERMEDIATE state)
        c: column in dataframe to apply the function to
    
    Returns:
        updated dataframe and column name to which function was applied
    """
    def _lowercase(tokens):
        return [token.lower() for token in tokens]
    dataframe[f'{c}_lowercase'] = dataframe[c].apply(_lowercase)
    del df[c]
    return dataframe, f'{c}_lowercase'

def remove_punct(dataframe, c):
    """Removes puncture.

    Removes puncture for each token list in the dataframe.
    WARNING: tokenization must have been carried out beforehand!

    Args:
        dataframe: pandas Dataframe (best in INTERMEDIATE state)
        c: column in dataframe to apply the function to
    
    Returns:
        updated dataframe and column name to which function was applied
    """
    punct = string.punctuation + "’" + "``" +"`" + "''" +"'"
    def _remove_punct(tokens):
        return [token for token in tokens if token not in punct]
    dataframe[f'{c}_nonpunctation'] = dataframe[c].apply(_remove_punct)
    del df[c]
    return dataframe, f'{c}_nonpunctation'

def fix_contractions(dataframe, c):
    """Converts English short forms to long forms.

    Converts English short forms to long forms for any text in the dataframe.

    Args:
        dataframe: pandas Dataframe (best in INTERMEDIATE state)
        c: column in dataframe to apply the function to
    
    Returns:
        updated dataframe and column name to which function was applied
    """
    def _fix_contractions(text):
        return contractions.fix(text)
    if c == '':
        dataframe[f'{c}_fixedcontractions'] = dataframe['rawContent'].apply(_fix_contractions)
    else:
        dataframe[f'{c}_fixedcontractions'] = dataframe[c].apply(_fix_contractions)
    try:
        del df[c]
    except KeyError:
        pass
    return dataframe, f'{c}_fixedcontractions'

def remove_stopwords(dataframe, c):
    """Removes stopwords.

    Removes stopwords for each token list in the dataframe.
    WARNING: tokenization must have been carried out beforehand!

    Args:
        dataframe: pandas Dataframe (best in INTERMEDIATE state)
        c: column in dataframe to apply the function to
    
    Returns:
        updated dataframe and column name to which function was applied
    """
    stop_words = stopwords.words('english')
    def _remove_stopwords(tokens):
        return [token for token in tokens if token not in stop_words]
    dataframe[f'{c}_nonstopwords'] = dataframe[c].apply(_remove_stopwords)
    del df[c]
    return dataframe, f'{c}_nonstopwords'

def remove_url(dataframe, c):
    """Removes URLs.

    Removes URLs for any text in the dataframe.

    Args:
        dataframe: pandas Dataframe (best in INTERMEDIATE state)
        c: column in dataframe to apply the function to
    
    Returns:
        updated dataframe and column name to which function was applied
    """
    def _remove_url(text):
        return re.sub(r'http\S+', '', text)
    if c == '':
        dataframe[f'{c}_nonurl'] = dataframe['rawContent'].apply(_remove_url)
    else:
        dataframe[f'{c}_nonurl'] = dataframe[c].apply(_remove_url)
    try:
        del df[c]
    except KeyError:
        pass
    return dataframe, f'{c}_nonurl'

def remove_emoji(dataframe, c):
    """Removes emojis

    Removes emojis for each token list in the dataframe.
    WARNING: tokenization must have been carried out beforehand!

    Args:
        dataframe: pandas Dataframe (best in INTERMEDIATE state)
        c: column in dataframe to apply the function to
    
    Returns:
        updated dataframe and column name to which function was applied
    """
    def _remove_emoji(tokens):
        return [token for token in tokens if not any(char in emoji.EMOJI_DATA for char in token)]
    dataframe[f'{c}_nonemoji'] = dataframe[c].apply(_remove_emoji)
    del df[c]
    return dataframe, f'{c}_nonemoji'
    
def lemmatize(dataframe, c):
    """Performs a lemmatization.

    Lemmatization of all token lists in the dataframe.
    WARNING: tokenization must have been carried out beforehand!

    Args:
        dataframe: pandas Dataframe (best in INTERMEDIATE state)
        c: column in dataframe to apply the function to
    
    Returns:
        updated dataframe and column name to which function was applied
    """
    lemmatizer = WordNetLemmatizer()
    def _lemmatize(tokens):
        return [lemmatizer.lemmatize(token) for token in tokens]
    dataframe[f'{c}_lemmatized'] = dataframe[c].apply(_lemmatize)
    del df[c]
    return dataframe, f'{c}_lemmatized'


if __name__ == '__main__':
    # setup logging
    logging.basicConfig(
        format='%(levelname)s %(message)s',
        level=logging.INFO
    )

    # setup cli with argparse
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    parser = argparse.ArgumentParser(description='Pre-processes text data', 
                                    epilog='Made with <3 by Lukas Schroeder')    
    parser.add_argument('path', help='Path to a .FEATHER file')
    parser.add_argument('--remove_url', help='removes URLs', action='store_true')
    parser.add_argument('--fix_contractions', help='converts English short forms to long forms', 
                        action='store_true')
    parser.add_argument('--lowercase', help='lowercase each token', action='store_true')
    parser.add_argument('--remove_punct', help='removes puncture', action='store_true')
    parser.add_argument('--remove_stopwords', help='removes stopwords', action='store_true')
    parser.add_argument('--remove_emoji', help='removes emojis', action='store_true')
    parser.add_argument('--lemmatize', help='performs a lemmatization', action='store_true')
    args = parser.parse_args()

    # load raw dataframe
    logging.info('Load dataset...')
    df = pd.read_feather(path=args.path)

    # run preprocessing pipeline
    logging.warning('Run preprocessing pipeline:')
    c = ''
    if args.remove_url:
        logging.info('  ~  remove urls...')
        df, c = remove_url(dataframe=df, c=c)
    if args.fix_contractions:
        logging.info('  ~  fix contractions...')
        df, c = fix_contractions(dataframe=df, c=c)
    logging.info('  ~  tokenize...')
    df, c = tokenize(dataframe=df, c=c)
    if args.lowercase:
        logging.info('  ~  lowercase...')
        df, c = lowercase(dataframe=df, c=c)
    if args.remove_punct:
        logging.info('  ~  remove puncture...')
        df, c = remove_punct(dataframe=df, c=c)
    if args.remove_stopwords:
        logging.info('  ~  remove stopwords...')
        df, c = remove_stopwords(dataframe=df, c=c)
    if args.remove_emoji:
        logging.info('  ~  remove emojis...')
        df, c = remove_emoji(dataframe=df, c=c)
    if args.lemmatize:
        logging.info('  ~  lemmatize...')
        df, c = lemmatize(dataframe=df, c=c)
    df = df.rename(columns={c: 'preprocessed_text'})
    logging.info('Preprocessing pipeline executed successfully!')

    # export results
    logging.warning('Export results...')
    df.to_feather(f"{os.path.join(PROJECT_ROOT, 'data', 'processed')}/twitter_tweets_processed.feather")
    df.to_csv(f"{os.path.join(PROJECT_ROOT, 'data', 'processed')}/twitter_tweets_processed.csv", index=False)
    logging.info('Done.')