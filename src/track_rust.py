"""Operations for the Rust track on Exercism."""

import os
from argparse import Namespace

import common


class TrackRust(object):
    """Solutions for the Rust track on exercism."""

    def get_name(self) -> str:
        """Return the name of the track."""
        return 'rust'

    def get_commands(self) -> list[common.Command]:
        """Return the list of commands specific to this track."""
        return [CargoCommand('build'),
                CargoCommand('check'),
                CargoCommand('test'),
                CargoCommand('clean')]

    def get_files(self, namespace: Namespace) -> list[str]:
        """Return code files for given solution."""
        return [common.get_path(namespace, 'src/lib.rs')]

    def get_test_files(self, namespace: Namespace) -> list[str]:
        """Return test files for given solution."""
        ...
        return [common.get_path(namespace, 'tests/{exercise}.rs')]

    def post_download(self, _: Namespace) -> None:
        """Prepare solution after download for faster solve."""
        pass


class CargoCommand(object):
    """Run a cargo command."""

    def __init__(self, name: str):
        """Create make command.

        :param name: name of the cargo command
        """
        self.__name = name

    def get_name(self) -> str:
        """Return the name of the command."""
        return self.__name

    def get_help(self) -> str:
        """Return help text for the command."""
        return f'run {self.__name}'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        os.chdir(common.get_path(namespace))
        os.system(f'cargo {self.__name}')
