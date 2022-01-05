#!/usr/bin/env python3

import argparse
import os
import sys
import importlib


def command_download(module, track):
    def command(exercise):
        if not all(os.path.exists(x) for x in module.files(exercise)):
            os.system(
                f'exercism download --exercise={exercise} --track={track}')
            module.init(exercise)
    return command


def command_open(module):
    def command(exercise):
        os.system('code {}'.format(
            ' '.join(module.files(exercise, include_test_files=True))))
    return command


def command_submit(module):
    def command(exercise):
        os.system('exercism submit {}'.format(
            ' '.join(module.files(exercise))))
    return command


def parse_track():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--track', default='c', choices=['c'])
    args = parser.parse_known_args(sys.argv[1:])[0]
    return args.track


def parse_args(commands):
    parser = argparse.ArgumentParser(description='Manage exercism solutions.')
    parser.add_argument('--track', default='c',
                        choices=['c'], help='language track')
    parser.add_argument('--exercise', required=True, help='exercise slug')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    for command, value in commands.items():
        subparsers.add_parser(command, help=value[0])
    return parser.parse_args(sys.argv[1:])


def main():
    track = parse_track()
    module = importlib.import_module(f'track_{track}')
    commands = {
        'download': ('download exercise and initialize', command_download(module, track)),
        'open':     ('open exercise files in VSCode',    command_open(module)),
        'submit':   ('submit solution to exercism',      command_submit(module)),
    }
    commands.update(module.commands())
    args = parse_args(commands)

    try:
        commands[args.command][1](args.exercise)
    except KeyError as e:
        print(f'Unknown command {e} for {args.track} track')
        exit(1)


if __name__ == '__main__':
    main()
