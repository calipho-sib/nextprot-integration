#!/usr/bin/python
import argparse

import logging

from nextprot_integration.CodeBuilder import CodeBuilder
from nextprot_integration.JavaPropertyMap import JavaPropertyMap

from nextprot_integration.service.shell import BashService
from nextprot_integration.service.prerequisite import SoftwareCheckr, EnvService
from nextprot_integration.service.pgdb import DatabaseService
from nextprot_integration.service.git import GitService

logging.basicConfig(filename='workflow.log', filemode='w', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

"""
This workflow is composed of multiple tasks. Each task should be run sequentially.
This workflow enable semi-automatic processing as it can interrupt on error, wait for a fix to be done
and resume from where it interrupted.

As such it has a persistent state.


example:

workflow = Workflow()

task = BuildCodeTask()

workflow.nextTask(task)
...
workflow.nextTask(task)

workflow.run()


See also doc/integration/workflow.md
"""


class Tracker:
    """Track the progression of this neXtProt integration
    It should be able to:
     - listens to every executing task
     - create check point last executing task
    """
    def __init__(self, workflow):
        self.__workflow = workflow

    def track(self):
        print ""


class IntegrationWorkflow:

    def __init__(self, dev_mode=False):
        self.__dev_mode = dev_mode
        self.__check_host_system()
        self.__update_all_git_repos()
        self.__load_java_props()
        self.__check_database()

    @staticmethod
    def __check_host_system():
        logging.info("Checking all required softwares")
        SoftwareCheckr.check_all_required_softwares()
        logging.info("Checking all required nextprot environment variables")
        EnvService.check_all_required_nextprot_envs()

    def __update_all_git_repos(self):
        logging.info("Updating all git repositories")
        if self.__dev_mode:
            dev_repos = {EnvService.get_np_perl_parsers_home(): 'didactic_integration',
                         EnvService.get_np_loaders_home(): 'didactic_integration',
                         EnvService.get_np_cv_home(): 'master'}
            git = GitService(registered_repos=dev_repos)
        else:
            git = GitService()

        git.update_all()

    def __check_database(self):
        logging.info("Checking database "+self.__java_props.get_property("database.name"))
        DatabaseService.check_database(self.__java_props.get_property("database.name"))

    def __load_java_props(self):
        self.__java_props = JavaPropertyMap(EnvService.get_np_dataload_prop_filename())
        self.__java_props.add_property("ant.lib.dir", EnvService.get_np_loaders_home()+"/lib")
        self.__java_props.add_property("tools.integration.dir", EnvService.get_np_loaders_home() + "/tools.integration")
        self.__java_props.add_property("tools.mappings.dir", EnvService.get_np_loaders_home() + "/tools.np_mappings")

    def build_code(self):
        logging.info("Building perl scripts, libs and java apps")
        builder = CodeBuilder(self)
        builder.build_integration_perl()
        builder.build_integration_jars()
        builder.build_np_mappings_jar()

    def get_java_property(self, java_property):
        return self.__java_props.get_property(java_property)

    def get_ant_lib_dir(self):
        return self.__java_props.get_property("ant.lib.dir")

    def get_db_name(self):
        return self.__java_props.get_property("database.name")

    def get_db_dump_dir(self):
        return self.__java_props.get_property("database.dump.dir")

    def get_tools_integration_dir(self):
        return self.__java_props.get_property("tools.integration.dir")

    def get_tools_mappings_dir(self):
        return self.__java_props.get_property("tools.mappings.dir")

    def exec_ant_task(self, ant_task_path, ant_task):
        """
        Parameters
        ----------
        ant_task_path : string
            the path where is located build.xml containing the task to run
        ant_task: string
            the ant task name
        """
        return BashService.exec_ant_task(ant_task_path, self.get_ant_lib_dir(), ant_task,
                                         EnvService.get_np_dataload_prop_filename())

    def dump_db_schema(self, db_schema):
        DatabaseService.dump_db(db_name=self.get_db_name(), db_schema=db_schema, dump_dir=self.get_db_dump_dir())

    def update_db_schema(self, update_type):
        DatabaseService.update_db_schema(self, tool_type=update_type)

    def restore_db_schema(self, db_schema, dump_file):
        DatabaseService.restore_db_schema(db_name=self.get_db_name(), db_schema=db_schema, dump_file=dump_file)


def parse_args():

    parser = argparse.ArgumentParser(description='Run neXtProt integration worflow')
    parser.add_argument('-d', '--dev-mode', help='enable dev mode', action='store_true')
    parser.add_argument('-s', '--save-point')
    parser.add_argument('-l', '--load-point')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    workflow = IntegrationWorkflow(dev_mode=args.dev_mode)
    workflow.build_code()

    #workflow.restore_db_schema(db_schema="np_mappings", )
    #workflow.update_db_schema(update_type="integration")
    #workflow.update_db_schema(update_type="mappings")
    #workflow.dump_db_schema(db_schema="nextprot")
    #workflow.dump_db_schema(db_schema="np_mappings")

