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

    def get_name(self) -> str:
        """Return the name of the track."""
        return 'rust'

    def get_commands(self) -> list[common.Command]:
        """Return the list of commands specific to this track."""
        return super().get_commands() + [
            InitCommand(),
            CargoCommand('build'),
            CargoCommand('check'),
            CargoCommand('test', '--', '--include-ignored'),
            CargoCommand('clean', support_features=False),
            CargoCommand('doc', '--open')]

    def get_additional_solution_files(self, exercise: Exercise) -> list[Path]:
        """Return code files for given solution."""
        return [exercise.get_path('Cargo.toml')]

    def post_download(self, exercise: Exercise) -> None:
        """Prepate rust workspace for this solution."""
        InitCommand().run(exercise)


class InitCommand(common.Command):
    """Add solution to rust packages and set as active debug target."""

    __LINTS = ['#![warn(clippy::all)]\n', '#![warn(missing_docs)]\n']

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'init'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 're-initialize exercise'

    def __init_package(self, exercise: Exercise) -> None:
        config_file = exercise.get_path('Cargo.toml')
        with config_file.open('r') as f:
            config = toml.load(f)
        if config['package']['name'] != exercise.get_name():
            config['package']['name'] = exercise.get_name()
            with config_file.open('w') as f:
                toml.dump(config, f)

    def __init_workspace(self, exercise: Exercise) -> None:
        rust_dir = exercise.get_root() / 'rust'
        dirs = [x for x in rust_dir.iterdir() if x.is_dir()]
        config_file = exercise.get_root() / 'Cargo.toml'
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
        config_dir = exercise.get_root() / '.vscode'
        config_file = config_dir / 'launch.json'
        template_file = config_dir / 'launch.json.template'
        with template_file.open('r') as f:
            launch = json.load(f)
        for config in launch.get('configurations'):
            if 'cargo' in config:
                config['cargo'].get('args', []).append(
                    exercise.fmt('--package={exercise}'))
        with config_file.open('w') as f:
            json.dump(launch, f, indent=4)

    def __init_lints(self, exercise: Exercise) -> None:
        file = exercise.find_solution_file('src/*.rs')
        with file.open('r') as f:
            lines = f.readlines()
        lints = [x for x in InitCommand.__LINTS if x not in lines]
        has_crate_doc = any(x for i, x in enumerate(lines)
                            if x.startswith('//! ') and
                            lines[i+1:i+2] == ['\n'])
        out_lines = []
        if not has_crate_doc:
            out_lines.append(exercise.fmt(
                '//! Solve {exercise} on Exercism.\n'))
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

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        # Set the current exercise a default.
        InitCommand().run(exercise)
        args = ['--package', exercise.get_name()]
        if self.__support_features:
            if exercise._namespace.features:
                args.extend(['--features', exercise._namespace.features])
            if exercise._namespace.all_features:
                args.extend(['--all-features'])
        args.extend(self.__args)
        subprocess.check_call(['cargo', self.__name] + args)
