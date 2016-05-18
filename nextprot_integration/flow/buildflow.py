import os
import sys

from nextprot_integration.service.git import GitService
from nextprot_integration.service.prerequisite import EnvService

top_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.pardir,
                                       os.pardir))
sys.path.insert(0, top_dir)

import taskflow.engines
from taskflow.patterns import graph_flow
from taskflow.patterns import linear_flow
from taskflow import task
from taskflow.listeners import logging as logging_listener
from taskflow.types import notifier

ANY = notifier.Notifier.ANY

# 1. flow to check, update and validate source repo
# 2. flow to
#

class GitUpdateTask(task.Task):
    """Update git repository to the lastest commit."""
    default_provides = ('stdout', 'stderr')

    def execute(self, git_repo_path):
        gs = GitService()
        result = gs.update(repo_path=git_repo_path)
        return result.stdout, result.stderr


class OutputAnalyzing(task.Task):

    def execute(self, stdout, stderr):
        print("Executing '%s'" % self.name)
        print("Analyzing stdout '%s' and stderr '%s'" % (stdout, stderr))


def make_git_update_flow(repo_path):

    lf = linear_flow.Flow("pass-from-to")
    lf.add(GitUpdateTask(name='git-update-%s' % repo_path.rsplit('/', 1)[1],
                         inject={'git_repo_path': repo_path}))
    lf.add(OutputAnalyzing(name='analyse-update-%s' % repo_path.rsplit('/', 1)[1]))

    return lf


def make_git_flow(repo_pathes):

    git_flow = graph_flow.Flow('git-flow')

    for repo_path in repo_pathes:
        git_flow.add(make_git_update_flow(repo_path))

    return git_flow


# These two functions connect into the state transition notification emission
# points that the engine outputs, they can be used to log state transitions
# that are occurring, or they can be used to suspend the engine (or perform
# other useful activities).
def flow_watch(state, details):
    print('Flow => %s' % state)


def task_watch(state, details):
    print('Task %s => %s' % (details.get('task_name'), state))


def print_wrapped(text):
    print("-" * (len(text)))
    print(text)
    print("-" * (len(text)))


if __name__ == "__main__":
    REPOS = [EnvService.get_np_perl_parsers_home(),
             EnvService.get_np_loaders_home(),
             EnvService.get_np_cv_home()]

    print_wrapped('Running all tasks:')

    gf = make_git_flow(repo_pathes=REPOS)

    e = taskflow.engines.load(gf, engine='serial')
    # This registers all (ANY) state transitions to trigger a call to the
    # flow_watch function for flow state transitions, and registers the
    # same all (ANY) state transitions for task state transitions.
    e.notifier.register(ANY, flow_watch)
    e.atom_notifier.register(ANY, task_watch)

    e.compile()
    e.prepare()
    # After prepare the storage layer + backend can now be accessed safely...
    backend = e.storage.backend

    print("----------")
    print("Before run")
    print("----------")
    print(backend.memory.pformat())
    print("----------")

    with logging_listener.DynamicLoggingListener(e):
        e.run()

        print("---------")
        print("After run")
        print("---------")
        for path in backend.memory.ls_r(backend.memory.root_path, absolute=True):
            value = backend.memory[path]
            if value:
                print("%s -> %s" % (path, value))
            else:
                print("%s" % (path))


