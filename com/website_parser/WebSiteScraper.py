import pprint
import urllib.parse
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from com.website_parser.ApartmentParser import Parser

PHANTOMJS_PATH = './phantomjs'


class WebSiteScraper:
    """ Class for scrapping data from websites, generating links of pages for parsing,
    saving the parsed data.
    """
    def __init__(self, websites_urls=None):
        """ Initializing the container object _scraped_data to store parsed data.
        :param websites_urls:
            List of websites to parse data from.
        """
        if websites_urls is None:
            self._websites_urls = ["http://www.oktv.ua", "http://www.dobovo.com"]
        self._scraped_data = {"oktvua": {}, "dobovo": {}}

    def _scrap_oktvua_apartments_urls(self, city_name):
        """ Method to scrap urls of apartments from www.oktv.ua
        Send the name of the city to the input text-box.

        :param city_name: str
            The name of the city to search the apartments
        :returns list
            The list of urls of apartments.
        """
        browser = webdriver.PhantomJS(PHANTOMJS_PATH)
        browser.get("http://www.oktv.ua/search")
        apartments_urls = []

        city = browser.find_element_by_id("input-addr-text")
        city.send_keys(city_name + Keys.RETURN)
        page_content = BeautifulSoup(browser.page_source, "html.parser")
        apartments = page_content.findAll(class_="col-lg-4 col-md-6 col-sm-6 col-xs-12 no-class")

        for apartment in apartments:
            apartments_urls.append("http://www.oktv.ua" + apartment.a["href"])

        browser.quit()
        return apartments_urls

    def _scrap_dobovo_apartment_urls(self):
        """ Method to scrap urls of apartments from www.dobovo.com
        Submits the "Search" button to go to the page with apartments.

        :returns list
            The list of urls of apartments.
        """
        browser = webdriver.PhantomJS(PHANTOMJS_PATH)
        browser.get("http://www.dobovo.com/ua/")

        apartments_urls = []

        current_url = browser.current_url
        search_button = browser.find_element_by_id("dbv_search_btn")
        search_button.click()
        while current_url == browser.current_url:
            sleep(0.1)

        page_content = BeautifulSoup(browser.page_source, "html.parser")
        apartments = page_content.findAll(class_="item__title dbv_js_apttitle dbv_js_apt_url dbv_js_url_with_dates")

        for apartment in apartments:  # encoding the url of the apartment into URL encoding
            url = apartment["href"]
            domen = url[:25]          # splitting the url into 2 strings - http://www.dobovo.com/ua/ and
            ap_url = url[25:]         # example   /київ-квартири-подобово/комфортна-студіо-в-центрі-міста-99053.html
            ap_url = urllib.parse.quote(ap_url, safe='')
            apartments_urls.append(domen+ap_url)

        browser.quit()
        return apartments_urls

    def parse_apartments_pages(self):
        """ Method which which creates lists of urls of apartments from websites.
        Calls methods to parse data from urls in the loop.
        Collecting all the information in the self._scraped_data object
        """
        oktvua_urls = self._scrap_oktvua_apartments_urls("Киев")
        dobovo_urls = self._scrap_dobovo_apartment_urls()

        parser = Parser()

        print("Scraping data from www.oktv.ua")
        for url in oktvua_urls:
            self._scraped_data["oktvua"][url] = parser.parse_oktvua_apartment_data(url, 2)

        print("Scraping data from www.dobovo.com")
        for url in dobovo_urls:
            self._scraped_data["dobovo"][url] = parser.parse_dobovo_apartment_data(url, 2)

    def print_parsed_data(self):
        pprint.pprint(self._scraped_data)


def main():
    s = WebSiteScraper()
    s.parse_apartments_pages()
    s.print_parsed_data()

if __name__ == "__main__":
    main()