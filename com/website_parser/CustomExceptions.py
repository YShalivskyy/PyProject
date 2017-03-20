class Error(Exception):
    """Base class for exceptions in this module."""
    def print_traceback(self):
        pass


class PageNotFoundException(Error):
    """ Exception raised when the web page wasn't found

        :param expression, str
            input expression in which the error occurred
        :param message, str
            explanation of the error
        :param _class_name, str
            name of the class where the error occurred
    """

    def __init__(self, expression, message, _class_name):
        self.expression = expression
        self.message = message
        self._class_name = _class_name

    def print_traceback(self):
        print(self.expression, self.message, self._class_name)


class UrlListException(Error):
    """ Exception raised when the list with url is empty

        :param expression, str
            input expression in which the error occurred
        :param message, str
            explanation of the error
        :param _class_name, str
            name of the class where the error occurred
    """

    def __init__(self, expression, message, _class_name):
        self.expression = expression
        self.message = message
        self._class_name = _class_name

    def print_traceback(self):
        print(self.expression, self.message, self._class_name)