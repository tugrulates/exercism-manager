import os
import sys
import manage


def __command_test(args):
    test = manage.get_path(args, '{exercise}_test.py')
    os.system(f'python -m pytest {test}')


def get_files(args, *, include_test_files=False):
    files = [manage.get_path(args, '{exercise}.py')]
    if include_test_files:
        files.append(manage.get_path(args, '{exercise}_test.py'))
    return files


def init(exercise):
    pass


def commands():
    return {
        'test': ('run tests', __command_test),
    }
