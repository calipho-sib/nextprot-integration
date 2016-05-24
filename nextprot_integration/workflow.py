#!/usr/bin/python
import argparse
import logging

from nextprot_integration.flow.buildcode import make_build_code_flow
import taskflow.engines
from taskflow.listeners import timing
from taskflow.types import notifier

ANY = notifier.Notifier.ANY

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


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


def make_flow():

    return make_build_code_flow()


if __name__ == '__main__':
    args = parse_args()

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

    #workflow.restore_db_schema(db_schema="np_mappings", )
    #workflow.update_db_schema(update_type="integration")
    #workflow.update_db_schema(update_type="mappings")
    #workflow.dump_db_schema(db_schema="nextprot")
    #workflow.dump_db_schema(db_schema="np_mappings")

