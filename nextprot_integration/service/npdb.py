import os
import psycopg2
import logging

from nextprot_integration.service.prerequisite import EnvService
from shell import BashService


class DatabaseService:
    """
    This class checks host environment for databases existence
    """
    def __init__(self):
        pass

    @staticmethod
    def check_database(db_name):
        """Check that local database 'db_name' exists
        raise an OSError if db does not exist or is not connectable"""
        logging.info("check database "+db_name)
        try:
            conn = psycopg2.connect("dbname='" + db_name + "' user='postgres' host='localhost' password='postgres'")
            conn.close()
        except Exception as error:
            raise ValueError("unable to connect to database '" + db_name+"', message=" + str(error.message))

    @staticmethod
    def vacuum_verbose_analyze(db_name):
        logging.info("clean/analyze database np_annot_uat")
        DatabaseService.exec_query(db_name, "vacuum verbose analyze;")

    @staticmethod
    def dump_db(db_name, db_schema, dump_dir):
        """Dumps database db_name to directory dump_dir
        Parameters
        ----------
        db_name : string
            the db name.
        db_schema: string
            the db schema
        dump_dir: string
            the directory to copy the dump file
        """
        logging.info("dump " + db_name + "." + db_schema + " schema")

        if not os.path.isdir(dump_dir):
            BashService.exec_bash("mkdir -p " + dump_dir)

        command = "pg_dump -U postgres -Fc --schema " + db_schema \
                  + " -f " + dump_dir+"/"+db_schema+"."+db_name+"_$(date "+"+%Y%m%d"+")-$(hostname).dump.gz " \
                  + db_name
        shell_result = BashService.exec_bash(command)
        if shell_result.has_error():
            raise ValueError("unable to dump database '" + db_name + "." + db_schema + "': " + shell_result.stderr +
                             " (command: '" + command + "')")

    @staticmethod
    def restore_db_schema(db_name, db_schema, dump_file):
        """Restores database schema db_name.db_schema from a dump archive

        Parameters
        ----------
        db_name : string
            the db name
        db_schema: string
            the db schema to restore
        dump_file: string
            the db dump file
        """
        schema_name = db_name + "." + db_schema
        logging.info("restore " + schema_name + " schema")

        if not os.path.isfile(dump_file):
            raise ValueError("unable to restore database schema '" + schema_name +
                             "' from unexisted archive " + dump_file)

        command = "pg_restore -U postgres -Fc --clean --exit-on-error --verbose --dbname " + db_name + \
                  " --schema " + db_schema + " " + dump_file

        shell_result = BashService.exec_bash(command)
        if shell_result.has_error():
            raise ValueError("unable to restore database schema '" + schema_name + "': " + shell_result.stderr)

    @staticmethod
    def update_db_schema(workflow, tool_type):

        if tool_type == "integration":
            # cd /work/projects/integration/nextprot-loaders/tools.integration
            # ant -lib lib/ -propertyfile $PROP_FILE db-integration-update
            path = workflow.get_tools_integration_dir()
        elif tool_type == "mappings":
            # cd /work/projects/integration/nextprot-loaders/tools.np_mappings
            # ant -lib lib/ -propertyfile $PROP_FILE db-mappings-update
            path = workflow.get_tools_mappings_dir()
        else:
            raise ValueError("unable db update tool type: '" + tool_type+"'")

        os.chdir(path)
        workflow.exec_ant_task(path, 'db-'+tool_type+'-update')

    @staticmethod
    def exec_query(db_name, command):

        # Connect to an existing database
        conn = psycopg2.connect("dbname='" + db_name + "' user='postgres' host='localhost' password='postgres'")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute(command)
        results = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return results


