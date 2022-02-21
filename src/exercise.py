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

    @property
    def name(self) -> str:
        """Return the slug of the exercise."""
        name: str = self.namespace.exercise
        return name

    @property
    def track(self) -> common.Track:
        """Track of the exercise."""
        return self._track

    @property
    def blurb(self) -> str:
        """Exercism solutions root."""
        blurb: str = self._get_config('config.json', ['blurb'])
        return blurb

    @property
    def user(self) -> Optional[str]:
        """User of the exercise if different from current user."""
        user: str = self.namespace.user
        return user

    @property
    def solution_files(self) -> list[Path]:
        """Code files for given solution."""
        files = self._get_config('config.json', ['files', 'solution'])
        return ([self.path / x for x in files] +
                self._track.get_additional_solution_files(self))

    @property
    def test_files(self) -> list[Path]:
        """Test files for given solution."""
        files = self._get_config('config.json', ['files', 'test'])
        return [self.path / x for x in files]

    @property
    def path(self) -> Path:
        """Exercise directory."""
        return (self.root /
                (Path('users') / self.user if self.user else '') /
                Path(self._track.get_name()) / self.name)

    @property
    def root(self) -> Path:
        """Exercism solutions root."""
        return Path(subprocess.check_output(
            ['exercism', 'workspace'], text=True).strip())

    @property
    def url(self) -> str:
        """Exercism solutions root."""
        url: str = self._get_config('metadata.json', ['url'])
        if url:
            return url
        assert not self.user
        return ('https://exercism.org'
                f'/tracks/{self.track}/exercises/{self.name}')

    @property
    def namespace(self) -> Namespace:
        """User supplied arguments."""
        return self._namespace

    def __str__(self) -> str:
        """Name of exercise."""
        return self.name

    def find_file(self, pattern: str) -> Path:
        """Find specific exercise file with the given pattern.

        :param pattern: glob pattern for the desired file
        """
        files = [x for x in self.solution_files if x.match(pattern)]
        assert files, f'no file matching "{pattern}" exists for exercise'
        assert len(files) == 1, f'multiple file matching "{pattern}": {files}'
        return files[0]

    def _get_config(self, config_file: str, keys: list[str]) -> Any:
        """Return Exercism config for solution, or None if not found.

        :param config_file: json file name for the config
        :param keys: list of keys to recursively lookup config
        """
        path = self.path / '.exercism' / config_file
        if not path.exists():
            return None
        with path.open() as f:
            def lookup(c: Any, k: Any) -> Any:
                return c.get(k, None) if isinstance(c, Mapping) else None
            config = json.load(f)
            return reduce(lookup, keys, config)

    def is_downloaded(self) -> bool:
        """Return whether the exercise is downloaded."""
        return self._get_config('metadata.json', ['exercise']) is not None

    def download(self) -> None:
        """Download the exercise."""
        assert not self.user
        if not (self.path.exists() and
                all(x.exists() for x in self.solution_files)):
            subprocess.check_call(['exercism', 'download',
                                   f'--exercise={self.name}',
                                   f'--track={self.track}'])
        self.post_download()

    def post_download(self) -> None:
        """Prepare solution after download for faster solve."""
        self._track.post_download(self)
