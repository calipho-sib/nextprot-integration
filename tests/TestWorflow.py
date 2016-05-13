from unittest import TestCase

from nextprot_integration.workflow import IntegrationWorkflow


class TestWorflow(TestCase):

    def test_ant_lib(self):
        workflow = IntegrationWorkflow(dev_mode=True)
        self.assertEqual("/Users/fnikitin/Projects/nextprot-loaders/lib", workflow.get_ant_lib_dir())

