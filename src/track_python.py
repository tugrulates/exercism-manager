"""Operations for the Python track on Exercism."""

import os
from argparse import Namespace

import common


class TrackPython(object):
    """Solutions for the Python track on exercism."""

    def get_name(self) -> str:
        """Return the name of the track."""
        return 'python'

    def get_commands(self) -> list[common.Command]:
        """Return the list of commands specific to this track."""
        return [TestCommand()]

    def get_files(self, namespace: Namespace) -> list[str]:
        """Return code files for given solution."""
        return [common.get_path(namespace, '{exercise_}.py')]

    def get_test_files(self, namespace: Namespace) -> list[str]:
        """Return test files for given solution."""
        return [common.get_path(namespace, '{exercise_}_test.py')]

    def post_download(self, _: Namespace) -> None:
        """Prepare solution after download for faster solve."""
        pass


class TestCommand(object):
    """Run tests using pytest."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'test'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'run tests'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        test = common.get_path(namespace, '{exercise_}_test.py')
        os.system(f'python -m pytest {test}')
