"""Operations for the Rust track on Exercism."""

import os
import re
from argparse import Namespace

import common


class TrackRust(object):
    """Solutions for the Rust track on exercism."""

    def get_name(self) -> str:
        """Return the name of the track."""
        return 'rust'

    def get_commands(self) -> list[common.Command]:
        """Return the list of commands specific to this track."""
        return [InitCommand(),
                CargoCommand('build'),
                CargoCommand('check'),
                CargoCommand('test'),
                CargoCommand('clean'),
                CargoCommand('doc', '--open')]

    def get_files(self, namespace: Namespace) -> list[str]:
        """Return code files for given solution."""
        return [common.get_path(namespace, 'src/lib.rs')]

    def get_test_files(self, namespace: Namespace) -> list[str]:
        """Return test files for given solution."""
        ...
        return [common.get_path(namespace, 'tests/{exercise}.rs')]

    def post_download(self, namespace: Namespace) -> None:
        """Prepate rust workspace for this solution."""
        InitCommand().run(namespace)


class InitCommand(object):
    """Add solution to rust packages and set as active debug target."""

    __PACKAGE_RE = re.compile(r'(?<="--package=)([\w-]+)(?=")')

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'init'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 're-initialize exercise'

    def __init_workspace(self, namespace: Namespace) -> None:
        rust_dir = common.get_path(namespace, '..')
        dirs = os.listdir(rust_dir)
        dirs = [x for x in dirs if os.path.isdir(os.path.join(rust_dir, x))]
        dirs = sorted(dirs)
        with open(os.path.join(rust_dir, '..', 'Cargo.toml'), 'w') as out:
            out.write('[workspace]\n\n')
            out.write('members = [\n')
            for exercise in dirs:
                out.write(f'    "rust/{exercise}",\n')
            out.write(']\n')

    def __init_launch(self, namespace: Namespace) -> None:
        launch = common.get_path(
            namespace, '..', '..', '.vscode', 'launch.json')
        with open(launch, 'r') as inp:
            content = inp.read()
        content = re.sub(InitCommand.__PACKAGE_RE, namespace.exercise, content)
        with open(launch, 'w') as out:
            out.write(content)

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        self.__init_workspace(namespace)
        self.__init_launch(namespace)


class CargoCommand(object):
    """Run a cargo command."""

    def __init__(self, name: str, *args: str):
        """Create make command.

        :param name: name of the cargo command
        :param args: extra arguments
        """
        self.__name = name
        self.__args = args

    def get_name(self) -> str:
        """Return the name of the command."""
        return self.__name

    def get_help(self) -> str:
        """Return help text for the command."""
        return f'run {self.__name}'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        InitCommand().run(namespace)
        args = ' '.join(self.__args)
        os.system(common.fmt(
            f'cargo {self.__name} -p={{exercise}} {args}', namespace))
