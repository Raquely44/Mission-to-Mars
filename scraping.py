# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

# Path to chromedriver
#!which chromedriver

def scrape_all():
   # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

   # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "Mars_hemispheres": mars_hemisphere(browser)
    } 

    #stop webdriver and return data
    browser.quit()
    return data   

# Set the executable path and initialize the chrome browser in splinter
#executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
#browser = Browser('chrome', **executable_path)

def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page and look at pages with ul item list and li slide objects
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #Add try/except for error handling
    try:
        # read from right to left. li is read first then all items nested in it.
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # within the varibale we created, find title from <div class="content_title">
        #slide_elem.find("div", class_='content_title')


        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # when .gettext() is with .find() we will get the text in the html result
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p

# ## JPL Space Images Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    # Add try/except for error handeling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
   
    return img_url

# ## Mars Facts
def mars_facts():
    try:
        # makes first table into dataframe. .read_html can only read tables
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    df.columns=['Description', 'Value']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

# ## Mars Hemisphere Information
def mars_hemisphere(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    
    html = browser.html
    names_soup = soup(html, 'html.parser')

    # 2. Create a list to hold the images and titles.
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    hemisphere_image_urls = []
    
    names = names_soup.find_all('h3')

    for name in names:
        hemisphere_name = name.text
        
        element = browser.is_element_present_by_text(hemisphere_name, wait_time=2)
        if element == True:
            element_link = browser.links.find_by_partial_text(hemisphere_name)
            element_link.click()
            
            html = browser.html
            img_soup = soup(html, 'html.parser')
            
            img_url = img_soup.select_one("ul li a").get("href")
            
            hemispheres = {'img_url': img_url, 'title': hemisphere_name}
            
            hemisphere_image_urls.append(hemispheres)
            
        #Go back to original page
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)
    return hemisphere_image_urls
    
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())