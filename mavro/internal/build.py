import os
import subprocess
import sys
import pathlib
from typing import Callable

from ..pkg.std import System
from ..parser.lens import LensParser
from ..parser.lines import LineParser
from ..internal.driver import create_temporary_file_from_lens

def build(
        usage: str,
        path: str,
        dist_path: str | None = None,
        no_delete: bool = False,
        line_loader: Callable | None = None,
        run: bool = True
    ) -> str:
    with open(path) as file_literal:
        cont: str = file_literal.read()
    lens: LensParser = LensParser(
        cont=cont,
        baseline=LineParser(),
        line_loader=line_loader
    )
    no_delete = no_delete or "--no-delete" in sys.argv
    with create_temporary_file_from_lens(lens, dist_path=dist_path, no_delete=no_delete) as fn:
        from ..pkg.std import System
        if run:
            result: subprocess.CompletedProcess = System().public__ensure(lambda: subprocess.run(
                f"{usage} {fn}",
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            ), error=KeyboardInterrupt) # NOQA
            if result:
                if result.stderr:
                    if "--verbose" in sys.argv:
                        print(result.stderr)
                    else:
                        try: info: str = result.stderr.split("\n")[-2].split(":", 1)[1].lstrip()
                        except Exception: # NOQA
                            info: str = "this error was passed with no message nor traceback."
                        try: name: str = result.stderr.split("\n")[-2].split(":", 1)[0]
                        except Exception: # NOQA
                            name: str = "ErrorNotFound"
                        if info == "'System' object has no attribute 'BaseString'":
                            name = "StringError"
                            info = "Attempted usage of String object without it's dedicated System merge."
                        print(f"fatal {name}: \033[31m{info}\033[0m")
    return fn
def build_from_sys_argv() -> None:
    args: list[str] = sys.argv
    try: args[1]
    except IndexError:
        args.append(".")
    usage: str = "python.exe"
    if "-u" in args:
        try:
            usage = args[args.index("-u") + 1]
        except IndexError:
            print("'-u' argument expected one parameter.")
            sys.exit(1)
    if args[1] in ["--version", "-v"]:
        from .. import version
        print(f"Mavro version: {version}")
        sys.exit(0)
    elif args[1] == "--github":
        os.system("start https://github.com/astridot/mavro")
        sys.exit(0)
    elif args[1] == "--pypi":
        os.system("start https://pypi.org/project/mavro")
        sys.exit(0)
    elif args[1] == "--author":
        os.system("start https://github.com/astridot")
        sys.exit(0)
    elif args[1].startswith("-"):
        args.append(args[1])
        args[1] = "."
    if os.path.exists(args[1]):
        if os.path.isdir(args[1]):
            args[1] = str(pathlib.Path(args[1]) / "main.mav")
        if "-c" in args or "--create" in args:
            with open(args[1], "w") as file:
                file.write("entrypoint\n  .print 'main.mav file was created!'\nend")
        if not os.path.exists(args[1]):
            print(f"'{args[1]}' does not exist, and cannot be executed.")
            return
        build(
            usage=usage,
            path=args[1]
        )
    else:
        print(f"'{args[1]}' does not exist, and cannot be executed.")
if __name__ == "__main__":
    build_from_sys_argv()
