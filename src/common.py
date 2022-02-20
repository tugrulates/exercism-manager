"""Common operations for all tracks on Exercism."""

import abc
import json
import subprocess
import sys
from argparse import ArgumentError, ArgumentParser, Namespace
from functools import reduce
from pathlib import Path
from typing import Any, Mapping


class Command(metaclass=abc.ABCMeta):
    """Script command for a single operation."""

    @abc.abstractmethod
    def get_name(self) -> str:
        """Return the name of the command."""

    @abc.abstractmethod
    def get_help(self) -> str:
        """Return help text for the command."""

    @abc.abstractmethod
    def run(self, namespace: Namespace) -> None:
        """Run the command.

        :param namespace: parsed arguments
        """

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command specific arguments to the parser."""
        pass


class Track(metaclass=abc.ABCMeta):
    """All solutions for an Exercism track."""

    @abc.abstractmethod
    def get_name(self) -> str:
        """Return the name of the track."""

    @abc.abstractmethod
    def get_commands(self) -> list[Command]:
        """Return the list of commands specific to this track."""

    def get_solution_files(self, namespace: Namespace) -> list[Path]:
        """Return code files for given solution.

        :param namespace: parsed arguments
        """
        files = get_config(namespace, 'config.json', ['files', 'solution'])
        return [get_path(namespace, x) for x in files]

    def find_solution_file(self, namespace: Namespace, pattern: str) -> Path:
        """Find specific exercise file with the given pattern.

        :param namespace: parsed arguments
        :param pattern: glob pattern for the desired file
        """
        files = [x for x in self.get_solution_files(namespace)
                 if x.match(pattern)]
        assert files, f'no file matching "{pattern}" exists for exercise'
        assert len(files) == 1, f'multiple file matching "{pattern}": {files}'
        return files[0]

    def get_test_files(self, namespace: Namespace) -> list[Path]:
        """Return test files for given solution.

        :param namespace: parsed arguments
        """
        files = get_config(namespace, 'config.json', ['files', 'test'])
        return [get_path(namespace, x) for x in files]

    @ abc.abstractmethod
    def post_download(self, namespace: Namespace) -> None:
        """Prepare solution after download for faster solve.

        :param namespace: parsed arguments
        """


def fmt(s: str, namespace: Namespace) -> str:
    """Format string using parsed arguments.

    A special template called `{exercise_}` is accepted. This converts dash
    characters into underscore in `namespace.exercise`.

    :param namespace: parsed arguments

    :example:

    >>> args = Namespace(track='rust', exercise='bu-st')
    >>> fmt('{track} to {exercise}', args)
    'rust to bu-st'
    >>> fmt('{track} to {exercise_}', args)
    'rust to bu_st'
    """
    mapping = vars(namespace).copy()
    mapping['exercise_'] = namespace.exercise.replace('-', '_')
    return s.format(**mapping)


def get_commands() -> list[Command]:
    """Return commands common to all tracks."""
    return [VisitCommand(), DownloadCommand(), OpenCommand(), SubmitCommand()]


def get_path(namespace: Namespace, path: str = '.') -> Path:
    """Return exercise file from given path template.

    :param namespace: parsed arguments
    :param path: path with possible namespace templates
    """
    return Path(get_root(),
                (Path('users') / namespace.user) if namespace.user else '.',
                namespace.track, namespace.exercise, fmt(path, namespace))


def get_root() -> Path:
    """Return the manager root."""
    return Path(sys.argv[0]).parent.parent


def get_config(namespace: Namespace, config_file: str,
               keys: list[str]) -> Any:
    """Return Exercism config for solution, or None if not found.

    :param namespace: parsed arguments
    :param config_file: json file name for the config
    :param keys: list of keys to recursively lookup config
    """
    path = get_path(namespace, '.exercism') / config_file
    if not path.exists():
        return None
    with path.open() as f:
        def lookup(c: Any, k: Any) -> Any:
            return c.get(k, None) if isinstance(c, Mapping) else None
        config = json.load(f)
        return list(reduce(lookup, keys, config))


class VisitCommand(Command):
    """Visit the url of solution on browser."""

    __URL = 'https://exercism.org/tracks/{track}/exercises/{exercise}'

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'visit'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'open the exercise page on browser'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        url = get_config(namespace, 'metadata.json', ['url'])
        if not url:
            if namespace.user:
                raise ArgumentError(
                    None, 'download a user solution before visiting')
            url = fmt(VisitCommand.__URL, namespace)
        subprocess.check_call(['python', '-m', 'webbrowser', url])


class DownloadCommand(Command):
    """Download solution from exercism."""

    __CMD = ['exercism', 'download',
             '--exercise={exercise}', '--track={track}']

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'download'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'download exercise and initialize'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        if namespace.user:
            raise ArgumentError(
                None, 'download user solutions through command line instead')
        module = namespace.module
        files = namespace.module.get_solution_files(namespace)
        if not files or not all(x.exists() for x in files):
            subprocess.check_call([fmt(x, namespace)
                                  for x in DownloadCommand.__CMD])
            module.post_download(namespace)


class OpenCommand(Command):
    """Open all code and test files on IDE."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'open'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'open exercise files in VSCode'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        files = (namespace.module.get_solution_files(namespace) +
                 namespace.module.get_test_files(namespace))
        subprocess.check_call(['code'] + files)


class SubmitCommand(Command):
    """Submit solution files to exercism."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'submit'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'submit solution to exercism'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        if namespace.user:
            raise ArgumentError(
                None, 'submitting user solutions is not allowed')
        files = namespace.module.get_solution_files(namespace)
        subprocess.check_call(['exercism', 'submit'] + files)
