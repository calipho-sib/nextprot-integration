from unittest import TestCase

import datetime

from nextprot_integration.task.old.GroupTaskResult import GroupTaskResult
from nextprot_integration.task.old.SingleTaskResult import SingleTaskResult


class TestTaskResult(TestCase):

    def test_constr(self):
        result = SingleTaskResult(task_name="bob")
        result.exec_code = 0
        self.assertEqual("bob", result.task_name)
        self.assertEqual(0, result.exec_code)

    def test_task_name_immutable(self):
        result = SingleTaskResult(task_name="bob")
        result.from_dict({"task_name":"bobby", "exec_code":1})
        self.assertEqual("bob", result.task_name)
        self.assertEqual(1, result.exec_code)

    def test_from_dicts(self):

        result = GroupTaskResult.from_dicts(task_name="few tasks", dicts=[
            {"task_name":"bob", "exec_code":0, "duration_in_sec":1},
            {"task_name":"bobby", "exec_code":1, "duration_in_sec":2, "exec_output":"yo"}
        ])

        self.assertEqual("bob", result.get_task_result(0).task_name)
        self.assertEqual(1, result.get_task_result(1).exec_code)
        self.assertEqual(None, result.get_task_result(0).exec_output)
        self.assertEqual("yo", result.get_task_result(1).exec_output)

    def test_from_dicts_missing_field(self):

        with self.assertRaises(ValueError):
            GroupTaskResult.from_dicts(task_name="few tasks", dicts=[
                {"exec_code":0}
            ])

    def test_to_sep_values(self):
        t0=datetime.datetime.now()
        result = SingleTaskResult(task_name="bob")
        result.exec_code = 0
        result.set_duration_in_sec(1)
        csv_values = result.to_separated_values()
        self.assertEqual("None,bob,None,0,None,None,None,None,"+t0.strftime("%Y%m%d%H%M")+",1\n", csv_values)

    def test_to_sep_values_given_fields(self):
        result = SingleTaskResult(task_name="bob")
        result.exec_code = 0
        csv_values = result.to_separated_values(fields=["task_name", "exec_code"])
        self.assertEqual("bob,0\n", csv_values)

    def test_to_csv(self):
        result = GroupTaskResult.from_dicts(task_name="few tasks", dicts=[
            {"task_name":"bob", "exec_code":0, "duration_in_sec":1},
            {"task_name":"joe", "exec_code":1, "duration_in_sec":2}
        ])

        csv_values = result.to_separated_values(fields=["task_name", "exec_code"])
        self.assertEqual("bob,0\njoe,1\n", csv_values)

    def test_to_csv_with_headers(self):
        result = GroupTaskResult.from_dicts(task_name="few tasks", dicts=[
            {"task_name":"bob", "exec_code":0, "duration_in_sec":1},
            {"task_name":"joe", "exec_code":1, "duration_in_sec":2}
        ])

        csv_values = result.to_separated_values(fields=["task_name", "exec_code"], header=True)
        self.assertEqual("task_name,exec_code\nbob,0\njoe,1\n", csv_values)

    def test_produce_log(self):
        result = SingleTaskResult(task_name="bob")
        print result.produce_log()