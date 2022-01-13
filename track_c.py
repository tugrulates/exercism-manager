import os
import re
from argparse import Namespace

import common


class TrackC(object):
    def get_name(self) -> str:
        return 'c'

    def get_commands(self) -> list[common.Command]:
        return [InitCommand(),
                MakeCommand('build', 'tests.out'),
                MakeCommand('test', 'test'),
                MakeCommand('clean', 'clean'),
                MakeCommand('memcheck', 'memcheck')]

    def get_files(self, namespace: Namespace) -> list[str]:
        return [common.get_path(namespace, '{exercise}.c'),
                common.get_path(namespace, '{exercise}.h')]

    def get_test_files(self, namespace: Namespace) -> list[str]:
        return [common.get_path(namespace, 'test_{exercise}.c')]

    def post_download(self, namespace: Namespace) -> None:
        InitCommand().run(namespace)


class InitCommand(object):
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
        return 'init'

    def get_help(self) -> str:
        return 're-initialize exercise'

    def __functions(self, path: str) -> list[Function]:
        with open(path) as inp:
            return [x[:3] for x in re.findall(InitCommand.__FUNC_RE,
                                              inp.read())]

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
        h_file = common.get_path(namespace, '{exercise}.h')
        c_file = common.get_path(namespace, '{exercise}.c')
        h_functions = self.__functions(h_file)
        c_functions = self.__functions(c_file)
        functions_to_add = [x for x in h_functions if x not in c_functions]
        if not functions_to_add:
            return
        with open(c_file) as inp:
            content = inp.read()
        content += ''.join(self.__stub_function(x) for x in functions_to_add)
        with open(c_file, 'w') as output:
            output.write(content)

    def __init_tests(self, namespace: Namespace) -> None:
        test_file = common.get_path(namespace, 'test_{exercise}.c')
        with open(test_file, 'r') as inp:
            content = inp.read()
        content = re.sub(r'(?<!// )TEST_IGNORE', r'// TEST_IGNORE', content)
        with open(test_file, 'w') as output:
            output.write(content)

    def run(self, namespace: Namespace) -> None:
        self.__init_tests(namespace)
        if not namespace.user:
            self.__init_code(namespace)


class MakeCommand(object):
    def __init__(self, name: str, target: str):
        self.__name = name
        self.__target = target

    def get_name(self) -> str:
        return self.__name

    def get_help(self) -> str:
        return f'run {self.__name}'

    def run(self, namespace: Namespace) -> None:
        os.chdir(common.get_path(namespace))
        os.system(f'make {self.__target}')
