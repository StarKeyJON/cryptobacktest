import pandas as pd
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import chromedriver_binary
import string
pd.options.display.float_format = '{:.0f}'.format

is_link = 'https://finance.yahoo.com/u/yahoo-finance/watchlists/crypto-top-market-cap/'

driver = webdriver.Chrome()
driver.get(is_link)
html = driver.execute_script('return document.body.innerHTML;')
soup = BeautifulSoup(html,'lxml')

features = soup.find_all('div', class_='1859.2601')

print(features)