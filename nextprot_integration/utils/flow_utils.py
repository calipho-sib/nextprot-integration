from abc import abstractmethod


class AbstractFlowFactory(object):
    """An abstraction that defines a Flow factory.

    A factory should implement create_flow that creates Flow objects
    """

    @abstractmethod
    def create_flow(self):
        """create TaskFlow instance"""
        pass

