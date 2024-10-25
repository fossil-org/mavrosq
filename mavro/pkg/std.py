from types import ModuleType as requirement # NOQA
from typing import Any as any # NOQA
from typing import Any as unknown # NOQA
from typing import Callable as callable # NOQA
import sys as _sys
import os as _os
true: True = True
false: False = False
null: None = None
class baseclass:
    def __starter__(self, *_, **__) -> None:
        raise NotImplementedError(f"{type(self).__name__.removeprefix("public__")} doesn't define a starter method, and therefore cannot be started.")


# SYSTEM AND IT'S SUBPROCESSES


@lambda _: _()
class System:
    def public__exit(self, code: int = 0) -> None: # NOQA
        print(f"\nexited with code {code}")
        _sys.exit(code)
    def public__cmd(self, command: str) -> None: # NOQA
        _os.system(command)


@lambda _: _()
class Console:
    def __init__(self) -> None:
        self.__activated: bool = False
    def __assertActivated(self, fn: str | None = None) -> None:
        if not self.__activated:
            raise BlockingIOError(f"Could not execute 'Console::{fn or "unknownService"}' because the Console service is not activated.")
    def __starter__(self) -> None:
        self.__activated = True
    def public__print(self, obj: any) -> None:
        self.__assertActivated("print")
        print(obj, end="")
    def public__input(self, obj: any) -> str:
        self.__assertActivated("input")
        return input(obj)