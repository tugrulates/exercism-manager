"""Operations for the Python track on Exercism."""

import subprocess

import common
from exercise import Exercise


class PythonTrack(common.Track):
    """Solutions for the Python track on exercism."""

    @property
    def name(self) -> str:
        """Name of the track."""
        return 'python'

    @property
    def commands(self) -> list[common.Command]:
        """List of commands specific to this track."""
        return [TestCommand()]


class TestCommand(common.Command):
    """Run tests using pytest."""

    @property
    def name(self) -> str:
        """Return the name of the command."""
        return 'test'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        for test in exercise.test_files:
            subprocess.check_call(['python', '-m', 'pytest', test])
