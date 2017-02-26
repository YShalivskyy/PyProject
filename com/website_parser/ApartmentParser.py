import math
from datetime import datetime, date
from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

PHANTOMJS_PATH = './phantomjs'


class Parser:
    """ Class for parsing date from url of the apartment
    """
    def __init__(self):
        self._today = date.today()

    def _parse_oktvua_apartment_page(self, url, apartments):
        """ Method for parsing the page and retrieving date about the apartment.
        :param url: str
            Link to the apartment page
        :param apartments: dict
            Dictionary object to store data.
        :return: dict
            Object with the data
        """
        page = requests.get(url)
        page_content = BeautifulSoup(page.content, 'html.parser')

        calendar = []

        calendar.append(page_content.find(class_="calendar"))
        next_calendar = calendar[0].findNext(class_="calendar")
        if next_calendar:
            calendar.append(next_calendar)

        for calendar_page in calendar:
            for day in calendar_page.findAll(attrs={"data-busy": "busy"}):
                rent_date = self._parse_date(day["data-time-default"], "%d.%m.%Y")
                if rent_date[0]:
                    apartments["busy_apartments"].add((rent_date[1], day["data-price-sum"]))

            for day in calendar_page.findAll(attrs={"data-busy": "free"}):
                rent_date = self._parse_date(day["data-time-default"], "%d.%m.%Y")
                if rent_date[0]:
                    apartments["free_apartments"].add((rent_date[1], day["data-price-sum"]))

        return apartments

    def _create_calendar_pages_links(self, url, period=3):
        """ Method to generate links of the page to iterate through the calendar.
        Example: https://oktv.ua/id3093652?date=1.03.2017
                 https://oktv.ua/id3093652?date=1.05.2017
        :param url: str
            Link to the apartment page
        :param period: int
            Amount of month from today date to scrap the data
        :return: list
            List of urls
        """
        calendar_page_links = []
        i = -1
        while i < period:
            month = "1.{0}.{1}".format(((self._today.month + i) % 12 + 1),
                                       self._today.year + math.floor((self._today.month + i) / 12))
            link = "{0}?date={1}".format(url, month)
            i += 2
            calendar_page_links.append(link)

        return calendar_page_links

    def _parse_date(self, rent_date, pattern):
        """ Method for checking if the data from the calendar is older than today date.
        and parse into date object
        :param rent_date:
            Date of renting from the calendar
        :param pattern:
            String pattern to match
        :return:
            True, date object if the date is actual
            False, None if the date is in the past
        """
        rent_date = datetime.strptime(rent_date, pattern).date()
        if rent_date > self._today:
            return True, rent_date
        else:
            return False, None

    def parse_dobovo_apartment_data(self, url, period=3):
        """ Method for parsing the data opportunities for booking from www.dobovo.com.
        :param url: str
            Link to the apartment page
        :param period: int
            Amount of month from today date to scrap the data
        :return: dict
            The dictionary object with the sets of free and busy apartments
            for the certain date and price.
        """
        browser = webdriver.PhantomJS(PHANTOMJS_PATH)
        browser.get(url)

        apartments = {"free_apartments": set(), "busy_apartments": set()}

        for j in range(period):  # iterating through the calendars
            page_content = BeautifulSoup(browser.page_source, "html.parser")

            calendar = []
            calendar.append(page_content.find(class_="dbv_calendar_dates"))  # searching for the tag with data
            next_calendar = calendar[0].findNext(class_="dbv_calendar_dates")
            if next_calendar:
                calendar.append(next_calendar)

            for calendar_page in calendar:
                for day in calendar_page.findAll(class_="cell is-inactive clickable"):
                    apartments["busy_apartments"].add(
                        (self._parse_date(day["date"], "%Y-%m-%d")[1], day.find(class_="dbv_val").text))

                for day in calendar_page.findAll(class_=["cell clickable", "is-selected", "in", "out"]):
                    apartments["free_apartments"].add(
                        (self._parse_date(day["date"], "%Y-%m-%d")[1], day.find(class_="dbv_val").text))

                for day in calendar_page.findAll(class_="cell clickable"):
                    apartments["free_apartments"].add(
                        (self._parse_date(day["date"], "%Y-%m-%d")[1], day.find(class_="dbv_val").text))

            next_month = browser.find_element_by_class_name("calendar-next")  # clicking to get to a next calendar page
            next_month.click()
            sleep(0.05)

        browser.quit()
        return apartments

    def parse_oktvua_apartment_data(self, url, period=3):
        """ Method for parsing the data opportunities for booking from www.oktv.ua.
        :param url: str
            Link to the apartment page
        :param period: int
            Amount of month from today date to scrap the data
        :return: dict
            The dictionary object with the sets of free and busy apartments
            for the certain date and price.
        """
        apartments = {"free_apartments": set(), "busy_apartments": set()}
        page_links = self._create_calendar_pages_links(url, period)

        for link in page_links:
            apartments = self._parse_oktvua_apartment_page(link, apartments)

        return apartments
