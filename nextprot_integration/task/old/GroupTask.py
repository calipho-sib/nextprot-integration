
from nextprot_integration.task.old.AbstractTask import AbstractTask
from nextprot_integration.task.old.GroupTaskResult import GroupTaskResult


class GroupTask(AbstractTask):
    """A task composed of multiple tasks to run sequentially
    """

    def __init__(self, task_name):
        super(GroupTask, self).__init__(task_name=task_name, group_name=task_name)
        self.__tasks = []

    def exec_task(self, group_task_result):
        """execute all tasks"""

        if not isinstance(group_task_result, GroupTaskResult):
            raise ValueError("object " + str(type(group_task_result)) + ": should be of GroupTaskResult type")

        for task in self.__tasks:
            single_task_result = task.new_task_result()
            group_task_result.add_task_result(single_task_result)

            task.exec_task_then_analyse(single_task_result)
            group_task_result.update(single_task_result)

            if single_task_result.exec_code != 0:
                break

        if group_task_result.count_task_result() == self.count_task():
            group_task_result.exec_code = 0

    def new_task_result(self):
        return GroupTaskResult(self.task_name)

    def add_task(self, task):
        self.__tasks.append(task)

    def get_task(self, index):
        return self.__tasks[index]

    def count_task(self):
        return len(self.__tasks)

    def new_log_validator(self, log_file):
        return None

    def analyse_result_update_status(self, group_task_result):
        super(GroupTask, self).analyse_result_update_status(group_task_result)

        if group_task_result.task_status == "failure":
            group_task_result.task_status += ": task " + str(group_task_result.count_task_result()-1)

