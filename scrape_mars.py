from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd


def init_browser():
    #Windows
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)



def data_scrape(url):
    browser = init_browser()
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    
    return soup

article_listings = data_scrape("https://mars.nasa.gov/news/")
mars_photo_scrap = data_scrape("https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars")
mars_weather = data_scrape("https://twitter.com/marswxreport?lang=en")
mars_facts = data_scrape("https://space-facts.com/mars/")
# mars_hires = data_scrape("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
mars_hires2 = data_scrape("https://astrogeology.usgs.gov/maps/mars-viking-hemisphere-point-perspectives")

