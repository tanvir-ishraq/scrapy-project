from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import scrapy

#scroll dynamic page using selenium module:
def load_full_page(driver): #module to scroll until all items are loaded
    time.sleep(2)  # Allow 2 seconds for the web page to open
    scroll_pause_time = .7
    screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    i = 1

    while True:
        # scroll one screen height each time
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
        i += 1
        time.sleep(scroll_pause_time)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = driver.execute_script("return document.body.scrollHeight;")  
        # Break the loop when the height we need to scroll to is larger than the total scroll height
        if (screen_height) * i > scroll_height:
            break


#Scrapes address all the subcategories urls
def subcategory_url_extract(driver):
    driver.get("https://www.luluhypermarket.com/en-ae/electronics") #Category address

    #select subcategory elements using corresponding css
    sub_css_class = driver.find_elements(By.CSS_SELECTOR, 'div.col-lg-2.col-md-3.col-auto')

    sub_urls=[]
    for element in sub_css_class:
        #get child element <a>. Then get url(href)
        a = element.find_element(By.TAG_NAME, "a") 
        sub_urls.append( a.get_attribute('href') )
    
    return sub_urls



class TesterSpider(scrapy.Spider):
    name = "procedure"

    #scrape stage 1. scraping subcateogry listings and the URLs
    def start_requests(self):
        driver = webdriver.Chrome(executable_path=r"G:\product_scrap_assesment\chromedriver_win32\chromedriver.exe")

        sub_urls = subcategory_url_extract(driver)

        for url in sub_urls:
        
            driver.get(url) #url must be str type
            load_full_page(driver) #dynamic page. so scroll till all items are load

            css_selector = driver.find_elements(By.CLASS_NAME, "js-gtm-product-link")
            for product_element in css_selector:
                href = product_element.get_attribute('href')
                yield scrapy.Request(href)

        driver.quit()

    
    #scrape stage 2. scrape individual products information. run command: scrapy crawl tester -o yourFile.json
    def parse(self, response):

        #summary processing:
        Product_Summary={}
        #list containing every points from Product summary:
        summray_points = response.css('.description-block.mb-3.mt-md-0 > ul >li::text').getall()
        i = 1
        for description in summray_points:
            Product_Summary[i] = description
            i += 1

        #price processing depeding on page structure:
        price = response.css('.current-price::text').get()  
        if(price==None): #found nothing means different html page structure
            price = response.css('.item.price > span::text').get()

    
        yield {
            'Title' : response.css('h1.product-name::text').get().replace('\n',''),            
            'Price' : 'AED '+price,
            'Product Details' : Product_Summary
        }
        
