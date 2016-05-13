from nextprot_integration.task.old.AbstractTask import AbstractTask
from nextprot_integration.task.old.SingleTaskResult import SingleTaskResult


class AbstractSingleTask(AbstractTask):

    def __init__(self, task_name=None):
        super(AbstractSingleTask, self).__init__(task_name=task_name)

    def new_task_result(self):
        return SingleTaskResult(self.task_name)

    def exec_task(self, task_result):
        pass

    def new_log_validator(self, log_file):
        pass
