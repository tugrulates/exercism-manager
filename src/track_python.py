"""Operations for the Python track on Exercism."""

import subprocess

import common
from exercise import Exercise


class PythonTrack(common.Track):
    """Solutions for the Python track on exercism."""

    def get_name(self) -> str:
        """Return the name of the track."""
        return 'python'

    def get_commands(self) -> list[common.Command]:
        """Return the list of commands specific to this track."""
        return super().get_commands() + [TestCommand()]


class TestCommand(common.Command):
    """Run tests using pytest."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'test'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'run tests'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        for test in exercise.get_test_files():
            subprocess.check_call(['python', '-m', 'pytest', test])
