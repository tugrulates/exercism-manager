#!/usr/bin/env python3
"""Script to orchestrate local Exercism solutions."""

import sys
from argparse import ArgumentError, ArgumentParser, Namespace
from typing import Optional

import common
from common import Command, Track
from track_c import TrackC
from track_python import TrackPython

TRACKS: list[Track] = [TrackC(), TrackPython()]


def parse_track() -> tuple[Namespace, ArgumentParser]:
    """Parse just the track argument.

    :return: (parsed arguments, parser)
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--track', choices=[x.get_name() for x in TRACKS])
    namespace, _ = parser.parse_known_args(sys.argv[1:])
    return namespace, parser


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
    parser.add_argument(
        '--user', help='operate for mentee solutions')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    for command in commands:
        subparsers.add_parser(command.get_name(), help=command.get_help())
    namespace, _ = parser.parse_args(sys.argv[1:])
    return namespace, parser


def main() -> None:
    """Run script with given arguments."""
    namespace: Namespace
    parser: ArgumentParser
    namespace, parser = parse_track()
    commands: list[Command] = common.get_commands()
    module: Optional[Track] = None

    for track in TRACKS:
        if track.get_name() == namespace.track:
            module = track
    if module:
        commands.extend(module.get_commands())
    namespace, parser = parse_args(commands)
    namespace.module = module

    try:
        commands = [x for x in commands if x.get_name() == namespace.command]
        if not commands:
            raise ArgumentError(
                None, common.fmt(
                    'Unknown command {command} for {track} track', namespace))
        for command in commands:
            command.run(namespace)
    except ArgumentError as e:
        parser.error(e.message)


if __name__ == '__main__':
    main()
