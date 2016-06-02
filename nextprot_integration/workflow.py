#!/usr/bin/python
import argparse
import logging

import nextprot_integration.utils.engine_utils as eu  # noqa
import taskflow.engines
from nextprot_integration.flow.buildcode import CodeBuildingFlowFactory
from nextprot_integration.service.jprop import JavaPropertyMap
from nextprot_integration.service.npdb import DatabaseService
from nextprot_integration.service.prerequisite import SoftwareCheckr, EnvService
from taskflow import states
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


def flow_watch(state, details):
    print("Flow '%s' transition to state %s" % (details['flow_name'], state))


def task_watch(state, details):
    print('Task %s => %s' % (details.get('task_name'), state))


FINISHED_STATES = (states.SUCCESS, states.FAILURE, states.REVERTED)


def integration_flow_factory():

    main_flow = linear_flow.Flow('integration-flow')
    main_flow.add(CodeBuildingFlowFactory().create_flow())

    return main_flow


def resume(flowdetail, backend):
    print('Resuming flow %s %s' % (flowdetail.name, flowdetail.uuid))
    e = taskflow.engines.load_from_detail(flow_detail=flowdetail,
                                          backend=backend)
    e.run()


# TODO: needs to be fixed
def run_with_persistence(flow_factory, store):

    with eu.get_backend() as backend:

        print("----------")
        print("Before run")
        print("----------")
        print(backend.pformat())
        print("----------")

        book, flow_detail = eu.create_log_book_and_flow_details(book_name="workflow-integration",
                                                                backend=backend)
        # CREATE AND RUN THE FLOW: FIRST ATTEMPT ####################

        engine = taskflow.engines.load(flow_factory, flow_detail=flow_detail,
                                       book=book, backend=backend, store=store)

        eu.print_task_states(flow_detail, "At the beginning, there is no state")
        eu.print_wrapped("Running")
        engine.run()
        eu.print_task_states(flow_detail, "After running")


def run_with_timing(store):

    engine = taskflow.engines.load(integration_flow_factory(), engine='serial', store=store)
    # This registers all (ANY) state transitions to trigger a call to the
    # flow_watch function for flow state transitions, and registers the
    # same all (ANY) state transitions for task state transitions.
    engine.notifier.register(ANY, flow_watch)
    engine.atom_notifier.register(ANY, task_watch)

    engine.compile()
    engine.prepare()
    # After prepare the storage layer + backend can now be accessed safely...
    backend = engine.storage.backend

    print("----------")
    print("Before run")
    print("----------")
    print(backend.memory.pformat())
    print("----------")

    with timing.PrintingDurationListener(engine):
        print('Running flow %s %s' % (engine.storage.flow_name,
                                      engine.storage.flow_uuid))
        engine.run()

        print("---------")
        print("After run")
        print("---------")
        for path in backend.memory.ls_r(backend.memory.root_path, absolute=True):
            value = backend.memory[path]
            if value:
                print("%s -> %s" % (path, value))
            else:
                print("%s" % path)

if __name__ == '__main__':
    eu.print_wrapped('Running all tasks:')

    run_with_timing(store={'settings': Settings(dev_mode=False)})
    #run_with_persistence(flow_factory=integration_flow_factory(),
                         #store={'settings': Settings(dev_mode=False)})





