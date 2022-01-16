"""Operations for the Rust track on Exercism."""

import os
import re
from argparse import ArgumentParser, Namespace

import toml

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
                CargoCommand('test', '--', '--include-ignored'),
                CargoCommand('clean', support_features=False),
                CargoCommand('doc', '--open')]

    def get_files(self, namespace: Namespace) -> list[str]:
        """Return code files for given solution."""
        return [common.get_path(namespace, 'src/lib.rs')]

    def get_test_files(self, namespace: Namespace) -> list[str]:
        """Return test files for given solution."""
        return [common.get_path(namespace, 'tests/{exercise}.rs')]

    def post_download(self, namespace: Namespace) -> None:
        """Prepate rust workspace for this solution."""
        InitCommand().run(namespace)


class InitCommand(common.Command):
    """Add solution to rust packages and set as active debug target."""

    __PACKAGE_RE = re.compile(r'(?<="--package=)([\w-]+)(?=")')
    __LINTS = ['#![warn(clippy::all)]\n', '#![deny(missing_docs)]\n']

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'init'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 're-initialize exercise'

    def __init_package(self, namespace: Namespace) -> None:
        config_file = common.get_path(namespace, 'Cargo.toml')
        with open(config_file, 'r') as inp:
            config = toml.load(inp)
        if config['package']['name'] != namespace.exercise:
            config['package']['name'] = namespace.exercise
            with open(config_file, 'w') as out:
                toml.dump(config, out)

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

    def __init_lints(self, namespace: Namespace) -> None:
        file = common.get_path(namespace, 'src/lib.rs')
        with open(file, 'r') as inp:
            lines = inp.readlines()
        lints = [x for x in InitCommand.__LINTS if x not in lines]
        has_crate_doc = any(x for i, x in enumerate(lines)
                            if x.startswith('//! ') and
                            lines[i+1:i+2] == ['\n'])
        out_lines = []
        if not has_crate_doc:
            out_lines.append(common.fmt(
                '//! Solve {exercise} on Exercism.\n', namespace))
            out_lines.append('\n')
        if lints:
            out_lines.extend(lints)
            out_lines.append('\n')
        out_lines.extend(lines)
        if lines != out_lines:
            with open(file, 'w') as out:
                out.writelines(out_lines)

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        self.__init_package(namespace)
        self.__init_workspace(namespace)
        self.__init_launch(namespace)
        self.__init_lints(namespace)


class CargoCommand(common.Command):
    """Run a cargo command."""

    def __init__(self, name: str, *args: str, support_features: bool = True):
        """Create make command.

        :param name: name of the cargo command
        :param args: extra arguments for cargo
        :param support_features: allow feature management
        """
        self.__name = name
        self.__args = args
        self.__support_features = support_features

    def get_name(self) -> str:
        """Return the name of the command."""
        return self.__name

    def get_help(self) -> str:
        """Return help text for the command."""
        return f'run {self.__name}'

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add supported cargo arguments."""
        if self.__support_features:
            parser.add_argument(
                '--features',
                help='space or comma separated list of features to enable')
            parser.add_argument('--all-features', default=False,
                                action='store_true',
                                help='enable all features')

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        InitCommand().run(namespace)
        args = ['--package', namespace.exercise]
        if namespace.features:
            args.extend(['--features', namespace.features])
        if namespace.all_features:
            args.extend(['--all-features'])
        args.extend(self.__args)
        args_str = ' '.join(args)
        os.system(f'cargo {self.__name} {args_str}')
