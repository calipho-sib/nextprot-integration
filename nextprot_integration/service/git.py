import os
import logging
import re
from shell import BashService
from prerequisite import EnvService


class GitService:
    """
    This class checks and update git repositories
    """
    def __init__(self, registered_repos=None):
        if registered_repos is None:
            self.__repos = {EnvService.get_np_perl_parsers_home(): 'master',
                            EnvService.get_np_loaders_home(): 'develop',
                            EnvService.get_np_cv_home(): 'master'}
        else:
            self.__repos = registered_repos

        # check directory path
        for path in self.__repos.keys():
            if not os.path.exists(path):
                raise OSError(path + " does not exist")

    def update(self, repo_path, branch=None):
        """Update the specified git repository"""
        if repo_path not in self.__repos:
            raise ValueError("'"+repo_path + "' is not registered")

        GitService.check_repository(repo_path)
        co_mess = self.checkout(repo_path, branch)
        logging.info(co_mess.rstrip())

        if not co_mess.startswith("Your branch is up-to-date with"):
            gp_err_mess = BashService.exec_bash("git pull").stderr
            if gp_err_mess:
                raise ValueError(gp_err_mess.rstrip())

    def update_all(self):
        """Update all registered git repositories"""
        # Check that the following git repositories are up-to-date and clean
        for repo in self.__repos.keys():
            self.update(repo)

    def checkout(self, repo_path, branch=None):
        """git checkout the specified repository to the given branch"""
        if repo_path not in self.__repos:
            raise ValueError("'"+repo_path + "' is not registered")

        if branch is None:
            branch = self.__repos[repo_path]

        os.chdir(repo_path)
        return BashService.exec_bash("git checkout " + branch).stdout

    @staticmethod
    def check_repository(repo_path):
        """Check that the git repository is clean"""
        os.chdir(repo_path)
        mess = "git repository " + repo_path + " [working branch " + GitService.get_working_branch(repo_path) + "]"

        # TODO: change with command "git status -su no" (do not show untracked file)
        shell_result = BashService.exec_bash("git status -s")
        if shell_result.stdout:
            status_list = filter(None, shell_result.stdout.split("\n"))

            for status in status_list:
                code, filename = re.split(r'\s+', status)
                if code != '??':
                    raise ValueError(mess + " is not clean: file='" + filename + "', status='" + code+"'")
                else:
                    logging.warn(mess + " untracked file: '" + filename + "'.")
        logging.info(mess + " is clean.")

    @staticmethod
    def get_working_branch(repo_path):
        os.chdir(repo_path)
        return BashService.exec_bash("git rev-parse --abbrev-ref HEAD").stdout.rstrip()
