# coding=utf-8
import os
import time
import shutil
import re

from nextprot_integration.service.git import GitService
from nextprot_integration.service.prerequisite import EnvService
from nextprot_integration.service.shell import BashService
from taskflow import task
from taskflow.patterns import linear_flow, unordered_flow


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


class FakeErrorTask(task.Task):
    """Always raise a ValueError
    """

    def execute(self, stdout):
        raise ValueError("Raising a fake error")


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


class ToolsIntegrationBuildJarCode(task.Task):
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
        file_path = settings.get_jar_repository_path()+"/com.genebio.nextprot.dataloader-jar-with-dependencies.jar"
        print ("remove file "+file_path)
        os.remove(file_path)


class ToolsIntegrationBuildPerlLibs(task.Task):
    """install perl dependencies, build and deploy perl libs found in repo ${np.parser.pl}
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_task_path=settings.get_tools_integration_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_task="install-perl",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/install-tools-integration-perl_"+time.strftime("%Y%m%d-%H%M%S")+".log"

    def revert(self, settings, *args, **kwargs):
        print ("cleaning "+str(EnvService.get_nextprot_perl5_lib()))
        shutil.rmtree(EnvService.get_nextprot_perl5_lib())


class ToolsMappingsBuildJarCode(task.Task):
    """build and install tools mappings jar in proper place

    Remark: the build jar com.genebio.nextprot.genemapping.datamodel.jar is deployed in
    EnvService.get_np_loaders_home()/com.genebio.nextprot.genemapping.datamodel/target
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_task_path=settings.get_tools_mappings_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_task="install-jar",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/install-mappings-integration-jar_"+time.strftime("%Y%m%d-%H%M%S")+".log"

    def revert(self, settings, *args, **kwargs):
        target_dir = EnvService.get_np_loaders_home()+"/com.genebio.nextprot.genemapping.datamodel/target"

        print ("cleaning "+target_dir)
        shutil.rmtree(target_dir)


def make_git_update_flow():
    """update repositories nextprot-perl-parsers and nextprot-loaders
    """
    lf = linear_flow.Flow("update-repos")

    for repo_path in [EnvService.get_np_perl_parsers_home(), EnvService.get_np_loaders_home()]:
        lf.add(GitUpdate(name='git-update-%s' % repo_path.rsplit('/', 1)[1],
                         inject={'git_repo_path': repo_path}))
    return lf


def make_build_code_flow(settings):
    """
    update-code-repos
     │
     `──> build-integration-jars --(output,logfile)--> store output in log file --(output)--> analysis output
     │
     └──> build-perl-libs --(output,logfile)--> store output in log file --(output)--> analysis output
     │
     `──> build-mappings-jar --(output,logfile)--> store output in log file --(output)--> analysis output
    """
    build_integration_jars = linear_flow.Flow('build-integration-jars-flow')
    build_integration_jars.add(ToolsIntegrationBuildJarCode(inject={'settings': settings}))
    build_integration_jars.add(LogTask(name="build-integration-jars-out-log"))
    build_integration_jars.add(OutputAnalysis(name="build-integration-jars-out-analyse"))

    build_perl_libs = linear_flow.Flow('build-perl-libs-flow')
    build_perl_libs.add(ToolsIntegrationBuildPerlLibs(inject={'settings': settings}))
    build_perl_libs.add(LogTask(name="build-perl-libs-out-log"))
    build_perl_libs.add(OutputAnalysis(name="build-perl-libs-out-analyse"))

    build_mapping_jar = linear_flow.Flow('build-mappings-jar-flow')
    build_mapping_jar.add(ToolsMappingsBuildJarCode(inject={'settings': settings}))
    build_mapping_jar.add(LogTask(name="build-mappings-jar-out-log"))
    build_mapping_jar.add(OutputAnalysis(name="build-mappings-jar-out-analyse"))

    build_flow = linear_flow.Flow('code-building-flow')
    build_flow.add(make_git_update_flow())
    build_flow.add(unordered_flow.Flow('unordered-builds').add(
        build_integration_jars,
        build_perl_libs,
        build_mapping_jar))

    return build_flow
