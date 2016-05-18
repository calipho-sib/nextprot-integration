import logging
import os
import sys

from nextprot_integration.service.git import GitService
from nextprot_integration.service.prerequisite import EnvService

logging.basicConfig(level=logging.INFO)

top_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.pardir,
                                       os.pardir))
sys.path.insert(0, top_dir)

import taskflow.engines
from taskflow.patterns import graph_flow
from taskflow.patterns import linear_flow
from taskflow import task
from taskflow.listeners import logging as logging_listener


class GitCheckoutTask(task.Task):
    """Update git repository to the lastest commit."""

    def execute(self, git_repo_path):
        gs = GitService()
        gs.checkout(repo_path=git_repo_path)


class GitUpdateTask(task.Task):
    """Update git repository to the lastest commit."""
    default_provides = ('stdout', 'stderr')

    def execute(self, git_repo_path):
        gs = GitService()
        result = gs.update(repo_path=git_repo_path)
        return result.stdout, result.stderr


class OutputAnalysing(task.Task):

    def execute(self, stdout, stderr):
        print("Executing '%s'" % self.name)
        print("Got input '%s' and '%s'" % (stdout, stderr))


def make_git_update_flow(repo_path):

    lf = linear_flow.Flow("pass-from-to")
    lf.add(GitUpdateTask(name='git-update-%s' % repo_path.rsplit('/', 1)[1],
                         inject={'git_repo_path': repo_path}))
    lf.add(OutputAnalysing(name='analyse-update-%s' % repo_path.rsplit('/', 1)[1]))

    return lf


def make_git_flow(repo_pathes):

    git_flow = graph_flow.Flow('git-flow')

    co_flow = graph_flow.Flow('git-co-flow')
    up_flow = graph_flow.Flow('git-up-flow')

    for repo_path in repo_pathes:
        co_flow.add(GitCheckoutTask(name='git-checkout-%s' % repo_path.rsplit('/', 1)[1],
                                    inject={'git_repo_path': repo_path}))
        up_flow.add(make_git_update_flow(repo_path))

    git_flow.add(co_flow, up_flow)

    return git_flow


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
    #gf = make_git_update_flow(repo_path=EnvService.get_np_cv_home())

    engine = taskflow.engines.load(gf)
    with logging_listener.DynamicLoggingListener(engine):
        engine.run()



