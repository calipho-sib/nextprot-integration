from abc import abstractmethod

import datetime


"""They're 3 kind of tasks:
- tasks that always run (i.e. IntegrationWorflow.__init)
- tasks that run once (i.e. download_listed_cvs)
- tasks that run on specific condition (i.e. build_code rerun when np_loaders or np_perl_parsers made a git pull)

A Task should have the following properties:
- tells if it ran properly (intercept eventual exit from shell execution and track it)
- on error run task (+gives the log/error code, give the error type(recoverable or not?))
- before run task
- after run task
- run condition (see 3 types of tasks)
- write info before run (type name, command, ...)
- write info after run + validation (error ? log ...)

Each task is supposed to:
1. exec if run_condition true // depending on the type of task and the previous workflow execution!
2. run task
3. returns ret code (ERROR, OK) with logs
4. validate the logs (ERROR, OK)

One of the run condition to consider depends on previous workflow executions (see Tracker role).
If task does not always run, check if already run in previous exec and check previous state (error code...)
"""


class AbstractTask(object):
    def __init__(self, task_name=None, group_name=None):
        """Execute this task when condition is True
        """
        self.__skip = False
        if task_name is None:
            self.__task_name = self.__class__.__name__
        else:
            self.__task_name = task_name
        if group_name is None:
            self.__group_name = None
        else:
            self.__group_name = group_name

    @property
    def skip(self):
        """return True if this task must be skipped"""
        return self.__skip

    @skip.setter
    def skip(self, boolean):
        """set False if has to be executed"""
        self.__skip = boolean

    @staticmethod
    def exec_then_skip(task_result):
        """skip next execution if no error
        """
        if task_result.exec_code == 0:
            return True
        return False

    @abstractmethod
    def exec_task(self, task_result):
        """execute task and update TaskResult"""
        pass

    @abstractmethod
    def new_task_result(self):
        """create new instance of TaskResult"""
        pass

    @abstractmethod
    def new_log_validator(self, log_file):
        """return a log validator that implement validate"""
        pass

    def analyse_result_update_status(self, task_result):
        """analyse task and update task status given execution results"""

        # analyse log if exists
        if task_result.produce_log():
            validator = self.new_log_validator(task_result.log_path)
            if validator is None:
                raise ValueError("missing log validator to evaluate produced log '"+task_result.log_path+"'")
            task_result.log_valid = validator.validate()

        # update status
        if task_result.exec_code != 0 or (task_result.log_valid is not None and not task_result.log_valid):
            task_result.task_status = "failure"
        else:
            task_result.task_status = "success"

    def exec_task_then_analyse(self, task_result):
        """execute task, set time duration and analyse results
        :param task_result: output of task execution
        """
        # execute task
        self.exec_task(task_result)
        # calculate execution duration
        task_result.set_duration_in_sec((datetime.datetime.now()-task_result.starting_date).total_seconds())
        # update task result status
        self.analyse_result_update_status(task_result)

        self.skip = self.exec_then_skip(task_result)

    def run(self):
        """execute task and return TaskResult"""
        if not self.skip:
            new_task_result = self.new_task_result()
            new_task_result.group_name = self.group_name
            self.exec_task_then_analyse(new_task_result)
            return new_task_result
        return None

    @property
    def task_name(self):
        return self.__task_name

    @property
    def group_name(self):
        """get group name"""
        return self.__group_name

