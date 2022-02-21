"""Operations for the C track on Exercism."""

import re
import subprocess
from pathlib import Path

import common
from exercise import Exercise


class CTrack(common.Track):
    """Solutions for the C track on exercism."""

    @property
    def name(self) -> str:
        """Name of the track."""
        return 'c'

    @property
    def commands(self) -> list[common.Command]:
        """List of commands specific to this track."""
        return [InitCommand(),
                MakeCommand('build', 'tests.out'),
                MakeCommand('test', 'test'),
                MakeCommand('clean', 'clean'),
                MakeCommand('memcheck', 'memcheck')]

    def post_download(self, exercise: Exercise) -> None:
        """Prepare solution after download for faster solve."""
        InitCommand().run(exercise)


class InitCommand(common.Command):
    """Uncomment all tests and create stub functions."""

    Function = tuple[str, str, str]

    _TYPE_RE = re.compile(r'(?:(?:const|unsigned|struct) )*\w+ \**')
    _PARAM_RE = re.compile(
        rf'{_TYPE_RE.pattern}(\w+)(?:\[(?:static )?.*?\])?')
    _PARAMS_RE = re.compile(
        rf'\((|void|{_PARAM_RE.pattern}(?:,[ \n\t]*{_PARAM_RE.pattern})*)\)',
        re.DOTALL)
    _FUNC_RE = re.compile(
        rf'(?:\n|^)({_TYPE_RE.pattern})(\w+){_PARAMS_RE.pattern}(?:;|\s?{{)',
        re.DOTALL)

    @property
    def name(self) -> str:
        """Name of the command."""
        return 'init'

    def __functions(self, path: Path) -> list[Function]:
        with path.open() as f:
            funcs = [x[:3]
                     for x in re.findall(InitCommand._FUNC_RE, f.read())]
            return [(x[0], x[1], re.sub(r'[\s\n]+', ' ', x[2]))
                    for x in funcs]

    def __stub_function(self, function: Function) -> str:
        stub = '\n'
        stub += '{}{}({}) {{\n'.format(*function)
        stub += '  // TODO: implement\n'
        if function[2] and function[2] != 'void':
            for param in re.findall(InitCommand._PARAM_RE, function[2]):
                stub += f'  *(int *)(&{param}) = 0;\n'
        if function[0].strip() == 'void':
            stub += '  return;\n'
        else:
            stub += f'  return *({function[0]}*)(0);\n'
        stub += '}\n'
        return stub

    def __init_code(self, exercise: Exercise) -> None:
        h_file = exercise.find_file('*.h')
        c_file = exercise.find_file('*.c')
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

    def __init_tests(self, exercise: Exercise) -> None:
        for test_file in exercise.test_files:
            with test_file.open('r') as f:
                content = f.read()
            content = re.sub(r'(?<!// )TEST_IGNORE',
                             r'// TEST_IGNORE', content)
            with test_file.open('w') as f:
                f.write(content)

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        self.__init_tests(exercise)
        if not exercise.user:
            self.__init_code(exercise)


class MakeCommand(common.Command):
    """Run a single make target."""

    def __init__(self, name: str, target: str):
        """Create make command.

        :param name: name of the command
        :param target: make target
        """
        self._name = name
        self._target = target

    @property
    def name(self) -> str:
        """Name of the command."""
        return self._name

    def run(self, exercise: Exercise) -> None:
        """Run the command."""
        subprocess.check_call(['make', self._target], cwd=exercise.path)
