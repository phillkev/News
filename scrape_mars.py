from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd


def init_browser():
    #Windows
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)


# Originally I declared my browser in the data_scrape() function however I found opening so many chromedrivers was hard on my laptop, even with the quit
# statement forcing the browser to close.  I also found that reusing the same browser and just passing new page links to speed up my runtime due to the amount of time 
# it took to initialize the chromedriver.

def data_scrape(url, browser):
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    return soup


def scrape():
    result_dict = {}

    browser = init_browser()

# Scape the Article listings
    article_listings = data_scrape("https://mars.nasa.gov/news/", browser)

    titles = article_listings.find_all('div', class_='list_text')
    subtitle = article_listings.find_all('div', class_='article_teaser_body')

    article_range = range(len(titles))

    title_list = []
    teaser_list = []

    # While the assignmentt only wanted us to pull the first article I wanted to collect all the articles just in case they might be useful 
    for article in article_range:
        title_list.append(titles[article].a.text)
        teaser_list.append(subtitle[article].text)

    # Here I grab just the first article and teaser    
    first_article_title = title_list[0]
    first_article_teaser = teaser_list[0]

    # create a dictionary and then add it to my results dictionary that will be inserted into the MongoDB
    articles = {'title': first_article_title, 'teaser': first_article_teaser}
    result_dict['articles'] = articles

# Mars photo link

    # The site returned a partial link so I needed to create a base url variable to add it to the scraped url link
    # I also used this to create my url for the search.  This wouls also allow me to utilize the link in future searches
    base_url = "https://www.jpl.nasa.gov"
    search_value = "/spaceimages/?search=&category=Mars"
    url = base_url + search_value

    mars_photo_scrap = data_scrape(url,browser)

    main_photo_section = mars_photo_scrap.find_all('a', class_='button', id='full_image')

    # I found I could use the scraped value and perform some replaces to return the desired link.
    photo_link = base_url + main_photo_section[0].attrs['data-fancybox-href']
    large_photo_link = photo_link.replace('medium','large')
    large_photo_link = large_photo_link.replace('ip','hires')

    # Add the photo to the resulting dictionary with a key value of 'main photo'
    result_dict['main photo'] = large_photo_link

# Mars twitter scrape

    # The weather string was difficult to get consistently.  On 2/14 NASA changed their data source used to report the weather.
    # This change forced me to change my scrape to ensure I was still capturinng the most recent scrape from the weather feed.
    mars_weather = data_scrape("https://twitter.com/marswxreport?lang=en", browser)

    mars_weather_text = mars_weather.find_all('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')

    tweet_range = range(len(mars_weather_text))

    # we only want the most recent weather data so break from loop as soon as the first tweet that has the text identified as
    # storinng the weatherr data.  Until 2/13 the string that started with the word Sol was used as the search criteria.  2/14 and 
    # later started using a new technology called InSight to feed twitter with the weather data.
    # This changed the search criteria so I would look for InSight instetad of Sol
    for tweet in tweet_range:
        if mars_weather_text[tweet].text[:7] == 'InSight':
            weather_string = mars_weather_text[tweet].text
            break

    # On 2/17 the weather feed had additional information.  I decided to remove all information after a \n if one was found
    t = weather_string.find("\n")
    if t > 0:
        weather_string = weather_string[:t]

    
    # Add the weather string to the result_dict with key 'weather'
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

    # I was not sure the best way to handle getting the HTML into a Dictionary so it could be loaded into the mongo DB
    # I ended up taking my Data Frame - converting it to an HTML file.  Read the HTML file into a string and then adding
    # it to my dictionary.  This is actually the part of the assignment I found most interesting.  When I was working on 
    # the last homework assignment I wanted a solution that would allow me to pass my navigation and footer  HTML into my
    # pages as variable so I could manage these shared components in one location.  This trick would allow me to do this.
    mars_facts_table.to_html('templates\mars_facts.html', index=False, justify='center')

    with open('templates\mars_facts.html', 'r') as f:
        table_html = f.read()
    
    # Add the weather string to the result_dict with key 'weather'
    result_dict['facts'] = table_html

# Mars Hemisphere Hi-res pictures

    # This section was a challenge.  The website was down.  I also hit the issue where the returned HTML link was incomplete
    # So I used the base_url solution developed above.
    base_url = "https://astrogeology.usgs.gov"

    # The reason for the name mars_hires2 is the original link provided by the readme was down.  I googled and found I was able
    # to get the photo links from a different page in the same site.
    mars_hires2 = data_scrape("https://astrogeology.usgs.gov/maps/mars-viking-hemisphere-point-perspectives",browser)

    mars_hires2_soup = mars_hires2.find_all('a', class_="item")

    pict_range = range(len(mars_hires2_soup))

    pict_list = []
    for pict in pict_range:
        # This site had multiple links for the same hemisphere.  I needed the links to the ones flagged as _enhanced.
        if mars_hires2_soup[pict].attrs['href'][-9:] == '_enhanced':
            # if it does scrape the new url for image links
            pict_html = data_scrape(base_url + mars_hires2_soup[pict].attrs['href'],browser)
            pict_soup = pict_html.find_all('div', class_='downloads')

            # add a dictionary containing the image title, the hi-res photo link and a thumb image link
            # I also captured the thumb image link.  I was planning on using the thumb image if the links to the larger image
            # failed to load.  I did not end up coding for this failure based on the time available for the assignment 
            pict_list.append({'title': mars_hires2_soup[pict].h3.text[:-9], 'img_url': pict_soup[0].a.attrs['href'], 'tmb_url':\
                            base_url + pict_soup[0].img.attrs['src']})

    # Added the hi-res photo link list to the result dictionary under the key 'hi-res'
    result_dict['hi-res'] = pict_list

    # the scrape is complete so we close the browser.  If this is not done it can lead to memory leaks.  I found some very odd
    # behavior when I did not hahve this in my code.  The most interesting is I found my copy/paste buffer was not working as
    # expected.
    browser.quit()

    return result_dict
