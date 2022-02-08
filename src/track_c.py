"""Operations for the C track on Exercism."""

import re
import subprocess
from argparse import Namespace
from pathlib import Path

import common


class CTrack(object):
    """Solutions for the C track on exercism."""

    def get_name(self) -> str:
        """Return the name of the track."""
        return 'c'

    def get_commands(self) -> list[common.Command]:
        """Return the list of commands specific to this track."""
        return [InitCommand(),
                MakeCommand('build', 'tests.out'),
                MakeCommand('test', 'test'),
                MakeCommand('clean', 'clean'),
                MakeCommand('memcheck', 'memcheck')]

    def get_files(self, namespace: Namespace) -> list[Path]:
        """Return code files for given solution."""
        return [common.get_path(namespace, '{exercise_}.c'),
                common.get_path(namespace, '{exercise_}.h')]

    def get_test_files(self, namespace: Namespace) -> list[Path]:
        """Return test files for given solution."""
        return [common.get_path(namespace, 'test_{exercise_}.c')]

    def post_download(self, namespace: Namespace) -> None:
        """Prepare solution after download for faster solve."""
        InitCommand().run(namespace)


class InitCommand(common.Command):
    """Uncomment all tests and create stub functions."""

    Function = tuple[str, str, str]

    __TYPE_RE = re.compile(r'(?:(?:const|unsigned|struct) )*\w+ \**')
    __PARAM_RE = re.compile(
        rf'{__TYPE_RE.pattern}(\w+)(?:\[(?:static )?.*?\])?')
    __PARAMS_RE = re.compile(
        rf'\((|void|{__PARAM_RE.pattern}(?:,[ \n\t]*{__PARAM_RE.pattern})*)\)',
        re.DOTALL)
    __FUNC_RE = re.compile(
        rf'(?:\n|^)({__TYPE_RE.pattern})(\w+){__PARAMS_RE.pattern}(?:;|\s?{{)',
        re.DOTALL)

    def get_name(self) -> str:
        """Return the name of the command."""
        return 'init'

    def get_help(self) -> str:
        """Return help text for the command."""
        return 're-initialize exercise'

    def __functions(self, path: Path) -> list[Function]:
        with path.open() as f:
            return [x[:3] for x in re.findall(InitCommand.__FUNC_RE, f.read())]

    def __stub_function(self, function: Function) -> str:
        stub = '\n'
        stub += '{}{}({}) {{\n'.format(*function)
        stub += '  // TODO: implement\n'
        if function[2] and function[2] != 'void':
            for param in re.findall(InitCommand.__PARAM_RE, function[2]):
                stub += f'  *(int *)(&{param}) = 0;\n'
        if function[0].strip() == 'void':
            stub += '  return;\n'
        else:
            stub += f'  return *({function[0]}*)(0);\n'
        stub += '}\n'
        return stub

    def __init_code(self, namespace: Namespace) -> None:
        h_file = common.get_path(namespace, '{exercise_}.h')
        c_file = common.get_path(namespace, '{exercise_}.c')
        h_functions = self.__functions(h_file)
        c_functions = self.__functions(c_file)
        functions_to_add = [x for x in h_functions if x not in c_functions]
        if not functions_to_add:
            return
        with c_file.open('r') as f:
            content = f.read()
        content += ''.join(self.__stub_function(x) for x in functions_to_add)
        with c_file.open('w') as f:
            f.write(content)

    def __init_tests(self, namespace: Namespace) -> None:
        test_file = common.get_path(namespace, 'test_{exercise_}.c')
        with test_file.open('r') as f:
            content = f.read()
        content = re.sub(r'(?<!// )TEST_IGNORE', r'// TEST_IGNORE', content)
        with test_file.open('w') as f:
            f.write(content)

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        self.__init_tests(namespace)
        if not namespace.user:
            self.__init_code(namespace)


class MakeCommand(common.Command):
    """Run a single make target."""

    def __init__(self, name: str, target: str):
        """Create make command.

        :param name: name of the command
        :param target: make target
        """
        self.__name = name
        self.__target = target

    def get_name(self) -> str:
        """Return the name of the command."""
        return self.__name

    def get_help(self) -> str:
        """Return help text for the command."""
        return f'run {self.__name}'

    def run(self, namespace: Namespace) -> None:
        """Run the command."""
        subprocess.check_call(['make', self.__target],
                              cwd=common.get_path(namespace))
