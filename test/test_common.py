"""Tests for the common module."""

import unittest
from argparse import Namespace

import common


class CommonTest(unittest.TestCase):
    """Test cases for common operations."""

    def test_fmt(self) -> None:
        """Test common.fmt."""
        args = Namespace(user=None, track='rust', exercise='rat-race')
        self.assertEqual(common.fmt('test', args), 'test')
        self.assertEqual(common.fmt('{track}', args), 'rust')
        self.assertEqual(common.fmt(
            '{track} and {exercise}', args), 'rust and rat-race')
        with self.assertRaises(KeyError):
            common.fmt('{unknown}', args)

    def test_get_path_no_user(self) -> None:
        """Test common.path when no user is given."""
        args = Namespace(user=None, track='rust', exercise='rat-race')
        self.assertRegex(common.get_path(args, 'a'), '.*/rust/rat-race/a$')
        self.assertNotRegex(common.get_path(args, 'a'), '.*/users/.*')
        self.assertRegex(
            common.get_path(args, 'a', 'b'), '.*/rust/rat-race/a/b$')
        self.assertRegex(
            common.get_path(args, 'a', 'b'), '.*/rust/rat-race/a/b$')
        self.assertRegex(
            common.get_path(args, '{exercise}.rs'),
            '.*/rust/rat-race/rat_race.rs$')
        self.assertRegex(
            common.get_path(args, 'test_{exercise}.rs'),
            '.*/rust/rat-race/test_rat_race.rs$')
        with self.assertRaises(KeyError):
            common.get_path(args, '{unknown}')

    def test_get_path_user(self) -> None:
        """Test common.path when a user is given."""
        args = Namespace(user='bob', track='rust', exercise='rat-race')
        self.assertRegex(
            common.get_path(args, 'a'),
            '.*/users/bob/rust/rat-race/a$')
        self.assertRegex(
            common.get_path(args, 'a', 'b'),
            '.*/users/bob/rust/rat-race/a/b$')
        self.assertRegex(common.get_path(
            args, 'test_{exercise}.rs'),
            '.*/users/bob/rust/rat-race/test_rat_race.rs$')


if __name__ == '__main__':
    unittest.main()
