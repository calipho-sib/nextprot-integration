import os
import subprocess

import logging


class ShellResult(object):

    def __init__(self):
        super(ShellResult, self).__init__()
        self.__stdout = None
        self.__stderr = None
        self.__return_code = None

    @property
    def stdout(self):
        return self.__stdout

    @stdout.setter
    def stdout(self, stdout):
        self.__stdout = (stdout.rstrip() if len(stdout) > 0 else None)

    @property
    def stderr(self):
        return self.__stderr

    @stderr.setter
    def stderr(self, stderr):
        self.__stderr = (stderr.rstrip() if len(stderr) > 0 else None)

    @property
    def return_code(self):
        return self.__return_code

    @return_code.setter
    def return_code(self, return_code):
        self.__return_code = return_code

    def has_error(self):
        return self.return_code != 0 and self.stdout is None

    def __repr__(self):
        return "return_code="+str(self.return_code)+", stdout=" + str(self.stdout)+", stderr="+str(self.stderr)


class BashService:
    """utilitary methods to help around bash command execution
    """
    # TODO: remove this HACK !!!!
    # HACK: while setting virtualenv, PATH was modified losing my current profile settings
    os.environ["PATH"] += os.pathsep + "/Users/fnikitin/Applications/apache-ant-1.9.7/bin"
    os.environ["PATH"] += os.pathsep + "/Users/fnikitin/Applications/apache-maven-3.2.3/bin"
    os.environ["PATH"] += os.pathsep + "/Applications/Postgres.app/Contents/MacOS/bin"

    def __init__(self):
        pass

    @staticmethod
    def exec_bash(bash_command, swap_output_error=False):
        logging.info("exec " + os.path.expandvars(bash_command))

        # Note about explicit shell invocation:
        # Invoking the shell does allow us to expand environment variables and file globs according to the
        # shell's usual mechanism. It is platform-dependent but it is not a problem as this script will be
        # executed on unix machines
        process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        shell_return = ShellResult()
        shell_return.return_code = process.returncode

        if not swap_output_error:
            shell_return.stdout = out
            shell_return.stderr = err
        else:
            shell_return.stdout = err
            shell_return.stderr = out

        return shell_return

    @staticmethod
    def exec_ant_task(ant_task_path, ant_lib_path, ant_task, prop_file):
        """Execute ant task located at specified path
        """
        if not os.path.isdir(ant_task_path):
            raise ValueError("cannot find directory '" + ant_task_path+"'")

        logging.info("cd "+ant_task_path)
        os.chdir(ant_task_path)

        command = "ant -lib " + ant_lib_path+" -propertyfile " + prop_file + " " + ant_task
        shell_result = BashService.exec_bash(command)

        if shell_result.has_error():
            logging.error(command + ": " + shell_result.stdout)
            raise ValueError(command + " failure: " + shell_result.stderr)
        else:
            logging.info(command + " success: " + shell_result.stdout)

        return shell_result.stdout
