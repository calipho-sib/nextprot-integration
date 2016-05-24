#!/usr/bin/python
import argparse
import logging

from nextprot_integration.flow.buildcode import make_build_code_flow
from nextprot_integration.service.jprop import JavaPropertyMap
from nextprot_integration.service.pgdb import DatabaseService
from nextprot_integration.service.prerequisite import SoftwareCheckr, EnvService
import taskflow.engines
from taskflow.listeners import timing
from taskflow.patterns import linear_flow
from taskflow.types import notifier

ANY = notifier.Notifier.ANY

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class Settings(object):

    def __init__(self, dev_mode=False):
        self.__dev_mode = dev_mode
        self.__check_host_system()
        self.__load_java_props()
        self.__check_database()
        self.__dev_mode = dev_mode

    @staticmethod
    def __check_host_system():
        logging.info("Checking all required softwares")
        SoftwareCheckr.check_all_required_softwares()
        logging.info("Checking all required nextprot environment variables")
        EnvService.check_all_required_nextprot_envs()

    def __check_database(self):
        logging.info("Checking database "+self.__java_props.get_property("database.name"))
        DatabaseService.check_database(self.__java_props.get_property("database.name"))

    def dev_mode(self):
        return self.__dev_mode

    def __load_java_props(self):
        self.__java_props = JavaPropertyMap(EnvService.get_np_dataload_prop_filename())
        self.__java_props.add_property("ant.lib.dir", EnvService.get_np_loaders_home()+"/lib")
        self.__java_props.add_property("tools.integration.dir", EnvService.get_np_loaders_home() + "/tools.integration")
        self.__java_props.add_property("tools.mappings.dir", EnvService.get_np_loaders_home() + "/tools.np_mappings")

    def get_java_property(self, java_property):
        return self.__java_props.get_property(java_property)

    def get_log_dir(self):
        return self.__java_props.get_property("log.dir")

    def get_jar_repository_path(self):
        return self.__java_props.get_property("jar.repository.path")

    def get_perl_install_path(self):
        return self.__java_props.get_property("perl.install.dir")

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


def parse_args():

    parser = argparse.ArgumentParser(description='Run neXtProt integration worflow')
    parser.add_argument('-d', '--dev-mode', help='enable dev mode', action='store_true')
    parser.add_argument('-s', '--save-point')
    parser.add_argument('-l', '--load-point')

    return parser.parse_args()


def print_wrapped(text):
    print("-" * (len(text)))
    print(text)
    print("-" * (len(text)))


def flow_watch(state, details):
    print("Flow '%s' transition to state %s" % (details['flow_name'], state))


def task_watch(state, details):
    print('Task %s => %s' % (details.get('task_name'), state))


def make_main_flow():

    main_flow = linear_flow.Flow('integration-flow')
    # load.xls/uniprot: building jars and perl libs
    main_flow.add(make_build_code_flow(Settings(dev_mode=False)))

    return main_flow


if __name__ == '__main__':
    args = parse_args()

    print_wrapped('Running all tasks:')

    mf = make_main_flow()

    e = taskflow.engines.load(mf, engine='serial')
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

    #workflow.restore_db_schema(db_schema="np_mappings", )
    #workflow.update_db_schema(update_type="integration")
    #workflow.update_db_schema(update_type="mappings")
    #workflow.dump_db_schema(db_schema="nextprot")
    #workflow.dump_db_schema(db_schema="np_mappings")