class Database(object):

    def __init__(self, db_name, password, dump_dir, host="localhost"):
        self.db_name = db_name
        self.password = password
        self.host = host
        self.dump_dir = dump_dir
        self.dumps_by_schema = {}

        if not os.path.isdir(dump_dir):
            os.makedirs(dump_dir)

    def check_connection(self):
        """Check that local database 'db_name' exists
        raise an OSError if db does not exist or is not connectable"""
        try:
            conn = psycopg2.connect("dbname='" + self.db_name + "' user='postgres' host='" +
                                    self.host + "' password='" + self.password + "'")
            conn.close()
        except Exception as error:
            raise ValueError("unable to connect to database '" + self.db_name+"', message=" + str(error.message))

    def dump(self, db_schema):
        """Dumps database db_name.db_schema to directory dump_dir and register in memory/pickle in disk ?
        db_schema: string
            the db schema
        """
        dump_file = self.dump_dir+"/"+db_schema+"."+self.db_name + "_$(date " + "+%Y%m%d" + ")-$(hostname).dump.gz"

        command = "pg_dump -U postgres -Fc --schema " + db_schema + " -f " + dump_file + self.db_name
        shell_result = BashService.exec_bash(command)
        if shell_result.has_error():
            raise ValueError("unable to dump database '" + self.db_name + "." + db_schema + "': " + shell_result.stderr)

        if db_schema not in self.dumps_by_schema:
            self.dumps_by_schema[db_schema] = []
        self.dumps_by_schema[db_schema].push(dump_file)

    def restore_previous_dump(self, db_schema):
        """Restores database schema db_name.db_schema from a dump archive
        db_schema: string
            the db schema to restore
        """
        schema_name = self.db_name + "." + db_schema

        if db_schema not in self.dumps_by_schema or len(self.dumps_by_schema[db_schema]) == 0:
            raise ValueError("no dump file found for schema '" + schema_name)

        dump_file = self.dumps_by_schema[db_schema].pop()

        command = "pg_restore -U postgres -Fc --clean --exit-on-error --verbose --dbname " + self.db_name + \
                  " --schema " + db_schema + " " + dump_file

        shell_result = BashService.exec_bash(command)
        if shell_result.has_error():
            raise ValueError("unable to restore database schema '" + schema_name + "': " + shell_result.stderr)


# TODO!!!!!!!!!!!!!!!!!!!!! Gives real implementations for any of the methods
class DatabaseBackup(object):
    """Responsible to save current snapshot or last_release and restore the last snapshot
    """

    def __init__(self, settings):

        self.__prepare_fs()

    def __prepare_fs(self):
        """Make directories to store npdb data snapshots and last release
        """

        if not os.path.isdir(EnvService.get_npdb_data()):
            raise ValueError("missing nextprot database location")

        # mkdir the following dirs if missing
        EnvService.get_npdb_last_snapshot_data()
        EnvService.get_npdb_initial_snapshot_data()

    def is_postgresql_running(self, pgdata):
        """
        :return: True if server is running else False
        """
        pass

    def start_postgresql(self):
        """Start PostgreSQL server on current snapshot
        """
        if not self.is_postgresql_running(pgdata=EnvService.get_npdb_data()):
            # pg_ctl -D pgdata start
            pass

    def stop_postgresql(self, pgdata_list):
        """Stop PostgreSQL server
        :param pgdatalist
        """
        for pgdata in pgdata_list:
            if self.is_postgresql_running(pgdata=pgdata):
                # pg_ctl -D pgdata stop --silent --mode fast or immediate
                pass

    def _prepare_first_backup(self):

        self.backup_initial_snapshot()
        self.restore_last_snapshot()

    def backup_initial_snapshot(self):
        """Backup the actual np data as initial snapshot
        """
        self.stop_postgresql(pgdata_list=[EnvService.get_npdb_data(), EnvService.get_npdb_initial_snapshot_data()])

        # rsync --archive --update --verbose EnvService.get_npdb_data() EnvService.get_npdb_initial_snapshot_data()

    def backup_current_snapshot(self):
        """Backup the current snapshot as last snapshot
        """
        self.stop_postgresql(pgdata_list=[EnvService.get_npdb_data(), EnvService.get_npdb_last_snapshot_data()])

        # rsync --delete --archive --update --verbose EnvService.get_npdb_data() EnvService.get_npdb_last_snapshot_data()
        self.start_postgresql()

    def restore_last_snapshot(self):
        """Restore the latest snapshot into current
        """
        self.stop_postgresql(pgdata_list=[EnvService.get_npdb_data(), EnvService.get_npdb_last_snapshot_data()])

        # rsync --delete --archive --update --verbose EnvService.get_npdb_last_snapshot_data() EnvService.get_npdb_data()
        self.start_postgresql()