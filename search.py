import json
import requests
import csv
import datetime
import logging as log
import threading
import time
import os.path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from urllib import parse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from time import sleep


__author__ = 'Eugene Oh'

class SearchRange (object):
    def __init__ (self, error_delay=5):
        self.error_delay = error_delay

    def searchRange (self, since, until, query):

        url = self.getURL(since, until, query)
        response = self.getResponse(url)

        tweets = self.parse(response)
        self.save_tweets(tweets)

    def getResponse(self, url):
        pause = 0.5
        driver = webdriver.Chrome()
        driver.get(url)
        height = driver.execute_script("return document.body.scrollHeight;")
        count = 0

        check = driver.find_element_by_class_name("back-to-top").is_displayed()
        while check is not True and count < 1:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(pause)
            if driver.find_element_by_class_name("stream-fail-container").is_displayed():
                driver.find_element_by_class_name("try-again-after-whale").click()
                sleep(pause)
            check = driver.find_element_by_class_name("back-to-top").is_displayed()

            newheight = driver.execute_script("return document.body.scrollHeight;")
            if height == newheight:
                count += 1
                sleep(23)

        page_source = driver.page_source
        driver.close()
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
                'user_id': None,
                'tweet_id' : li['data-item-id'],
                'created_at' : None,
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
                time = float(date['data-time-ms'])
                t = datetime.datetime.fromtimestamp((time/1000))
                fmt = "%Y-%m-%d %H:%M:%S"
                tweet['created_at'] = t.strftime(fmt)

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
            # Print out tweets
            if tweet['created_at'] is not None:
                log.info("%i [%s] - %s" % (self.counter, str(tweet['created_at']), tweet['text']))

class TwitterSearch (SearchRange):
    # Constructor takes rate_delay_seconds and error_delay_seconds and until and threads
    def __init__ (self, error_delay_seconds, since, until, threads):

        #Initialize Variables
        super(TwitterSearch, self).__init__(error_delay_seconds)
        self.since = since
        self.until = until
        self.threads = threads
        self.lock = threading.Lock()

    def search(self, query):
        n_days = (self.until-self.since).days
        tp = ThreadPoolExecutor(max_workers=self.threads)
        print (n_days)
        for i in range (0, n_days, 120):
            since_range = self.since + datetime.timedelta(days=i)
            until_range = self.since + datetime.timedelta(days=(i+140))
            if until_range > self.until:
                until_range = self.until

            tp.submit(self.searchRange, since_range, until_range, query)

        tp.shutdown(wait = True)

    def save_tweets(self, tweets):
        with self.lock:
            file_exists = os.path.isfile("tweets.csv")
            with open ('tweets.csv', 'a') as f:
                w = csv.DictWriter(f, fieldnames = tweets[0].keys())
                if not file_exists:
                    w.writeheader()
                for tweet in tweets:
                    w.writerow(tweet)

if __name__ == '__main__':
    #log.basicConfig(level=log.INFO)
    start = time.time()
    error_delay_seconds = 5
    max_threads = 10

    with open ('userInfo.txt', 'r') as fl:
        query = fl.readline()
        while query:
            search_query = "from:" + query
            since = fl.readline()
            until = fl.readline()
            select_tweets_since = datetime.datetime.strptime(since.strip(), '%Y-%m-%d')
            select_tweets_until = datetime.datetime.strptime(until.strip(), '%Y-%m-%d')

            twit = TwitterSearch(error_delay_seconds, select_tweets_since, select_tweets_until, max_threads)
            twit.search(search_query)
            query = fl.readline()

    end = time.time()
    ttime = end-start
    print("time ellapsed %i" % (int(ttime)))
