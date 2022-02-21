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
        return [InitCommand(), TestCommand()]

    def post_download(self, exercise: Exercise) -> None:
        """Prepare solution for for niceties."""
        InitCommand().run(exercise)


class InitCommand(common.Command):
    """Add docstring to solution file."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return 'init'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        for file in exercise.solution_files:
            with file.open('r') as f:
                lines = f.readlines()
            if lines and not lines[0].startswith('"""'):
                lines.insert(0, f'"""Solve {exercise.name} on Exercism."""\n')
                lines.insert(1, '\n')
                with file.open('w') as f:
                    f.writelines(lines)


class TestCommand(common.Command):
    """Run tests using pytest."""

    @ property
    def name(self) -> str:
        """Return the name of the command."""
        return 'test'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        for test in exercise.test_files:
            subprocess.check_call(['python', '-m', 'pytest', test])
