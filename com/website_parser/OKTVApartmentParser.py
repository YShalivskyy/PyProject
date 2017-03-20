import math
import requests
from bs4 import BeautifulSoup
from com.website_parser.Parser import AbstractApartmentParser
from com.website_parser.CustomExceptions import PageNotFoundException


class OKTVApartmentParser(AbstractApartmentParser):

    def parse_apartment_data(self, url, period):
        """ Method for parsing the data opportunities for booking.
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

        try:
            for link in page_links:
                page = requests.get(link)
                if page.status_code == 404:
                    raise PageNotFoundException("Expression: page.requests.get(link)",
                                                "The apartment page wasn't found", self.__class__)
                page_content = BeautifulSoup(page.content, 'html.parser')

                calendar = []

                calendar.append(page_content.find(class_="calendar"))
                next_calendar = calendar[0].findNext(class_="calendar")
                if next_calendar:
                    calendar.append(next_calendar)

                for calendar_page in calendar:
                    # day = calendar_page.findAll(attrs={"data-busy": "busy"})

                    for day in calendar_page.findAll(attrs={"data-busy": "busy"}):
                        rent_date = self.parse_date(day["data-time-default"], "%d.%m.%Y")
                        if rent_date[0]:
                            apartments["busy_apartments"].add((rent_date[1], day["data-price-sum"]))

                    for day in calendar_page.findAll(attrs={"data-busy": "free"}):
                        rent_date = self.parse_date(day["data-time-default"], "%d.%m.%Y")
                        if rent_date[0]:
                            apartments["free_apartments"].add((rent_date[1], day["data-price-sum"]))

            return apartments

        except AttributeError as e:
            print("AttributeError: ", e, self.__class__)
        except ConnectionError as e:
            print("ConnectionError: ", e, self.__class__)
        except KeyError as e:
            print("Key Error: ", e, self.__class__)
        except PageNotFoundException as e:
            print(e.print_traceback())
        except Exception as e:
            print("Undefined exception: ", e, self.__class__)

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

    def parse_date(self, rent_date, pattern):
        return super(OKTVApartmentParser, self).parse_date(rent_date, pattern)
