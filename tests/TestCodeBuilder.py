from unittest import TestCase

from nextprot_integration.CodeBuilder import CodeBuilder
from nextprot_integration.workflow import IntegrationWorkflow


class TestCodeBuilder(TestCase):

    def test_build_integration_perl(self):
        builder = CodeBuilder(IntegrationWorkflow(dev_mode=True))
        builder.build_integration_perl()

    def test_build_integration_jars(self):
        builder = CodeBuilder(IntegrationWorkflow(dev_mode=True))
        builder.build_integration_jars()

    def test_build_np_mapping_jar(self):
        builder = CodeBuilder(IntegrationWorkflow(dev_mode=True))
        builder.build_np_mappings_jar()
