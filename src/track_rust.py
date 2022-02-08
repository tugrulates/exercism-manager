"""Operations for the Rust track on Exercism."""

import json
import re
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, MutableMapping

import toml

import common


class RustTrack(object):
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

    def get_files(self, namespace: Namespace) -> list[Path]:
        """Return code files for given solution."""
        return [common.get_path(namespace, 'src/lib.rs'),
                common.get_path(namespace, 'Cargo.toml')]

    def get_test_files(self, namespace: Namespace) -> list[Path]:
        """Return test files for given solution."""
        return [common.get_path(namespace, 'tests/{exercise}.rs')]

    def post_download(self, namespace: Namespace) -> None:
        """Prepate rust workspace for this solution."""
        InitCommand().run(namespace)


class InitCommand(common.Command):
    """Add solution to rust packages and set as active debug target."""

    __PACKAGE_RE = re.compile(r'(?<="--package=)([\w-]+)(?=")')
    __LINTS = ['#![warn(clippy::all)]\n', '#![warn(missing_docs)]\n']

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'init'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 're-initialize exercise'

    def __init_package(self, namespace: Namespace) -> None:
        config_file = common.get_path(namespace, 'Cargo.toml')
        with config_file.open('r') as f:
            config = toml.load(f)
        if config['package']['name'] != namespace.exercise:
            config['package']['name'] = namespace.exercise
            with config_file.open('w') as f:
                toml.dump(config, f)

    def __init_workspace(self, namespace: Namespace) -> None:
        rust_dir = common.get_root() / 'rust'
        dirs = [x for x in rust_dir.iterdir() if x.is_dir()]
        config_file = common.get_root() / 'Cargo.toml'
        config: MutableMapping[str, Any]
        if config_file.exists():
            with config_file.open('r') as f:
                config = toml.load(f)
        config = config or {'workspace': {'members': []}}
        if set(dirs) != set(config.get('workspace', {}).get('members', [])):
            config['workspace']['members'] = [f'rust/{x.name}' for x in dirs]
            with config_file.open('w') as f:
                toml.dump(config, f)

    def __init_launch(self, namespace: Namespace) -> None:
        config_dir = common.get_root() / '.vscode'
        config_file = config_dir / 'launch.json'
        template_file = config_dir / 'launch.json.template'
        with template_file.open('r') as f:
            launch = json.load(f)
        for config in launch.get('configurations'):
            if 'cargo' in config:
                config['cargo'].get('args', []).append(
                    common.fmt('--package={exercise}', namespace))
        with config_file.open('w') as f:
            json.dump(launch, f, indent=4)

    def __init_lints(self, namespace: Namespace) -> None:
        file = common.get_path(namespace, 'src/lib.rs')
        with file.open('r') as f:
            lines = f.readlines()
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
            with file.open('w') as f:
                f.writelines(out_lines)

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
        if self.__support_features:
            if namespace.features:
                args.extend(['--features', namespace.features])
            if namespace.all_features:
                args.extend(['--all-features'])
        args.extend(self.__args)
        subprocess.check_call(['cargo', self.__name] + args)
