import logging

from nextprot_integration.JavaPropertyMap import JavaPropertyMap

from nextprot_integration.service.prerequisite import SoftwareCheckr, EnvService
from nextprot_integration.service.pgdb import DatabaseService


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
