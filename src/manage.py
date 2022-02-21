"""Script to orchestrate local Exercism solutions."""

from __future__ import annotations

import sys
from argparse import ArgumentError, ArgumentParser, Namespace
from subprocess import CalledProcessError

from common import Command, DownloadCommand, Track
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
    commands = track.get_commands()
    namespace, parser = parse_args(commands)
    [command] = [x for x in track.get_commands()
                 if x.get_name() == namespace.command]

    try:
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
    parser.add_argument('--track', required=True,
                        choices=[x.get_name() for x in TRACKS],
                        help='language track')
    parser.add_argument('--exercise', required=True, help='exercise slug')
    parser.add_argument('--user', help='operate for mentee solutions')
    subparsers = parser.add_subparsers(
        title='commands', dest='command', required=True)
    for command in commands:
        subparser = subparsers.add_parser(
            command.get_name(), help=command.get_help())
        command.add_arguments(subparser)
    namespace = parser.parse_args(sys.argv[1:])
    return namespace, parser


def parse_track() -> Track:
    """Parse just the track argument.

    :return: (parsed arguments, parser)
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--track', choices=[x.get_name() for x in TRACKS])
    namespace, _ = parser.parse_known_args(sys.argv[1:])
    [track] = [x for x in TRACKS if x.get_name() == namespace.track]
    return track


if __name__ == '__main__':
    main()
