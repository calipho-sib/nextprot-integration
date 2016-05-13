from unittest import TestCase

from nextprot_integration.task.old.BashTask import BashTask
from nextprot_integration.task.old.GroupTask import GroupTask
from nextprot_integration.task.old.GroupTaskResult import GroupTaskResult


class TestGroupTask(TestCase):

    def test_group_task_result(self):
        result = GroupTaskResult(task_name="echoes")
        self.assertIsNotNone(result.starting_date)
        self.assertEqual("echoes", result.task_name)

    def test_add_task(self):
        group = GroupTask(task_name="echoes")

        self.assertEqual(0, group.count_task())
        group.add_task(BashTask(command="echo toto"))
        group.add_task(BashTask(command="sleep 2"))
        group.add_task(BashTask(command="echo bob"))
        self.assertEqual("echoes", group.task_name)
        self.assertEqual("echoes", group.group_name)
        self.assertEqual(3, group.count_task())

    def test_run_3_success(self):
        group = GroupTask("echoes")

        group.add_task(BashTask(command="echo toto"))
        group.add_task(BashTask(command="sleep 2"))
        group.add_task(BashTask(command="echo bob"))
        result = group.run()
        self.assertEqual(0, result.exec_code)
        self.assertEqual(3, result.count_task_result())
        self.assertTrue(result.duration_in_sec >= 2)
        self.assertEqual("toto\nbob", result.exec_output)
        self.assertEqual(None, result.exec_error)
        self.assertEqual("success", result.task_status)

    def test_run2(self):
        group = GroupTask("echoes")

        group.add_task(BashTask(command="echo toto"))
        group.add_task(BashTask(command="sleep 2"))
        group.add_task(BashTask(command="echo bob"))
        result = group.run()

        for index in range(result.count_task_result()):
            self.assertIsNotNone(result.get_task_result(index).duration_in_sec)
            self.assertTrue(result.get_task_result(index).duration_in_sec>0)

    def test_run_task_1_success_1_failure(self):
        group = GroupTask("echoes")

        group.add_task(BashTask(command="echo toto"))
        group.add_task(BashTask(command="slep 2"))
        group.add_task(BashTask(command="echo bob"))
        result = group.run()

        self.assertEqual(127, result.exec_code)
        self.assertEqual(2, result.count_task_result())
        self.assertEqual("toto", result.exec_output)
        self.assertEqual("/bin/sh: slep: command not found", result.exec_error)
        self.assertEqual("failure: task 1", result.task_status)

    def test_run_once(self):
        group = GroupTask("echoes")

        group.add_task(BashTask(command="echo toto"))
        group.add_task(BashTask(command="sleep 2"))
        group.add_task(BashTask(command="echo bob"))
        group.run()
        result = group.run()
        self.assertIsNone(result)

    def test_run_twice_when_error(self):
        group = GroupTask("echoes")

        group.add_task(BashTask(command="echo toto"))
        group.add_task(BashTask(command="slep 2"))
        group.add_task(BashTask(command="echo bob"))
        group.run()
        result = group.run()
        self.assertIsNotNone(result)
        self.assertEqual("failure: task 1", result.task_status)

    def test_doing_tasks(self):
        task1 = GroupTask("resting")
        task1.add_task(BashTask(command="sleep 2", task_name="sleeping a bit"))
        task1.add_task(BashTask(command="echo zzzzzz", task_name="ronking"))
        task1.add_task(BashTask(command="sleep 1", task_name="sleeping a bit again"))
        task1.add_task(BashTask(command="echo slept well", task_name="awaking"))

        task2 = GroupTask("calling friends")
        task2.add_task(BashTask(command="echo toto", task_name="calling toto"))
        task2.add_task(BashTask(command="echo bob", task_name="calling bob"))

        tasks = GroupTask("todo")
        tasks.add_task(task1)
        tasks.add_task(task2)

        results = tasks.run()
        print results.to_separated_values(header=True)


