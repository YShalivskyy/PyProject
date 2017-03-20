from abc import ABC, abstractmethod
from datetime import datetime, date


class AbstractApartmentParser(ABC):

    def __init__(self):
        self._today = date.today()
        print("AbstractConstructor called")
        super(AbstractApartmentParser, self).__init__()

    @abstractmethod
    def parse_apartment_data(self, url, period):
        pass

    @abstractmethod
    def parse_date(self, rent_date, pattern):
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
