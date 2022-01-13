import os
from argparse import Namespace

import common


class TrackPython(object):
    def get_name(self) -> str:
        return 'python'

    def get_commands(self) -> list[common.Command]:
        return [TestCommand()]

    def get_files(self, args: Namespace) -> list[str]:
        return [common.get_path(args, '{exercise}.py')]

    def get_test_files(self, args: Namespace) -> list[str]:
        return [common.get_path(args, '{exercise}_test.py')]

    def post_download(self, _: Namespace) -> None:
        pass


class TestCommand(object):
    def get_name(self) -> str:
        return 'test'

    def get_help(self) -> str:
        return 'run tests'

    def run(self, args: Namespace) -> None:
        test = common.get_path(args, '{exercise}_test.py')
        os.system(f'python -m pytest {test}')
