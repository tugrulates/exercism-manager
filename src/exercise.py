"""Common operations for all tracks on Exercism."""

from __future__ import annotations

import json
import subprocess
from argparse import Namespace
from functools import reduce
from pathlib import Path
from typing import Any, Mapping, Optional

import common


class Exercise:
    """Exercise object."""

    def __init__(self, track: common.Track, namespace: Namespace):
        """Create new object."""
        self._track = track
        self._namespace = namespace

        self._name: str = namespace.exercise
        self._user: str = namespace.user

        self._root = Path(subprocess.check_output(
            ['exercism', 'workspace'], text=True).strip())
        self._path = (self._root /
                      Path('users') / self._user if self._user else '' /
                      Path(track.get_name()) / self._name)

    def fmt(self, s: str) -> str:
        """Format string using parsed arguments.

        :example:

        >>> args = Namespace(track='rust', exercise='bob')
        >>> exercise = Exercise(args)
        >>> exercise.fmt('{track} to {exercise}')
        'rust to bob'
        """
        mapping = vars(self._namespace).copy()
        return s.format(**mapping)

    def get_name(self) -> str:
        """Return the slug of the exercise."""
        return self._name

    def get_solution_files(self) -> list[Path]:
        """Return code files for given solution."""
        files = self._get_config('config.json', ['files', 'solution'])
        return ([self.get_path(x) for x in files] +
                self._track.get_additional_solution_files(self))

    def find_solution_file(self, pattern: str) -> Path:
        """Find specific exercise file with the given pattern.

        :param pattern: glob pattern for the desired file
        """
        files = [x for x in self.get_solution_files()
                 if x.match(pattern)]
        assert files, f'no file matching "{pattern}" exists for exercise'
        assert len(files) == 1, f'multiple file matching "{pattern}": {files}'
        return files[0]

    def get_test_files(self) -> list[Path]:
        """Return test files for given solution."""
        files = self._get_config('config.json', ['files', 'test'])
        return [self.get_path(x) for x in files]

    def get_path(self, path: str = '.') -> Path:
        """Return exercise file from given path template.

        :param path: path with possible namespace templates
        """
        return self._path / self.fmt(path)

    def get_user(self) -> Optional[str]:
        """Return the user of the exercise if different from current user."""
        return self._user

    def get_root(self) -> Path:
        """Return the manager root."""
        return self._root

    def _get_config(self, config_file: str,
                    keys: list[str]) -> Any:
        """Return Exercism config for solution, or None if not found.

        :param config_file: json file name for the config
        :param keys: list of keys to recursively lookup config
        """
        path = self.get_path('.exercism') / config_file
        if not path.exists():
            return None
        with path.open() as f:
            def lookup(c: Any, k: Any) -> Any:
                return c.get(k, None) if isinstance(c, Mapping) else None
            config = json.load(f)
            return list(reduce(lookup, keys, config))

    def is_downloaded(self) -> bool:
        """Return whether the exercise is downloaded."""
        return self._get_config('metadata.json', ['exercise']) is not None

    def download(self) -> None:
        """Download the exercise."""
        assert not self._user
        if not (self.get_path().exists() and
                all(x.exists() for x in self.get_solution_files())):
            subprocess.check_call(['exercism', 'download',
                                   self.fmt('--exercise={exercise}'),
                                   self.fmt('--track={track}')])
        self.post_download()

    def post_download(self) -> None:
        """Prepare solution after download for faster solve."""
        self._track.post_download(self)
