import os
import re
import sys


__TYPE_RE = re.compile(r'(?:const )?(?:struct )?\w+ \**')
__PARAM_RE = re.compile(rf'{__TYPE_RE.pattern}(\w+)')
__PARAMS_RE = re.compile(
    rf'\((|void|{__PARAM_RE.pattern}(?:,[ \n\t]*{__PARAM_RE.pattern})*)\)', re.DOTALL)
__FUNC_RE = re.compile(
    rf'\n({__TYPE_RE.pattern})(\w+){__PARAMS_RE.pattern}(?:;|\s?{{)', re.DOTALL)


def __path(exercise, pattern=''):
    basename = pattern.format(exercise.replace('-', '_'))
    return os.path.join(os.path.dirname(sys.argv[0]), 'c', exercise, basename)


def __init_tests(exercise):
    test_file = __path(exercise, 'test_{}.c')
    with open(test_file, 'r') as input:
        content = input.read()
    content = re.sub(r'(?<!// )TEST_IGNORE', r'// TEST_IGNORE', content)
    with open(test_file, 'w') as output:
        output.write(content)


def __functions(path):
    with open(path) as input:
        return [x[:3] for x in re.findall(__FUNC_RE, input.read())]


def __stub_function(function):
    stub = '\n'
    stub += '{}{}({}) {{\n'.format(*function)
    stub += '  // TODO: implement\n'
    if function[2] and function[2] != 'void':
        for param in re.findall(__PARAM_RE, function[2]):
            stub += f'  *(int *)(&{param}) = 0;\n'
    if function[0].strip() == 'void':
        stub += '  return;\n'
    else:
        stub += f'  return *({function[0]}*)(0);\n'
    stub += '}\n'
    return stub


def __init_code(exercise):
    h_file = __path(exercise, '{}.h')
    c_file = __path(exercise, '{}.c')
    h_functions = __functions(h_file)
    c_functions = __functions(c_file)
    functions_to_add = [x for x in h_functions if x not in c_functions]
    if not functions_to_add:
        return
    with open(c_file) as input:
        content = input.read()
    content += ''.join(__stub_function(x) for x in functions_to_add)
    with open(c_file, 'w') as output:
        output.write(content)


def __command_init(exercise):
    __init_tests(exercise)
    __init_code(exercise)


def __command_make(target):
    def command(exercise):
        os.chdir(__path(exercise))
        os.system(f'make {target}')
    return command


def files(exercise, *, include_test_files=False):
    return ([__path(exercise, '{}.c'),  __path(exercise, '{}.h')] +
            [__path(exercise, 'test_{}.c')] if include_test_files else [])


def init(exercise):
    __command_init(exercise)


def commands():
    return {
        'init':     ('re-initialize exercise', __command_init),
        'build':    ('build solution',         __command_make('tests.out')),
        'test':     ('run tests',              __command_make('test')),
        'clean':    ('clean build artifacts',  __command_make('clean')),
        'memcheck': ('run memory checks',      __command_make('memcheck')),
    }
