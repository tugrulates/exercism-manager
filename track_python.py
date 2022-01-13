import os
from argparse import Namespace

import common


class TrackPython(object):
    def get_name(self) -> str:
        return 'python'

    def get_commands(self) -> list[common.Command]:
        return [TestCommand()]

    def get_files(self, namespace: Namespace) -> list[str]:
        return [common.get_path(namespace, '{exercise}.py')]

    def get_test_files(self, namespace: Namespace) -> list[str]:
        return [common.get_path(namespace, '{exercise}_test.py')]

    def post_download(self, _: Namespace) -> None:
        pass


class TestCommand(object):
    def get_name(self) -> str:
        return 'test'

    def get_help(self) -> str:
        return 'run tests'

    def run(self, namespace: Namespace) -> None:
        test = common.get_path(namespace, '{exercise}_test.py')
        os.system(f'python -m pytest {test}')
