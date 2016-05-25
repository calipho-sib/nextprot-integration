from unittest import TestCase

import taskflow.engines
from taskflow.patterns import linear_flow


class TestFlow(TestCase):

    @staticmethod
    def run_flow(flow):
        e = taskflow.engines.load(flow, engine='serial')
        e.run()

    def test_create_flow(self):

        TestFlow.run_flow(linear_flow.Flow('test-flow'))


