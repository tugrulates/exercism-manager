#!/usr/bin/env python3

import argparse
import importlib
import json
import os
import sys

SITE = 'https://exercism.org'
TRACKS = {'c', 'python'}


def command_visit(args):
    metadata = get_metadata(args)
    if metadata:
        url = '{url}'.format(**metadata)
    else:
        if args.user:
            raise argparse.ArgumentError(
                None, 'download a user solution before visiting')
        url = f'{SITE}/tracks/{args.track}/exercises/{args.exercise}'
    os.system(f'python3 -m webbrowser "{url}"')


def command_download(args):
    if args.user:
        raise argparse.ArgumentError(
            None, 'download user solutions through command line instead')
    module = get_module(args)
    if not all(os.path.exists(x) for x in module.get_files(args)):
        os.system('exercism download ' +
                  f'--exercise={args.exercise} --track={args.track}')
        module.init(args.exercise)


def command_open(args):
    module = get_module(args)
    os.system('code {}'.format(
        ' '.join(module.get_files(args, include_test_files=True))))


def command_submit(args):
    if args.user:
        raise argparse.ArgumentError(
            None, 'submitting user solutions is not allowed')
    module = get_module(args)
    os.system('exercism submit {}'.format(
        ' '.join(module.get_files(args))))


def get_module(args):
    if args.track:
        return importlib.import_module(f'track_{args.track}')
    return None


def get_path(args, *path):
    abs_path = [os.path.dirname(sys.argv[0])]
    if args.user:
        abs_path.extend(['users', args.user])
    abs_path.extend([args.track, args.exercise])
    abs_path.extend(
        [x.format(exercise=args.exercise.replace('-', '_'),
                  track=args.track) for x in path])
    return os.path.join(*abs_path)


def get_metadata(args):
    metadata_file = get_path(args, '.exercism', 'metadata.json')
    if not os.path.exists(metadata_file):
        return None
    with open(metadata_file, 'r') as input:
        return json.load(input)


def parse_track():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--track', choices=TRACKS)
    args = parser.parse_known_args(sys.argv[1:])[0]
    return args, parser


def parse_args(commands):
    parser = argparse.ArgumentParser(description='Manage exercism solutions.')
    parser.add_argument('--track', required=True,
                        choices=TRACKS, help='language track')
    parser.add_argument('--exercise', required=True, help='exercise slug')
    parser.add_argument(
        '--user', help='operate for mentee solutions')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    for command, value in commands.items():
        subparsers.add_parser(command, help=value[0])
    args = parser.parse_args(sys.argv[1:])
    return args, parser


def main():
    args, parser = parse_track()
    commands = {
        'visit':    ('open the exercise page on browser', command_visit),
        'download': ('download exercise and initialize',  command_download),
        'open':     ('open exercise files in VSCode',     command_open),
        'submit':   ('submit solution to exercism',       command_submit),
    }
    module = get_module(args)
    if module:
        commands.update(module.commands())
    args, parser = parse_args(commands)

    try:
        try:
            command = commands[args.command][1]
        except KeyError as e:
            print(f'Unknown command {e} for {args.track} track')
            exit(1)
        command(args)
    except argparse.ArgumentError as e:
        print(parser.error(e.message))
        exit(1)


if __name__ == '__main__':
    main()
