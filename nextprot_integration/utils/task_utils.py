from taskflow import task


class FakeErrorTask(task.Task):
    """Always raise a ValueError
    """

    def execute(self, stdout):
        raise ValueError("Raising a fake error")