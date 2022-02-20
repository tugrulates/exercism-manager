"""Operations for the Python track on Exercism."""

import subprocess
from argparse import Namespace

import common


class PythonTrack(common.Track):
    """Solutions for the Python track on exercism."""

    def get_name(self) -> str:
        """Return the name of the track."""
        return 'python'

    def get_commands(self) -> list[common.Command]:
        """Return the list of commands specific to this track."""
        return [TestCommand()]

    def post_download(self, _: Namespace) -> None:
        """Prepare solution after download for faster solve."""
        pass


class TestCommand(common.Command):
    """Run tests using pytest."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'test'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'run tests'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        for test in namespace.module.get_test_files(namespace):
            subprocess.check_call(['python', '-m', 'pytest', test])
