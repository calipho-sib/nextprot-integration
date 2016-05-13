from unittest import TestCase

from nextprot_integration.task.old.BashTask import BashTask, AbstractBashTaskWithLog


class TestBashTask(TestCase):

    def test_task(self):
        task = BashTask("sleep 2")
        result = task.run()
        self.assertEqual("success", result.task_status)
        self.assertEqual(2, int(result.duration_in_sec))
        self.assertEqual(0, result.exec_code)
        self.assertEqual(None, result.exec_output)
        self.assertEqual(None, result.exec_error)

    def test_task_command_not_found(self):
        task = BashTask("slep 2")
        result = task.run()
        self.assertEqual(127, result.exec_code)
        self.assertEqual(None, result.exec_output)
        self.assertEqual("/bin/sh: slep: command not found", result.exec_error)
        self.assertEqual("failure", result.task_status)

    def test_run_once(self):
        task = BashTask("echo toto")
        task.run()
        result = task.run()
        self.assertIsNone(result)

    def test_run_twice_on_error(self):
        task = BashTask("eco toto")
        task.run()
        result = task.run()
        self.assertIsNotNone(result)
        self.assertEqual("failure", result.task_status)

    def test_no_log(self):

        task = BashTask("echo toto")
        result = task.run()
        self.assertIsNone(result.log_path)
        self.assertIsNone(result.log_valid)

    def test_with_log(self):
        class BashTaskWithLog(AbstractBashTaskWithLog):
            def new_log_validator(self, log_file):
                return type("AbstractLogValidator", (object,), {"validate": lambda self: True})()

        task = BashTaskWithLog("nohup echo toto > /tmp/toto.log", log="/tmp/toto.log")
        result = task.run()
        self.assertEqual("/tmp/toto.log", result.log_path)
        self.assertTrue(result.log_valid)
        self.assertEqual("success", result.task_status)

    def test_with_log_missing_validator(self):
        class BashTaskWithLogNoValidator(AbstractBashTaskWithLog):
            def new_log_validator(self, log_file):
                return None

        task = BashTaskWithLogNoValidator("nohup echo toto > /tmp/toto.log", log="/tmp/toto.log")
        with self.assertRaises(ValueError):
            task.run()

    def test_with_log_failed(self):
        class BashTaskWithLog(AbstractBashTaskWithLog):
            def new_log_validator(self, log_file):
                return type("AbstractLogValidator", (object,), {"validate": lambda self: False})()

        task = BashTaskWithLog("nohup echo toto > /tmp/toto.log", log="/tmp/toto.log")
        result = task.run()
        self.assertEqual("/tmp/toto.log", result.log_path)
        self.assertFalse(result.log_valid)
        self.assertEqual("failure", result.task_status)