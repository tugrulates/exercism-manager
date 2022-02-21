"""Common operations for all tracks on Exercism."""

from __future__ import annotations

import abc
import subprocess
from argparse import ArgumentError, ArgumentParser
from pathlib import Path

from exercise import Exercise


def get_default_commands() -> list[Command]:
    """Return list of commands common to all tracks."""
    return [OpenCommand(),
            DownloadCommand(),
            InfoCommand(),
            CodeCommand(),
            SubmitCommand()]


class Track(metaclass=abc.ABCMeta):
    """All solutions for an Exercism track."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the track."""

    @property
    @abc.abstractmethod
    def commands(self) -> list[Command]:
        """List of commands for this track."""

    def get_additional_solution_files(self, exercise: Exercise) -> list[Path]:
        """Return extra code files for an exercise solution."""
        return []

    def post_download(self, exercise: Exercise) -> None:
        """Prepare solution after download for faster solve."""
        pass

    def __str__(self) -> str:
        """Name of track."""
        return self.name


class Command(metaclass=abc.ABCMeta):
    """Script command for a single operation."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the command."""

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command specific arguments to the parser."""
        pass

    def needs_download(self) -> bool:
        """Return whether the exercise is needed locally."""
        return True

    @abc.abstractmethod
    def run(self, exercise: Exercise) -> None:
        """Run the command."""

    def __str__(self) -> str:
        """Name of command."""
        return self.name


class OpenCommand(Command):
    """Visit the url of solution on browser."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return 'visit'

    def needs_download(self) -> bool:
        """Return whether the exercise is needed locally."""
        return False

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        if exercise.user and not exercise.is_downloaded():
            raise ArgumentError(
                None, 'download a user solution before visiting')
        subprocess.check_call(['python', '-m', 'webbrowser', exercise.url])


class DownloadCommand(Command):
    """Download solution from exercism."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return 'download'

    def needs_download(self) -> bool:
        """Return whether the exercise is needed locally."""
        return False

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        if exercise.user:
            raise ArgumentError(
                None, 'download user solutions through exercism CLI instead')
        exercise.download()


class InfoCommand(Command):
    """Print information about the exercise."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return 'info'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        solution_files = [str(x.relative_to(exercise.path))
                          for x in exercise.solution_files]
        test_files = [str(x.relative_to(exercise.path))
                      for x in exercise.test_files]
        lines = [f'track:          {exercise.track}',
                 f'exercise:       {exercise.name}',
                 f'blurb:          {exercise.blurb}',
                 f'user:           {exercise.user}' if exercise.user else None,
                 f'path:           {exercise.path}',
                 f'url:            {exercise.url}',
                 f'solution files: {solution_files}',
                 f'test files:     {test_files}']
        print('\n'.join(filter(None, lines)))


class CodeCommand(Command):
    """Open all code and test files on IDE."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return 'open'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        files = exercise.solution_files + exercise.test_files
        subprocess.check_call(['code'] + [str(x) for x in files])


class SubmitCommand(Command):
    """Submit solution files to exercism."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return 'submit'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        if exercise.user:
            raise ArgumentError(
                None, 'submitting user solutions is not allowed')
        files = exercise.solution_files
        subprocess.check_call(['exercism', 'submit'] + [str(x) for x in files])
