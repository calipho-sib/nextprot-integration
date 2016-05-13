
from nextprot_integration.task.old.AbstractTaskResult import AbstractTaskResult
from nextprot_integration.task.old.SingleTaskResult import SingleTaskResult


class GroupTaskResult(AbstractTaskResult):
    """Contains results of group tasks
    """

    def __init__(self, task_name):
        self.__starting_date = None
        self.__task_name = None
        super(self.__class__, self).__init__(task_name)

        self.__values = {}
        self.__task_results = []
        self.__duration_in_sec = None
        self.__exec_code = None
        self.__exec_output = None
        self.__exec_error = None
        self.__task_status = None

    @staticmethod
    def from_dicts(task_name, dicts):

        result = GroupTaskResult(task_name)

        for d in dicts:
            for field in AbstractTaskResult.MANDATORY_FIELDS:
                if field not in d:
                    raise ValueError("missing mandatory field '" + field + "'")

            res = SingleTaskResult(task_name=d["task_name"])
            del d["task_name"]
            res.from_dict(d)
            result.add_task_result(res)
        return result

    def add_task_result(self, task_result):
        if not issubclass(task_result.__class__, AbstractTaskResult):
            raise ValueError("object " + str(type(task_result)) + ": should be of AbstractTaskResult type")
        self.__task_results.append(task_result)

    def has_task_result(self):
        return len(self.__task_results) > 0

    def count_task_result(self):
        return len(self.__task_results)

    def get_task_result(self, index):
        if index >= self.count_task_result():
            raise ValueError("cannot access " + str(index) + "th record (total count=" + str(self.count_task_result()) + ")")

        return self.__task_results[index]

    def set_duration_in_sec(self, duration):
        self.__duration_in_sec = duration

    @property
    def task_name(self):
        return self.__task_name

    def set_task_name(self, name):
        self.__task_name = name

    def group_name(self):
        return None

    @property
    def starting_date(self):
        return self.__starting_date

    def set_starting_date(self, date):
        self.__starting_date = date

    @property
    def duration_in_sec(self):
        return self.__duration_in_sec

    @property
    def log_path(self):
        return None

    @property
    def log_valid(self):
        return None

    @property
    def exec_code(self):
        return self.__exec_code

    @exec_code.setter
    def exec_code(self, code):
        self.__exec_code = code

    @property
    def exec_output(self):
        return self.__exec_output

    @exec_output.setter
    def exec_output(self, output):
        self.__exec_output = output

    @property
    def exec_error(self):
        return self.__exec_error

    @exec_error.setter
    def exec_error(self, error):
        self.__exec_error = error

    @property
    def task_status(self):
        return self.__task_status

    @task_status.setter
    def task_status(self, status):
        self.__task_status = status

    def concat_field_value(self, method, value, sep='\n'):

        ret = getattr(self, method)

        if value is None:
            return ret
        elif ret is not None:
            return ret + sep + value
        return value

    def update(self, single_task_result):
        self.exec_code = single_task_result.exec_code
        self.exec_output = self.concat_field_value("exec_output", single_task_result.exec_output)
        self.exec_error = self.concat_field_value("exec_error", single_task_result.exec_error)

    def to_separated_values(self, fields=SingleTaskResult.FIELDS, sep=",", header=False):
        return GroupTaskResult.to_all_separated_values(self.__task_results, fields=fields, sep=sep, header=header)

    @staticmethod
    def to_all_separated_values(task_results, fields=AbstractTaskResult.FIELDS, sep=",", header=True):
        AbstractTaskResult.check_fields(fields)

        sv = ''
        if header:
            sv = sep.join(fields) + "\n"
        for task_result in task_results:
            sv += task_result.to_separated_values(sep=sep, fields=fields)

        return sv

    def __repr__(self):
        return "group task results: " + str(self.__task_results)
