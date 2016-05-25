# coding=utf-8
import shutil
import time

import os
import re
from nextprot_integration.service.git import GitService
from nextprot_integration.service.prerequisite import EnvService
from nextprot_integration.service.shell import BashService
from nextprot_integration.utils.flow_utils import AbstractFlowFactory
from taskflow import task
from taskflow.patterns import linear_flow, unordered_flow


class GitUpdate(task.Task):
    """Update git repository to the latest commit.

    [Note about code from load.xls/uniprot: line 10-13]
    """
    default_provides = ('stdout', 'stderr')

    def execute(self, git_repo_path, settings):
        """Execute this task.
        :param git_repo_path: the git repository to update
        :param settings the workflow settings
        :return: the tuple (stdout, stderr)
        """
        gs = GitService(dev_mode=settings.dev_mode())
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


class ToolsIntegrationBuildJars(task.Task):
    """build and install tools integration jars in proper place

    [Note about code from load.xls/uniprot (line 15-17)]:
      'install-code' target was splitted in:
     - 'install-jars' (this task)
     - 'install-perl' (see ToolsIntegrationBuildPerlLibs)
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_build_path=settings.get_tools_integration_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_target="install-jars",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/install-tools-integration-jars_"+time.strftime("%Y%m%d-%H%M%S")+".log"

    def revert(self, settings, *args, **kwargs):
        file_path = settings.get_jar_repository_path()+"/com.genebio.nextprot.dataloader-jar-with-dependencies.jar"
        print ("remove file "+file_path)
        os.remove(file_path)


class ToolsIntegrationBuildPerlLibs(task.Task):
    """install perl dependencies, build and deploy perl libs found in repo ${np.parser.pl}

    [Note about code from load.xls/uniprot (line 15-17)]:
      'install-code' target was splitted in:
     - 'install-perl' (this task)
     - 'install-jars' (see ToolsIntegrationBuildJars)
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_build_path=settings.get_tools_integration_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_target="install-perl",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/install-tools-perl-libs_"+time.strftime("%Y%m%d-%H%M%S")+".log"

    def revert(self, settings, *args, **kwargs):
        print ("cleaning "+str(EnvService.get_nextprot_perl5_lib()))
        shutil.rmtree(EnvService.get_nextprot_perl5_lib())


class BuildScalaParserJars(task.Task):
    """build scala parser jars

    [Note about code from load.xls/uniprot (line 15,16,19)]

    Side Effect: deploys jars in settings.get_tools_integration_dir()/target:
     - integration-1.0-jar-with-dependencies.jar
     - integration-1.0.jar
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_maven_task(mvn_pom_path=settings.get_tools_integration_dir(),
                                             mvn_goal="package")
        return stdout, settings.get_log_dir()+"/install-scala-parsers_"+time.strftime("%Y%m%d-%H%M%S")+".log"

    def revert(self, settings, *args, **kwargs):
        target_dir = settings.get_tools_integration_dir()+"/target"
        print ("cleaning "+target_dir)
        shutil.rmtree(target_dir)


class ToolsMappingsBuildJar(task.Task):
    """build and install tools mappings jar in proper place

    [Note about code from load.xls/uniprot (line 21,22)]

    Side Effect: deploys jar in EnvService.get_np_loaders_home()/com.genebio.nextprot.genemapping.datamodel/target:
     - com.genebio.nextprot.genemapping.datamodel.jar
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_build_path=settings.get_tools_mappings_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_target="install-jar",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/install-tools-integration-mappings-jar_"+time.strftime("%Y%m%d-%H%M%S")+".log"

    def revert(self, settings, *args, **kwargs):
        target_dir = EnvService.get_np_loaders_home()+"/com.genebio.nextprot.genemapping.datamodel/target"

        print ("cleaning "+target_dir)
        shutil.rmtree(target_dir)


