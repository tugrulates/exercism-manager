import os
import sys


def __path(exercise, pattern=''):
    basename = pattern.format(exercise.replace('-', '_'))
    return os.path.join(os.path.dirname(sys.argv[0]), 'python', exercise, basename)


def __command_test():
    def command(exercise):
        test = __path(exercise, '{}_test.py')
        os.system(f'python -m pytest {test}')
    return command


def files(exercise, *, include_test_files=False):
    files = [__path(exercise, '{}.py')]
    if include_test_files:
        files.append(__path(exercise, '{}_test.py'))
    return files


def init(exercise):
    pass


def commands():
    return {
        'test':     ('run tests',              __command_test()),
    }
