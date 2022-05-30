import pandas as pd
import datetime as dt
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager


# scrape all
############
def scrape_all():

    # initiate headless driver for deployment 
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    url_title = mars_hemisphere(browser)

    # run all functions and store results in a dictionary
    data = {
        'news_title': news_title,
        'negraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'last_modified': dt.datetime.now(),
        'hemispheres': url_title
    }

    # stop browser
    browser.quit()
    return data


# mars news
###########
def mars_news(browser):
    # visit the mars news site
    url = 'https://redplanetscience.com/'
    # url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)
    # optional delay for loading the page
    browser.is_element_not_present_by_css('div.list_text', wait_time=1)

    # convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # use the parent element to find the first 'a' tag and save it as news_title
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    # return 
    return news_title, news_p


# featured image
################
def featured_image(browser):

    # visit url
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # add try/except for error handling
    try:
        # find the relative img url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # use the base url to create an absolute url
    # img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url


# mars facts
############
def mars_facts():
    try:
        # use read-html to scrape the facts table into a dataframe
        # df = pd.read_html('https://galaxyfacts-mars.com')[0]
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None
    

    # assign columns and set index of dataframe    
    df.columns = ['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # convert df into html format
    return df.to_html(classes="table table-hover table-striped table-borderless")


# mars hemisphere
#################
def mars_hemisphere(browser):
    # visit the Mars Hemispheres url
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    browser.is_element_not_present_by_css('div.list_text', wait_time=1)
    
    hemisphere_image_urls = []

    for i in range(4):
        url_title = {}
        title = browser.find_by_tag('h3')[i].text
        browser.find_by_tag('h3')[i].click()
        html = browser.html
        img_soup = soup(html, 'html.parser')
        results = img_soup.select('ul')
        img_href = results[0].select('li')[0].find('a').get('href')
        url_title['img_url'] = f"{url}{img_href}"
        url_title['title'] = title
        hemisphere_image_urls.append(url_title)
        try:
            browser.links.find_by_partial_text('Back').click()
        except BaseException:
            continue

    # return data
    return hemisphere_image_urls


# main
######
if __name__ == '__main__':
    # if running as script, print scraped data
    print(scrape_all())