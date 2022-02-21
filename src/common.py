"""Common operations for all tracks on Exercism."""

from __future__ import annotations

import abc
import subprocess
from argparse import ArgumentError, ArgumentParser
from pathlib import Path

from exercise import Exercise


class Track(metaclass=abc.ABCMeta):
    """All solutions for an Exercism track."""

    @abc.abstractmethod
    def get_name(self) -> str:
        """Return the name of the track."""

    def get_commands(self) -> list[Command]:
        """Return the list of all commands available for exercises."""
        return [VisitCommand(), DownloadCommand(),
                OpenCommand(), SubmitCommand()]

    def get_additional_solution_files(self, exercise: Exercise) -> list[Path]:
        """Return the list of commands specific to this track."""
        return []

    def post_download(self, exercise: Exercise) -> None:
        """Prepare solution after download for faster solve."""
        pass


class Command(metaclass=abc.ABCMeta):
    """Script command for a single operation."""

    @abc.abstractmethod
    def get_name(self) -> str:
        """Return the name of the command."""

    @abc.abstractmethod
    def get_help(self) -> str:
        """Return help text for the command."""

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command specific arguments to the parser."""
        pass

    def needs_download(self) -> bool:
        """Return whether the exercise is needed locally."""
        return True

    @abc.abstractmethod
    def run(self, exercise: Exercise) -> None:
        """Run the command."""


class VisitCommand(Command):
    """Visit the url of solution on browser."""

    __URL = 'https://exercism.org/tracks/{track}/exercises/{exercise}'

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'visit'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'open the exercise page on browser'

    def needs_download(self) -> bool:
        """Return whether the exercise is needed locally."""
        return False

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        if not exercise.is_downloaded():
            if exercise.get_user():
                raise ArgumentError(
                    None, 'download a user solution before visiting')
        else:
            url = exercise.fmt(VisitCommand.__URL)
        subprocess.check_call(['python', '-m', 'webbrowser', url])


class DownloadCommand(Command):
    """Download solution from exercism."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'download'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'download exercise and initialize'

    def needs_download(self) -> bool:
        """Return whether the exercise is needed locally."""
        return False

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        if exercise.get_user():
            raise ArgumentError(
                None, 'download user solutions through command line instead')
        exercise.download()


class OpenCommand(Command):
    """Open all code and test files on IDE."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'open'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'open exercise files in VSCode'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        files = (exercise.get_solution_files() + exercise.get_test_files())
        subprocess.check_call(['code'] + [str(x) for x in files])


class SubmitCommand(Command):
    """Submit solution files to exercism."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'submit'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'submit solution to exercism'

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        if exercise.get_user:
            raise ArgumentError(
                None, 'submitting user solutions is not allowed')
        files = exercise.get_solution_files()
        subprocess.check_call(['exercism', 'submit'] + [str(x) for x in files])
