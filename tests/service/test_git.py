from unittest import TestCase

from nextprot_integration.service.git import GitService
from nextprot_integration.service.prerequisite import EnvService


class TestGitService(TestCase):

    def test_check_repo(self):
        GitService.check_repository(EnvService.get_np_perl_parsers_home())

    def test_check_unknown_repo(self):
        """should raise OSError: [Errno 2] No such file or directory: 'myrepo'
        """
        with self.assertRaises(OSError):
            GitService.check_repository("myrepo")

    def test_checkout(self):
        git = GitService()
        repo = EnvService.get_np_loaders_home()
        shell_return = git.checkout(repo, "develop")
        self.assertEqual("Your branch is up-to-date with 'origin/develop'.", shell_return.stdout)
        self.assertEqual("develop", GitService.get_working_branch(repo))
        git.checkout(repo, "didactic_integration")

    def test_update(self):
        repo = EnvService.get_np_loaders_home()
        git = GitService()
        shell_return = git.update(repo, "develop")
        self.assertEqual("Your branch is up-to-date with 'origin/develop'.", shell_return.stdout)
        self.assertEqual("develop", GitService.get_working_branch(repo))
        git.checkout(repo, "didactic_integration")

    def test_unregistered_repo(self):
        git = GitService()
        with self.assertRaises(ValueError):
            git.checkout("myrepo", "mybranch")
