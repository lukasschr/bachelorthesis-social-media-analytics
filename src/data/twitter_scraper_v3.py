from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import datetime
from src import utils
import os


def query(q:str, since:datetime.datetime, until:datetime.datetime, limit:int):
    since = str(since.date())
    until = str(until.date())

    _base_url = f'https://nitter.net/search?f=tweets&q={q}&since={since}&until={until}&near='
    
    driver = webdriver.Chrome()
    driver.get(_base_url)

    collected_posts = 0
    while collected_posts <= limit:
        time.sleep(1)
        div_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="show-more"]')))
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        tweet_containers = soup.find_all("div", class_="timeline-item")
        tweets = []
        for tweet in tweet_containers:
            # try:
            #     tweet_link = tweet.find("a", class_="tweet-link")["href"]
            # except:
            #     tweet_link = None
            # try:
            #     tweet_date = tweet.find("span", class_="tweet-date").find("a")["title"]
            # except:
            #     tweet_date = None
            # try:
            #     tweet_content = tweet.find("div", class_="tweet-content").text.strip()
            # except:
            #     tweet_content = None
            try:
                tweet_link = f"https://twitter.com{tweet.find('a', class_='tweet-link')['href']}"
                tweet_date = tweet.find('span', class_='tweet-date').find('a')['title']
                tweet_content = tweet.find('div', class_='tweet-content').text.strip()
                _ = {
                    'url': tweet_link,
                    'date': tweet_date,
                    'rawContent': tweet_content
                }
                tweets.append(_)
            except:
                pass

        for t in tweets:
            utils.cache(PROJECT_ROOT, obj=t, caching_token='twitter_scraper_v3')
        
        collected_posts += len(tweets)
        del tweets
        print(f'{collected_posts} / {limit}')
        
        div_element.click()

    driver.quit()
                 



PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GOAL = 100_000

after = datetime.datetime(2023, 1, 1)
before = datetime.datetime(2023, 3, 31)

posts_to_be_collected_per_day = GOAL // ((before - after).days)


iteration_date = after
while iteration_date < before:
    print(f'{iteration_date} - {iteration_date + datetime.timedelta(days=1)}')
    query(q="%28%23technology+OR+%23tech+OR+%23innovation%29+lang%3Aen&e-nativeretweets=on", 
          since=iteration_date, 
          until=iteration_date + datetime.timedelta(days=1), 
          limit=posts_to_be_collected_per_day)
    iteration_date += datetime.timedelta(days=1)