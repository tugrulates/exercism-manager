
import json
import os
import sys
from argparse import ArgumentError, Namespace
from typing import Mapping, Protocol


class Command(Protocol):
    def get_name(self) -> str:
        ...

    def get_help(self) -> str:
        ...

    def run(self, args: Namespace) -> None:
        ...


class Track(Protocol):
    def get_name(self) -> str:
        ...

    def get_commands(self) -> list[Command]:
        ...

    def get_files(self, args: Namespace) -> list[str]:
        ...

    def get_test_files(self, args: Namespace) -> list[str]:
        ...

    def post_download(self, args: Namespace) -> None:
        ...


def get_commands() -> list[Command]:
    return [VisitCommand(), DownloadCommand(), OpenCommand(), SubmitCommand()]


def get_path(args: Namespace, *path: str) -> str:
    abs_path = [os.path.dirname(sys.argv[0])]
    if args.user:
        abs_path.extend(['users', args.user])
    abs_path.extend([args.track, args.exercise])
    abs_path.extend(
        [x.format(exercise=args.exercise.replace('-', '_'),
                  track=args.track) for x in path])
    return os.path.join(*abs_path)


def get_metadata(args: Namespace) -> Mapping[str, object]:
    metadata_file = get_path(args, '.exercism', 'metadata.json')
    if not os.path.exists(metadata_file):
        return {}
    with open(metadata_file, 'r') as input:
        return dict(json.load(input))


class VisitCommand(object):
    def get_name(self) -> str:
        return 'visit'

    def get_help(self) -> str:
        return 'open the exercise page on browser'

    def run(self, args: Namespace) -> None:
        metadata = get_metadata(args)
        if metadata:
            url = '{url}'.format(**metadata)
        else:
            if args.user:
                raise ArgumentError(
                    None, 'download a user solution before visiting')
            url = ('https://exercism.org/tracks/' +
                   f'{args.track}/exercises/{args.exercise}')
        os.system(f'python3 -m webbrowser "{url}"')


class DownloadCommand(object):
    def get_name(self) -> str:
        return 'download'

    def get_help(self) -> str:
        return 'download exercise and initialize'

    def run(self, args: Namespace) -> None:
        if args.user:
            raise ArgumentError(
                None, 'download user solutions through command line instead')
        if not all(os.path.exists(x) for x in args.module.get_files(args)):
            os.system('exercism download ' +
                      f'--exercise={args.exercise} --track={args.track}')
            args.module.post_download(args)


class OpenCommand(object):
    def get_name(self) -> str:
        return 'open'

    def get_help(self) -> str:
        return 'open exercise files in VSCode'

    def run(self, args: Namespace) -> None:
        files = args.module.get_files(args) + args.module.get_test_files(args)
        files = ' '.join(files)
        os.system(f'code {files}')


class SubmitCommand(object):
    def get_name(self) -> str:
        return 'submit'

    def get_help(self) -> str:
        return 'submit solution to exercism'

    def run(self, args: Namespace) -> None:
        if args.user:
            raise ArgumentError(
                None, 'submitting user solutions is not allowed')
        os.system('exercism submit {}'.format(
            ' '.join(args.module.get_files(args))))
