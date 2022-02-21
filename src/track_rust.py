"""Operations for the Rust track on Exercism."""

import json
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, MutableMapping

import toml

import common
from exercise import Exercise


class RustTrack(common.Track):
    """Solutions for the Rust track on exercism."""

    @property
    def name(self) -> str:
        """Name of the track."""
        return 'rust'

    @property
    def commands(self) -> list[common.Command]:
        """List of commands specific to this track."""
        return [InitCommand(),
                CargoCommand('build'),
                CargoCommand('check'),
                CargoCommand('test', '--', '--include-ignored'),
                CargoCommand('clean', support_features=False),
                CargoCommand('doc', '--open')]

    def get_additional_solution_files(self, exercise: Exercise) -> list[Path]:
        """Return code files for given solution."""
        return [exercise.path / 'Cargo.toml']

    def post_download(self, exercise: Exercise) -> None:
        """Prepate rust workspace for this solution."""
        InitCommand().run(exercise)


class InitCommand(common.Command):
    """Add solution to rust packages and set as active debug target."""

    _LINTS = ['#![warn(clippy::all)]\n', '#![warn(missing_docs)]\n']

    @property
    def name(self) -> str:
        """Name of the command."""
        return 'init'

    def __init_package(self, exercise: Exercise) -> None:
        config_file = exercise.path / 'Cargo.toml'
        with config_file.open('r') as f:
            config = toml.load(f)
        if config['package']['name'] != exercise.name:
            config['package']['name'] = exercise.name
            with config_file.open('w') as f:
                toml.dump(config, f)

    def __init_workspace(self, exercise: Exercise) -> None:
        rust_dir = exercise.root / 'rust'
        dirs = [x for x in rust_dir.iterdir() if x.is_dir()]
        config_file = exercise.root / 'Cargo.toml'
        config: MutableMapping[str, Any]
        if config_file.exists():
            with config_file.open('r') as f:
                config = toml.load(f)
        config = config or {'workspace': {'members': []}}
        if set(dirs) != set(config.get('workspace', {}).get('members', [])):
            config['workspace']['members'] = [f'rust/{x.name}' for x in dirs]
            with config_file.open('w') as f:
                toml.dump(config, f)

    def __init_launch(self, exercise: Exercise) -> None:
        config_dir = exercise.root / '.vscode'
        config_file = config_dir / 'launch.json'
        template_file = config_dir / 'launch.json.template'
        with template_file.open('r') as f:
            launch = json.load(f)
        for config in launch.get('configurations'):
            if 'cargo' in config:
                config['cargo'].get('args', []).append(
                    f'--package={exercise.name}')
        with config_file.open('w') as f:
            json.dump(launch, f, indent=4)

    def __init_lints(self, exercise: Exercise) -> None:
        file = exercise.find_file('src/*.rs')
        with file.open('r') as f:
            lines = f.readlines()
        lints = [x for x in InitCommand._LINTS if x not in lines]
        has_crate_doc = any(x for i, x in enumerate(lines)
                            if x.startswith('//! ') and
                            lines[i+1:i+2] == ['\n'])
        out_lines = []
        if not has_crate_doc:
            out_lines.append(
                f'//! Solve {exercise.name} on Exercism.\n')
            out_lines.append('\n')
        if lints:
            out_lines.extend(lints)
            out_lines.append('\n')
        out_lines.extend(lines)
        if lines != out_lines:
            with file.open('w') as f:
                f.writelines(out_lines)

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        self.__init_package(exercise)
        self.__init_workspace(exercise)
        self.__init_launch(exercise)
        self.__init_lints(exercise)


class CargoCommand(common.Command):
    """Run a cargo command."""

    def __init__(self, name: str, *args: str, support_features: bool = True):
        """Create make command.

        :param name: name of the cargo command
        :param args: extra arguments for cargo
        :param support_features: allow feature management
        """
        self._name = name
        self._args = args
        self._support_features = support_features

    @property
    def name(self) -> str:
        """Name of the command."""
        return self._name

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add supported cargo arguments."""
        if self._support_features:
            parser.add_argument(
                '--features',
                help='space or comma separated list of features to enable')
            parser.add_argument('--all-features', default=False,
                                action='store_true',
                                help='enable all features')

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        # Set the current exercise a default.
        InitCommand().run(exercise)
        args = ['--package', exercise.name]
        if self._support_features:
            if exercise.namespace.features:
                args.extend(['--features', exercise.namespace.features])
            if exercise.namespace.all_features:
                args.extend(['--all-features'])
        args.extend(self._args)
        subprocess.check_call(['cargo', self.name] + args)
