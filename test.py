from bs4 import BeautifulSoup
from selenium import webdriver
import time



PATH = 'C:\Program Files (x86)\chromedriver.exe'



target_url = "https://twitter.com/scrapingdog"


driver=webdriver.Chrome(PATH)

driver.get(target_url)
time.sleep(5)



resp = driver.page_source
driver.close()

print(resp)