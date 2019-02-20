from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd


def init_browser():
    #Windows
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)



def data_scrape(url, browser):
    # browser = init_browser()
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    # browser.quit()
    return soup

# article_listings = data_scrape("https://mars.nasa.gov/news/")
# mars_photo_scrap = data_scrape("https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars")
# mars_weather = data_scrape("https://twitter.com/marswxreport?lang=en")
# mars_facts = data_scrape("https://space-facts.com/mars/")
# mars_hires = data_scrape("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
# mars_hires2 = data_scrape("https://astrogeology.usgs.gov/maps/mars-viking-hemisphere-point-perspectives")

def scrape():
    result_dict = {}
    browser = init_browser()

    # Article listings
    article_listings = data_scrape("https://mars.nasa.gov/news/", browser)

    titles = article_listings.find_all('div', class_='list_text')
    subtitle = article_listings.find_all('div', class_='article_teaser_body')

    article_range = range(len(titles))

    title_list = []
    teaser_list = []

    for article in article_range:
        title_list.append(titles[article].a.text)
        teaser_list.append(subtitle[article].text)

        
    first_article_title = title_list[0]
    first_article_teaser = teaser_list[0]

    articles = {'title': first_article_title, 'teaser': first_article_teaser}
    result_dict['articles'] = articles

    # Mars photo link

    base_url = "https://www.jpl.nasa.gov"
    search_value = "/spaceimages/?search=&category=Mars"
    url = base_url + search_value

    mars_photo_scrap = data_scrape(url,browser)

    main_photo_section = mars_photo_scrap.find_all('a', class_='button', id='full_image')


    photo_link = base_url + main_photo_section[0].attrs['data-fancybox-href']
    large_photo_link = photo_link.replace('medium','large')
    large_photo_link = large_photo_link.replace('ip','hires')

    result_dict['main photo'] = large_photo_link

    # Mars twitter scrape
    mars_weather = data_scrape("https://twitter.com/marswxreport?lang=en", browser)

    mars_weather_text = mars_weather.find_all('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')

    tweet_range = range(len(mars_weather_text))

    # we only want the most recent weather data so break from loop as soon as the first tweet that has the text starting with 
    # Sol is found
    for tweet in tweet_range:
        if mars_weather_text[tweet].text[:7] == 'InSight':
            weather_string = mars_weather_text[tweet].text
            break

    t = weather_string.find("\n")
    if t > 0:
        weather_string = weather_string[:t]

    result_dict['weather'] = weather_string

    # Mars facts

    mars_facts = data_scrape("https://space-facts.com/mars/", browser)

    mars_facts_title_soup = mars_facts.find_all('td', class_='column-1')
    mars_facts_value_soup = mars_facts.find_all('td', class_='column-2')

    table_range = range(len(mars_facts_title_soup))

    mars_facts_titles = []
    mars_facts_values = []
    for row in table_range:
        mars_facts_titles.append(mars_facts_title_soup[row].text)
        mars_facts_values.append(mars_facts_value_soup[row].text)

    mars_facts_table = pd.DataFrame({"Title": mars_facts_titles,
                                "Value": mars_facts_values})

    mars_facts_table.to_html('templates\mars_facts.html', index=False, justify='center')

    with open('templates\mars_facts.html', 'r') as f:
        table_html = f.read()
    
    result_dict['facts'] = table_html

    # Mars Hemisphere Hi-res pictures

    base_url = "https://astrogeology.usgs.gov"

    mars_hires2 = data_scrape("https://astrogeology.usgs.gov/maps/mars-viking-hemisphere-point-perspectives",browser)

    mars_hires2_soup = mars_hires2.find_all('a', class_="item")

    pict_range = range(len(mars_hires2_soup))

    pict_list = []
    for pict in pict_range:
        # check to see if the href ends in _enhanced
        if mars_hires2_soup[pict].attrs['href'][-9:] == '_enhanced':
            # if it does scrape the new url for image links
            pict_html = data_scrape(base_url + mars_hires2_soup[pict].attrs['href'],browser)
            pict_soup = pict_html.find_all('div', class_='downloads')

            # add a dictionary containing the image title, the hi-res photo link and a thumb image link
            # the thumb image link is added so my site will still be able to display an image even if the hi-res is down
            pict_list.append({'title': mars_hires2_soup[pict].h3.text[:-9], 'img_url': pict_soup[0].a.attrs['href'], 'tmb_url':\
                            base_url + pict_soup[0].img.attrs['src']})

    result_dict['hi-res'] = pict_list
    browser.quit()

    return result_dict
