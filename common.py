"""Common operations for all tracks on Exercism."""

import json
import os
import sys
from argparse import ArgumentError, Namespace
from typing import Mapping, Protocol


class Command(Protocol):
    """Script command for a single operation."""

    def get_name(self) -> str:
        """Return the name of the command."""
        ...

    def get_help(self) -> str:
        """Return help text for the command."""
        ...

    def run(self, namespace: Namespace) -> None:
        """Run the command.

        :param namespace: parsed arguments
        """
        ...


class Track(Protocol):
    """All solutions for an Exercism track."""

    def get_name(self) -> str:
        """Return the name of the track."""
        ...

    def get_commands(self) -> list[Command]:
        """Return the list of commands specific to this track."""
        ...

    def get_files(self, namespace: Namespace) -> list[str]:
        """Return code files for given solution.

        :param namespace: parsed arguments
        """
        ...

    def get_test_files(self, namespace: Namespace) -> list[str]:
        """Return test files for given solution.

        :param namespace: parsed arguments
        """
        ...

    def post_download(self, namespace: Namespace) -> None:
        """Prepare solution after download for faster solve.

        :param namespace: parsed arguments
        """
        ...


def fmt(s: str, namespace: Namespace) -> str:
    """Format string using parsed arguments.

    :param namespace: parsed arguments

    :example:

    >>> args = Namespace(track='rust', exercise='bust')
    >>> fmt('{track} to {exercise}', args)
    'rust to bust'
    """
    return s.format(**vars(namespace))


def get_commands() -> list[Command]:
    """Return commands common to all tracks."""
    return [VisitCommand(), DownloadCommand(), OpenCommand(), SubmitCommand()]


def get_path(namespace: Namespace, *path: str) -> str:
    """Return file given path with templates.

    :param namespace: parsed arguments
    :param path: path segments with possible argument templates
    """
    abs_path = [os.path.dirname(sys.argv[0])]
    if namespace.user:
        abs_path.extend(['users', namespace.user])
    abs_path.extend([namespace.track, namespace.exercise])
    replacements = vars(namespace).copy()
    replacements['exercise'] = namespace.exercise.replace('-', '_')
    abs_path.extend(x.format(**replacements) for x in path)
    return os.path.join(*abs_path)


def get_metadata(namespace: Namespace) -> Mapping[str, object]:
    """Return Exercism metadata config for solution.

    :param namespace: parsed arguments
    """
    metadata_file = get_path(namespace, '.exercism', 'metadata.json')
    if not os.path.exists(metadata_file):
        return {}
    with open(metadata_file, 'r') as inp:
        return dict(json.load(inp))


class VisitCommand(object):
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
        metadata = get_metadata(namespace)
        if metadata:
            url = '{url}'.format(**metadata)
        else:
            if namespace.user:
                raise ArgumentError(
                    None, 'download a user solution before visiting')
            url = fmt(VisitCommand.__URL, namespace)
        os.system(f'python3 -m webbrowser "{url}"')


class DownloadCommand(object):
    """Download solution from exercism."""

    __CMD = 'exercism download --exercise={exercise}  --track={track}'

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
        if not all(os.path.exists(x) for x in module.get_files(namespace)):
            os.system(fmt(DownloadCommand.__CMD, namespace))
            module.post_download(namespace)


class OpenCommand(object):
    """Open all code and test files on IDE."""

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'open'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 'open exercise files in VSCode'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        files = namespace.module.get_files(
            namespace) + namespace.module.get_test_files(namespace)
        files = ' '.join(files)
        os.system(f'code {files}')


class SubmitCommand(object):
    """Submit solution files to exercism."""

    __CMD = 'exercism submit {files}'

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
        files = namespace.module.get_files(namespace)
        files = ' '.join(files)
        os.system(SubmitCommand.__CMD.format(files=files))
