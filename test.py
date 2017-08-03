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


driver = webdriver.Chrome()
driver.get("https://twitter.com/search?f=tweets&q=from%3Ae_oh12+since%3A2015-10-01+until%3A2016-01-09")
height = driver.execute_script("return document.body.scrollHeight;")
count = 0
driver.implicitly_wait(1)
c = driver.find_element_by_css_selector(".stream-fail-container").is_displayed()
check = len(driver.find_elements_by_css_selector(".back-to-top"))
print (check)
print (len(driver.find_elements_by_css_selector(".SearchEmptyTimeline-emptyDescription")))
driver.implicitly_wait(0)