class DbIntegrationUpdate(task.Task):
    """update the integration database structure with DbMaintain

    [Note about code from load.xls/uniprot (line 16,18)]

    Side Effect (non revertible):
    Update tables from scripts in com.genebio.nextprot.datamodel/src/main/resources/dbscripts/
    Update table dbmaintain_scripts by adding a row for each executed script (and execution state: field "succeeded")
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_build_path=settings.get_tools_integration_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_target="db-integration-update",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/db-integration-update_"+time.strftime("%Y%m%d-%H%M%S")+".log"


class DbMappingsUpdate(task.Task):
    """update the mappings database structure with DbMaintain

    [Note about code from load.xls/uniprot (line 21,23)]

    Side Effect (non revertible):
    Update tables from scripts in com.genebio.nextprot.genemapping.datamodel/src/main/resources/dbscripts
    Update table dbmaintain_scripts by adding a row for each executed script (and execution state: field "succeeded")
    """
    default_provides = ('stdout', 'log_file_path')

    def execute(self, settings):
        stdout = BashService.exec_ant_task(ant_build_path=settings.get_tools_mappings_dir(),
                                           ant_lib_path=settings.get_ant_lib_dir(),
                                           ant_target="db-mappings-update",
                                           prop_file=EnvService.get_np_dataload_prop_filename())
        return stdout, settings.get_log_dir()+"/db-mappings-update_"+time.strftime("%Y%m%d-%H%M%S")+".log"


class CodeBuildingFlowFactory(AbstractFlowFactory):

    def create_flow(self):
        """
        update-code-repos
         │
         `──> build-code
         │       │
         │       `──> build-integration-jars --(output,logfile)--> store output in log file --(output)--> analysis output
         │       │
         │       └──> build-perl-libs --(output,logfile)--> store output in log file --(output)--> analysis output
         │       │
         │       `──> build-scala-parser-jars --(output,logfile)--> store output in log file --(output)--> analysis output
         │       │
         │       `──> build-mappings-jar --(output,logfile)--> store output in log file --(output)--> analysis output
         │
         `──> update-dbs
                 │
                 `──> update_db_integration --(output,logfile)--> store output in log file --(output)--> analysis output
                 │
                 `──> update_db_mappings --(output,logfile)--> store output in log file --(output)--> analysis output
        """
        return linear_flow.Flow('code-building-flow').add(
            self._new_git_update_flow(),
            unordered_flow.Flow('code-builds').add(
                self._new_build_integration_jars_flow(),
                self._new_build_perl_libs_flow(),
                self._new_build_scala_parser_jars_flow(),
                self._new_build_mapping_jar_flow()),
            linear_flow.Flow('update-dbs').add(
                self._new_update_db_integration_flow(),
                self._new_update_db_mappings_flow()
            )
        )

    def _new_git_update_flow(self):
        """update repositories nextprot-perl-parsers and nextprot-loaders
        """
        lf = linear_flow.Flow("update-repos")

        for repo_path in [EnvService.get_np_perl_parsers_home(), EnvService.get_np_loaders_home()]:
            lf.add(GitUpdate(name='git-update-%s' % repo_path.rsplit('/', 1)[1],
                             inject={'git_repo_path': repo_path}))
        return lf

    def _new_build_integration_jars_flow(self):

        build_integration_jars = linear_flow.Flow('build-integration-jars-flow')
        build_integration_jars.add(ToolsIntegrationBuildJars())
        build_integration_jars.add(LogTask(name="build-integration-jars-out-log"))
        build_integration_jars.add(OutputAnalysis(name="build-integration-jars-out-analyse"))

        return build_integration_jars

    def _new_build_perl_libs_flow(self):

        build_perl_libs = linear_flow.Flow('build-perl-libs-flow')
        build_perl_libs.add(ToolsIntegrationBuildPerlLibs())
        build_perl_libs.add(LogTask(name="build-perl-libs-out-log"))
        build_perl_libs.add(OutputAnalysis(name="build-perl-libs-out-analyse"))

        return build_perl_libs

    def _new_build_scala_parser_jars_flow(self):

        build_scala_parser_jars = linear_flow.Flow('build-scala-parser-jars-flow')
        build_scala_parser_jars.add(BuildScalaParserJars())
        build_scala_parser_jars.add(LogTask(name="build-scala-parser-jars-out-log"))
        build_scala_parser_jars.add(OutputAnalysis(name="build-scala-parser-jars-out-analyse"))

        return build_scala_parser_jars

    def _new_build_mapping_jar_flow(self):

        build_mapping_jar = linear_flow.Flow('build-mappings-jar-flow')
        build_mapping_jar.add(ToolsMappingsBuildJar())
        build_mapping_jar.add(LogTask(name="build-mappings-jar-out-log"))
        build_mapping_jar.add(OutputAnalysis(name="build-mappings-jar-out-analyse"))

        return build_mapping_jar

    def _new_update_db_integration_flow(self):

        update_db_integration = linear_flow.Flow('update-db-integration-flow')
        update_db_integration.add(DbIntegrationUpdate())
        update_db_integration.add(LogTask(name="update-db-integration-out-log"))
        update_db_integration.add(OutputAnalysis(name="update_db_integration-out-analyse"))

        return update_db_integration

    def _new_update_db_mappings_flow(self):

        update_db_mappings = linear_flow.Flow('update-db-mappings-flow')
        update_db_mappings.add(DbMappingsUpdate())
        update_db_mappings.add(LogTask(name="update-db-mappings-out-log"))
        update_db_mappings.add(OutputAnalysis(name="update-db-mappings-out-analyse"))

        return update_db_mappings

