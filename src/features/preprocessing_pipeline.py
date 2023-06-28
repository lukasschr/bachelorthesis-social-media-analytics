import pandas as pd
import contractions
import nltk
import string
import emoji
import re

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import WordPunctTokenizer

from tqdm import tqdm
from src.utils import logger


class PreprocessingPipeline:
    """A superclass for preprocessing pipeline classes.

    Defines important methods and techniques to preprocess text for modeling.

    Attributes:
        dataframe: A pandas dataframe; The text to be processed must be in the 'rawContent' column.
    """
    def __init__(self, dataframe:pd.DataFrame) -> None:
        logger.info('initialize pipeline and download required nltk packages...')
        # download required nltk packages
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        self.__dataframe = dataframe
        self.__dataframe['preprocessed_text'] = self.__dataframe['rawContent'].copy()
        tqdm.pandas()

    def remove_urls(self):
        """Removes URLs from the text."""
        logger.info('remove urls...')
        def _remove_urls(text):
            # define regex pattern for url detection
            url_pattern = re.compile(r'\b(?:https?://)?(?:[a-z]+\.[a-z]+\.[a-z]+|[a-z]+\.[a-z]+(?:/[^\s]*)?)\b')
            # remove url matches from the text
            text_without_urls = re.sub(url_pattern, '', text)
            return text_without_urls
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_remove_urls)

    def remove_mentions(self):
        """Removes mentions of other Twitter users from the text."""
        logger.info('remove twitter user mentions...')
        def _remove_mentions(text):
            # define regex pattern for user mentions
            mention_pattern = re.compile(r'@\w+')
            # remove user mentions from the text
            text_without_mentions = re.sub(mention_pattern, '', text)
            return text_without_mentions
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_remove_mentions)

    def fix_contractions(self):
        """Repairs english language contractions."""
        logger.info('fix contractions...')
        def _fix_contractions(text):
            try:
                return contractions.fix(text)
            except IndexError: # error should not appear
                return text
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_fix_contractions)

    def tokenize_text(self):
        """Performs a tokenization of the texts."""
        logger.info('tokenize text...')
        # define tokenizer function
        tokenizer = WordPunctTokenizer()
        def _tokenize_text(text):
            return tokenizer.tokenize(text)
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_tokenize_text)

    def lowercase(self):
        """Performs a lowercasing of the tokens."""
        logger.info('lowercase tokens...')
        def _lowercase(tokens):
            return [token.lower() for token in tokens]
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_lowercase)

    def remove_punct(self):
        """Removes punctuation within token lists."""
        logger.info('remove punctuation...')
        # adding more characters to the punctuation list
        punct = string.punctuation + "’" + "``" +"`" + "''" +"'" + "•" + "“" + "”" + "…" + "�" + "‘" + "…" + "/…" + "-…" + "-#" + "’" + "..." + ".”" + "!!"
        def _remove_punct(tokens):
            return [token for token in tokens if token not in punct]
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_remove_punct)

    def remove_numerics(self):
        """Removes numeric values within token lists."""
        logger.info('remove numeric values...')
        def _remove_numerics(tokens):
            return [token for token in tokens if not token.isdigit()]
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_remove_numerics)

    def remove_stopwords(self):
        """Removes all stop words within token lists."""
        logger.info('remove stopwords...')
        # define list of stopwords
        stop_words = stopwords.words('english')
        additional_stop_words = ['u']
        stop_words.extend(additional_stop_words)
        def _remove_stopwords(tokens):
            return [token for token in tokens if token not in stop_words and len(token) > 1]
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_remove_stopwords)
    
    def remove_emoji(self):
        """Removes all emojis within the token lists"""
        logger.info('remove emojis...')
        def _remove_emoji(tokens):
            return [token for token in tokens if not any(char in emoji.EMOJI_DATA for char in token)]
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_remove_emoji)

    def lemmatize(self):
        """Performs a lemmatization of the tokens"""
        logger.info('lemmatize tokens...')
        # initialization of the lemmatizer
        lemmatizer = WordNetLemmatizer()
        def _lemmatize(tokens):
            return [lemmatizer.lemmatize(token) for token in tokens]
        self.__dataframe['preprocessed_text'] = self.__dataframe['preprocessed_text'].progress_apply(_lemmatize)
    
    def __get_dataframe(self):
        return self.__dataframe
    
    def __set_dataframe(self, dataframe:pd.DataFrame):
        self.__dataframe = dataframe

    dataframe = property(__get_dataframe, __set_dataframe)


class DefaultPipeline(PreprocessingPipeline):
    """The default preprocessing pipeline.

    Contains the run method, which executes the standard preprocessing pipeline

    Attributes:
        dataframe: A pandas dataframe; The text to be processed must be in the 'rawContent' column.
    """
    def __init__(self, dataframe:pd.DataFrame) -> None:
        super().__init__(dataframe)
    
    def run(self):
        """Runs the preprocessing pipeline.

        Executes the previously specified methods of the pipeline
        
        Returns:
            dataframe: the pandas dataframe, with the 'preprocessed_text' column containing the processed text
        """
        logger.warning('starting default preprocessing pipeline')
        self.remove_urls()
        self.remove_mentions()
        self.fix_contractions()
        self.tokenize_text()
        self.lowercase()
        self.remove_punct()
        self.remove_numerics()
        self.remove_stopwords()
        self.remove_emoji()
        self.lemmatize()
        logger.info('preprocessing completed successfully!')
        return self.dataframe