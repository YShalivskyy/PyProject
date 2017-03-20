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
