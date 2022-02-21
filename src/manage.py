"""Script to orchestrate local Exercism solutions."""

from __future__ import annotations

import inspect
import sys
from argparse import ArgumentError, ArgumentParser, Namespace
from subprocess import CalledProcessError
from typing import Any, Optional

from common import Command, DownloadCommand, Track, get_default_commands
from exercise import Exercise
from track_c import CTrack
from track_python import PythonTrack
from track_rust import RustTrack

TRACKS = [CTrack(), PythonTrack(), RustTrack()]


def main() -> None:
    """Run script with given arguments."""
    namespace: Namespace
    parser: ArgumentParser
    track = parse_track()
    commands = get_default_commands() + (track.commands if track else [])
    namespace, parser = parse_args(commands)
    [command] = [x for x in commands if x.name == namespace.command]

    try:
        assert track
        exercise = Exercise(track, namespace)
        if command.needs_download() and not exercise.is_downloaded():
            DownloadCommand().run(exercise)
        command.run(exercise)
    except ArgumentError as e:
        parser.error(e.message)
    except CalledProcessError:
        exit(1)


def parse_args(commands: list[Command]) -> tuple[Namespace, ArgumentParser]:
    """Parse all command line arguments.

    :param commands: commands to serve through the command line
    :return: (parsed arguments, parser)
    """
    parser = ArgumentParser(description='Manage Exercism solutions.')
    parser.add_argument('-t', '--track', required=True,
                        choices=[x.name for x in TRACKS],
                        help='language track')
    parser.add_argument('-e', '--exercise', required=True,
                        help='exercise slug')
    parser.add_argument('-u', '--user', help='operate for mentee solutions')
    subparsers = parser.add_subparsers(
        title='commands', dest='command', required=True)
    for command in commands:
        subparser = subparsers.add_parser(command.name, help=get_help(command))
        command.add_arguments(subparser)
    namespace = parser.parse_args(sys.argv[1:])
    return namespace, parser


def parse_track() -> Optional[Track]:
    """Parse just the track argument.

    :return: (parsed arguments, parser)
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-t', '--track', choices=[x.name for x in TRACKS])
    namespace, _ = parser.parse_known_args(sys.argv[1:])
    if namespace.track:
        [track] = [x for x in TRACKS if x.name == namespace.track]
        return track
    return None


def get_help(obj: Any) -> Optional[str]:
    """Generate command line help from docstring of object."""
    docstring = inspect.getdoc(obj)
    if not docstring:
        return None
    return ''.join(docstring.splitlines()[:1]).strip().rstrip('.').lower()


if __name__ == '__main__':
    main()
