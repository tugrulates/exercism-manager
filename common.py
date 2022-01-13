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

    def run(self, namespace: Namespace) -> None:
        ...


class Track(Protocol):
    def get_name(self) -> str:
        ...

    def get_commands(self) -> list[Command]:
        ...

    def get_files(self, namespace: Namespace) -> list[str]:
        ...

    def get_test_files(self, namespace: Namespace) -> list[str]:
        ...

    def post_download(self, namespace: Namespace) -> None:
        ...


def fmt(s: str, namespace: Namespace) -> str:
    return s.format(**vars(namespace))


def get_commands() -> list[Command]:
    return [VisitCommand(), DownloadCommand(), OpenCommand(), SubmitCommand()]


def get_path(namespace: Namespace, *path: str) -> str:
    abs_path = [os.path.dirname(sys.argv[0])]
    if namespace.user:
        abs_path.extend(['users', namespace.user])
    abs_path.extend([namespace.track, namespace.exercise])
    replacements = vars(namespace).copy()
    replacements['exercise'] = namespace.exercise.replace('-', '_')
    abs_path.extend(x.format(**replacements) for x in path)
    return os.path.join(*abs_path)


def get_metadata(namespace: Namespace) -> Mapping[str, object]:
    metadata_file = get_path(namespace, '.exercism', 'metadata.json')
    if not os.path.exists(metadata_file):
        return {}
    with open(metadata_file, 'r') as inp:
        return dict(json.load(inp))


class VisitCommand(object):
    __URL = 'https: // exercism.org/tracks/{track}/exercises/{exercise}'

    def get_name(self) -> str:
        return 'visit'

    def get_help(self) -> str:
        return 'open the exercise page on browser'

    def run(self, namespace: Namespace) -> None:
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
    __CMD = 'exercism download --exercise={exercise}  --track={track}'

    def get_name(self) -> str:
        return 'download'

    def get_help(self) -> str:
        return 'download exercise and initialize'

    def run(self, namespace: Namespace) -> None:
        if namespace.user:
            raise ArgumentError(
                None, 'download user solutions through command line instead')
        module = namespace.module
        if not all(os.path.exists(x) for x in module.get_files(namespace)):
            os.system(fmt(DownloadCommand.__CMD, namespace))
            module.post_download(namespace)


class OpenCommand(object):
    def get_name(self) -> str:
        return 'open'

    def get_help(self) -> str:
        return 'open exercise files in VSCode'

    def run(self, namespace: Namespace) -> None:
        files = namespace.module.get_files(
            namespace) + namespace.module.get_test_files(namespace)
        files = ' '.join(files)
        os.system(f'code {files}')


class SubmitCommand(object):
    __CMD = 'exercism submit {files}'

    def get_name(self) -> str:
        return 'submit'

    def get_help(self) -> str:
        return 'submit solution to exercism'

    def run(self, namespace: Namespace) -> None:
        if namespace.user:
            raise ArgumentError(
                None, 'submitting user solutions is not allowed')
        files = namespace.module.get_files(namespace)
        files = ' '.join(files)
        os.system(SubmitCommand.__CMD.format(files=files))
