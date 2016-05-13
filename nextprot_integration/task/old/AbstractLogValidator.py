from abc import abstractmethod


class AbstractLogValidator(object):
    """Responsible of validating a log file
    """

    def __init__(self, log_file):
        self.__log_file = log_file

    @abstractmethod
    def validate(self):
        """this method should read log file and return True if its content is valid else False
        """
        pass
