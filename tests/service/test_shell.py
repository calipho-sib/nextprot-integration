from unittest import TestCase

from nextprot_integration.service.shell import BashService


class TestBashService(TestCase):

    def test_exec_bash(self):
        sh_result = BashService.exec_bash("echo koko")
        self.assertEqual(0, sh_result.return_code)
        self.assertEqual("koko", sh_result.stdout)
        self.assertEqual(None, sh_result.stderr)

    def test_exec_ant_task(self):
        self.fail()
