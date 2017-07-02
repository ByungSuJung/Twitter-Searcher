import json
import requests
import csv
import datetime
import logging as log
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib import parse
from bs4 import BeautifulSoup 
from concurrent.futures import ThreadPoolExecutor
from time import sleep


__author__ = 'Eugene Oh'

class SearchRange (object):

    def __init__ (self, rate_delay, error_delay=5):
        self.rate_delay = rate_delay
        self.error_delay = error_delay
        self.counter = 0

    def search (self, since, until, query):
        
        url = self.getURL(since, until, query)
        response = self.getResponse(url)

        tweets = self.parse(response)

        self.save_tweets(tweets)

    def getResponse(self, url):
        pause = 0.5
        driver = webdriver.Chrome(executable_path=r"..\..\Windows\webdrivers\chromedriver.exe")
        driver.get(url)
        
        lastHeight = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(pause)
            newHeight = driver.execute_script("return document.body.scrollHeight")
            if newHeight == lastHeight:
                break
            lastHeight = newHeight
        
        page_source = driver.page_source

        return page_source


    def getURL (self, since, until, query):
        params = {
            'f':'tweets',
            'q':query + ' since:' + str(since)[:10] + ' until:' + str(until)[:10]
        }
        
        url_tupple = ('https', 'twitter.com', '/search', '', parse.urlencode(params), '')
        return parse.urlunparse(url_tupple)

    @staticmethod
    def parse(items_html):
        soup = BeautifulSoup (items_html, "html.parser")
        tweets = []

        for li in soup.find_all("li", class_='js-stream-item'):
            if 'data-item-id' not in li.attrs:
                continue
            
            tweet = {
                'tweet_id' : li['data-item-id'],
                'created_at' : None,
                'user_id': None,
                'user_name' : None,
                'text' : None,
                'num_word' : None,
                'link' : None,
                'image' : None,
                'num_replies' : None,
                'num_retweets' : None,
                'num_favorites' : None
            }

            # Tweet text and number of words
            text_p = li.find("p", class_="tweet-text")
            if text_p is not None:
                tweet['text'] = text_p.get_text()
                tweet['num_word'] = len(tweet['text'].split())

            # Tweet UserID and Username
            user_details = li.find("div", class_= "tweet")
            if user_details is not None:
                tweet['user_id'] = user_details['data-user-id']
                tweet['user_name'] = user_details['data-name']

            # Tweet date
            date = li.find("span", class_="_timestamp")
            if date is not None:
                tweet['created_at'] = float(date['data-time-ms'])

            # Tweet Retweets
            retweets = li.select("span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount")
            if retweets is not None and len(retweets) > 0:
                tweet['num_retweets'] = int(retweets[0]['data-tweet-stat-count'])

            # Tweet Favorites
            favorites = li.select("span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount")
            if favorites is not None and len(favorites) > 0:
                tweet['num_favorites'] = int(favorites[0]['data-tweet-stat-count'])

            # Tweet Replies
            replies = li.select("span.ProfileTweet-action--reply > span.ProfileTweet-actionCount")
            if replies is not None and len(replies) > 0:
                tweet['num_replies'] = int(replies[0]['data-tweet-stat-count'])

            # Check if there is a link
            link = li.find("div", class_="js-macaw-cards-iframe-container")
            if link is not None:
                tweet['link'] = 1
            else:
                tweet['link'] = 0

            # Check if there is an image
            image = li.find("div", class_="js-adaptive-photo")
            if image is not None:
                tweet['image'] = 1
            else:
                tweet['image'] = 0
            
            tweets.append(tweet)

        return tweets
    
    def save_tweets(self, tweets):

        for tweet in tweets:
            # Lets add a counter so we only collect a max number of tweets
            self.counter += 1

            if tweet['created_at'] is not None:
               t = datetime.datetime.fromtimestamp((tweet['created_at']/1000))
               fmt = "%Y-%m-%d %H:%M:%S"
               log.info("%i [%s] - %s - %i - %i - %i - %i - %i" % (self.counter, t.strftime(fmt), tweet['text'], tweet['num_replies'], tweet['num_favorites'],tweet['link'], tweet['image'], tweet['num_word']))



if __name__ == '__main__':
    log.basicConfig(level=log.INFO)

    search_query = "from:23andMe"
    rate_delay_seconds = 0
    error_delay_seconds = 5

    # Example of using TwitterSearch
    twit = SearchRange(rate_delay_seconds, error_delay_seconds)

    select_tweets_since = datetime.datetime.strptime("2017-06-01", '%Y-%m-%d')
    select_tweets_until = datetime.datetime.strptime("2017-07-01", '%Y-%m-%d')
 
    twit.search(select_tweets_since, select_tweets_until, search_query)

    print("SearchRange collected %i" % twit.counter)

