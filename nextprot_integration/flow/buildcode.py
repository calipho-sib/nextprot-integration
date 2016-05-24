import time

import shutil

import re

from nextprot_integration.service.git import GitService
from nextprot_integration.service.prerequisite import EnvService
from nextprot_integration.service.shell import BashService
from nextprot_integration.settings import Settings
from taskflow import task
import taskflow.engines
from taskflow.patterns import linear_flow
from taskflow.listeners import timing
from taskflow.types import notifier

ANY = notifier.Notifier.ANY


class GitUpdate(task.Task):
    """Update git repository to the latest commit.
    """
    default_provides = ('stdout', 'stderr')

    def execute(self, git_repo_path):
        """Execute this task.
        :param git_repo_path: the git repository to update
        :return: the tuple (stdout, stderr)
        """
        gs = GitService(dev_mode=True)
        result = gs.update(repo_path=git_repo_path)
        return result.stdout, result.stderr


class OutputAnalysis(task.Task):
    """Consume and analyse stdout of the previous task
    raise a ValueError if stdout is invalid
    """

    def execute(self, stdout):
        """Analyse task output
        :param stdout: output of the previous task
        """
        ln = 0
        errors = ""
        for line in stdout.split("\n"):
            if re.match(r'.*ERROR.*', line):
                errors += 'Line '+str(ln) + ': ' + line+"\n"
            ln += 1

        if len(errors) > 0:
            raise ValueError("Error found in output "+str(errors))


class LogTask(task.Task):
    """write stdout into a specified log file
    :return input 'stdout'
    """
    default_provides = 'stdout'

    def execute(self, stdout, log_file_path):

        with open(log_file_path, 'w') as log_file:
            log_file.write(stdout)

        return stdout


class ToolsIntegrationInstallJarCode(task.Task):
    """build and install tools integration jars in proper place
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_task_path=settings.get_tools_integration_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_task="install-jars",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/install-tools-integration-jars_"+time.strftime("%Y%m%d-%H%M%S")+".log"

    def revert(self, settings, *args, **kwargs):
        print ("clean "+str(settings.get_jar_repository_path()))
        shutil.rmtree(settings.get_jar_repository_path())


class ToolsIntegrationInstallPerlCode(task.Task):
    """build and install tools integration jars in proper place
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_task_path=settings.get_tools_integration_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_task="install-perl",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/install-tools-integration-perl_"+time.strftime("%Y%m%d-%H%M%S")+".log"

    def revert(self, settings, *args, **kwargs):
        print ("clean "+str(settings.get_perl_install_path()))
        shutil.rmtree(settings.get_perl_install_path())


def make_git_update_flow():
    """update repositories nextprot-perl-parsers and nextprot-loaders
    """
    lf = linear_flow.Flow("update-repos")

    for repo_path in [EnvService.get_np_perl_parsers_home(), EnvService.get_np_loaders_home()]:
        lf.add(GitUpdate(name='git-update-%s' % repo_path.rsplit('/', 1)[1],
                         inject={'git_repo_path': repo_path}))
    return lf


def make_flow():
    """
    update-code-repos -> ant-install-jars --(output,logfile)--> store output in log file --(output)--> analysis output
    """
    git_flow = linear_flow.Flow('code-building-flow')

    git_flow.add(make_git_update_flow())

    git_flow.add(ToolsIntegrationInstallJarCode(inject={'settings': Settings(dev_mode=True)}))
    git_flow.add(LogTask(name="log jars installation ant output"))
    git_flow.add(OutputAnalysis(name="analyse jars installation ant output"))

    git_flow.add(ToolsIntegrationInstallPerlCode(inject={'settings': Settings(dev_mode=True)}))
    git_flow.add(LogTask(name="log perl installation ant output"))
    git_flow.add(OutputAnalysis(name="analyse perl installation ant output"))

    return git_flow


def flow_watch(state, details):
    print("Flow '%s' transition to state %s" % (details['flow_name'], state))


def task_watch(state, details):
    print('Task %s => %s' % (details.get('task_name'), state))


def print_wrapped(text):
    print("-" * (len(text)))
    print(text)
    print("-" * (len(text)))


if __name__ == "__main__":
    print_wrapped('Running all tasks:')

    gf = make_flow()

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

    with timing.PrintingDurationListener(e):
        e.run()

        print("---------")
        print("After run")
        print("---------")
        for path in backend.memory.ls_r(backend.memory.root_path, absolute=True):
            value = backend.memory[path]
            if value:
                print("%s -> %s" % (path, value))
            else:
                print("%s" % path)
