import logging

from nextprot_integration.task.old.AbstractTaskResult import AbstractTaskResult


class SingleTaskResult(AbstractTaskResult):

    def __init__(self, task_name):
        self.__values = {}
        super(SingleTaskResult, self).__init__(task_name)

    def __get_field_value(self, field, fields=AbstractTaskResult.FIELDS):
        AbstractTaskResult.check_field(field, fields=fields)

        if field not in self.__values:
            return None
        return self.__values[field]

    def from_dict(self, kvs):
        for field, value in kvs.iteritems():
            AbstractTaskResult.check_field(field)
            if field not in AbstractTaskResult.IMMUTABLE_FIELDS:
                self.__values[field] = value
            else:
                logging.warn("field '" + field + "' is immutable")

    @property
    def task_name(self):
        return self.__get_field_value("task_name")

    def set_task_name(self, name):
        self.__values["task_name"] = name

    @property
    def starting_date(self):
        return self.__get_field_value("starting_date")

    def set_starting_date(self, date):
        self.__values["starting_date"] = date

    @property
    def group_name(self):
        return self.__get_field_value("group_name")

    @group_name.setter
    def group_name(self, name):
        self.__values["group_name"] = name

    @property
    def task_status(self):
        return self.__get_field_value("task_status")

    @task_status.setter
    def task_status(self, name):
        self.__values["task_status"] = name

    @property
    def exec_code(self):
        return self.__get_field_value("exec_code")

    @exec_code.setter
    def exec_code(self, code):
        self.__values["exec_code"] = code

    @property
    def exec_output(self):
        return self.__get_field_value("exec_output")

    @exec_output.setter
    def exec_output(self, output):
        self.__values["exec_output"] = output

    @property
    def exec_error(self):
        return self.__get_field_value("exec_error")

    @exec_error.setter
    def exec_error(self, error):
        self.__values["exec_error"] = error

    @property
    def log_path(self):
        return self.__get_field_value("log_path")

    @log_path.setter
    def log_path(self, path):
        self.__values["log_path"] = path

    @property
    def log_valid(self):
        return self.__get_field_value("log_valid")

    @log_valid.setter
    def log_valid(self, valid):
        self.__values["log_valid"] = valid

    @property
    def duration_in_sec(self):
        return self.__get_field_value("duration_in_sec")

    def set_duration_in_sec(self, duration):
        self.__values["duration_in_sec"] = duration

    def __to_field_value_string(self, field, fields=AbstractTaskResult.FIELDS):
        if field == "starting_date":
            return self.starting_date_formatted
        return self.__get_field_value(field, fields=fields)

    def to_separated_values(self, fields=AbstractTaskResult.FIELDS, sep=","):
        AbstractTaskResult.check_fields(fields)

        values = [self.__to_field_value_string(field, fields) for field in fields]
        sv = sep.join(map(lambda v: str(v), values)) + "\n"

        return sv

    def __repr__(self):
        return "single task result: " + str(self.__values)
