#!/usr/bin/env python3

import sys
from argparse import ArgumentError, ArgumentParser, Namespace
from typing import Optional

import common
from common import Command, Track
from track_c import TrackC
from track_python import TrackPython

TRACKS: list[Track] = [TrackC(), TrackPython()]


def parse_track() -> tuple[Namespace, ArgumentParser]:
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--track', choices=[x.get_name() for x in TRACKS])
    args = parser.parse_known_args(sys.argv[1:])[0]
    return args, parser


def parse_args(commands: list[Command]) -> tuple[Namespace, ArgumentParser]:
    parser = ArgumentParser(description='Manage exercism solutions.')
    parser.add_argument('--track', required=True,
                        choices=[x.get_name() for x in TRACKS],
                        help='language track')
    parser.add_argument('--exercise', required=True, help='exercise slug')
    parser.add_argument(
        '--user', help='operate for mentee solutions')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    for command in commands:
        subparsers.add_parser(command.get_name(), help=command.get_help())
    args = parser.parse_args(sys.argv[1:])
    return args, parser


def main() -> None:
    args: Namespace
    parser: ArgumentParser
    args, parser = parse_track()
    commands: list[Command] = common.get_commands()
    module: Optional[Track] = None

    for track in TRACKS:
        if track.get_name() == args.track:
            module = track
    if module:
        commands.extend(module.get_commands())
    args, parser = parse_args(commands)
    args.module = module

    try:
        commands = [x for x in commands if x.get_name() == args.command]
        if not commands:
            raise ArgumentError(
                None, f'Unknown command {args.command} for {args.track} track')
        for command in commands:
            command.run(args)
    except ArgumentError as e:
        print(parser.error(e.message))
        exit(1)


if __name__ == '__main__':
    main()
