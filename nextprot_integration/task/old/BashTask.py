
from nextprot_integration.service.shell import BashService
from nextprot_integration.task.old.AbstractSingleTask import AbstractSingleTask
from nextprot_integration.task.old.SingleTaskResult import SingleTaskResult


class BashTask(AbstractSingleTask):

    def __init__(self, command, task_name=None):
        super(BashTask, self).__init__(task_name=task_name)
        self.__command = command

    def exec_task(self, task_result):
        if not isinstance(task_result, SingleTaskResult):
            raise ValueError("object " + str(type(task_result)) + ": should be of SingleTaskResult type")

        shell_result = BashService.exec_bash(self.__command)

        task_result.exec_output = shell_result.stdout
        task_result.exec_error = shell_result.stderr
        task_result.exec_code = shell_result.return_code

    def new_log_validator(self, log_file):
        return None


class AbstractBashTaskWithLog(BashTask):

    def __init__(self, command, log):
        super(AbstractBashTaskWithLog, self).__init__(command)
        self.__log_path = log

    def exec_task(self, task_result):
        super(AbstractBashTaskWithLog, self).exec_task(task_result)

        task_result.log_path = self.__log_path

    def new_log_validator(self, log_file):
        pass
