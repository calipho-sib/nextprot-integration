import os
from abc import abstractmethod

import datetime


class AbstractTaskResult(object):

    FIELDS = ["group_name", "task_name", "task_status", "exec_code", "exec_output", "exec_error", "log_path",
              "log_valid", "starting_date", "duration_in_sec"]
    IMMUTABLE_FIELDS = ["task_name", "starting_date"]
    MANDATORY_FIELDS = ["task_name"]

    # error is non recoverable, exception and warning are
    FAILURES = ["error", "exception", "warning"]

    def __init__(self, task_name):
        self.set_task_name(task_name)
        self.set_starting_date(datetime.datetime.now())

    @abstractmethod
    def set_task_name(self, name):
        pass

    @abstractmethod
    def set_starting_date(self, date):
        pass

    @abstractmethod
    def set_duration_in_sec(self, duration):
        pass

    @abstractmethod
    def task_name(self):
        pass

    @abstractmethod
    def starting_date(self):
        pass

    @abstractmethod
    def group_name(self):
        pass

    @abstractmethod
    def task_status(self):
        pass

    @abstractmethod
    def exec_code(self):
        pass

    @abstractmethod
    def exec_output(self):
        pass

    @abstractmethod
    def exec_error(self):
        pass

    @abstractmethod
    def log_path(self):
        pass

    @abstractmethod
    def log_valid(self):
        pass

    @abstractmethod
    def duration_in_sec(self):
        pass

    @property
    def starting_date_formatted(self):
        return self.starting_date.strftime("%Y%m%d%H%M")

    def produce_log(self):
        return self.log_path is not None and os.path.isfile(self.log_path) and os.path.getsize(self.log_path) > 0

    @staticmethod
    def check_fields(fields):
        for field in fields:
            AbstractTaskResult.check_field(field)

    @staticmethod
    def check_field(field, fields=FIELDS):
        if field not in fields:
            raise ValueError("field '" + field + "' does not exist in " + str(fields))

    @staticmethod
    def all_fields():
        return AbstractTaskResult.FIELDS

    @staticmethod
    def mandatory_fields():
        return AbstractTaskResult.IMMUTABLE_FIELDS
