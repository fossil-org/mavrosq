from types import ModuleType as requirement # NOQA
from typing import Any as any # NOQA
from typing import Any as unknown # NOQA
from typing import Callable as callable # NOQA
import sys as _sys


true: True = True
false: False = False
null: None = None
iife: callable = lambda _: _()
static: callable = staticmethod

# SYSTEM AND IT'S SUBPROCESSES


class NotStartableError(Exception):
    ...
class MergeOverlapError(Exception):
    ...
class DeprecationError(Exception):
    ...
class EntrypointError(Exception):
    ...
class _SecretFailValue:
    ...

class System:
    PIPE: int = 0
    SPARE: int = 1
    ORIGIN: int = 2
    def public__exit(self, code: int = 0, silent: bool = False) -> None: # NOQA
        if not silent:
            from ..parser.coding import identifyCode
            print(f"\n{identifyCode(code)} (code {code})")
        _sys.exit(code)
    def public__createError(self, name: str) -> type: # NOQA
        return type(name, (Exception,), {})
    def public__importPython(self, module: str) -> "ModuleType": # NOQA
        import importlib
        return importlib.import_module(module)
    def public__ensure(self, # NOQA
                       action: callable,
                       default: any = None,
                       error: type[Exception] = Exception,
                       message: str | None = None
    ):
        try:
            return action()
        except error as exc:
            if str(exc) == message or message is None:
                return default
    def public__redirect(self,
                             action: callable,
                             new: Exception,
                             error: type[Exception] = Exception,
                             message: str | None = None
    ):
        if self.public__ensure(action, _SecretFailValue, error, message) == _SecretFailValue:
            raise new
    def public__merge(self, obj, /, method = None) -> None:
        try:
            name: str = obj.__name__
        except AttributeError:
            name: str = type(obj).__name__
        if method == self.ORIGIN:
            setattr(self, name, obj)
        else:
            for name, value in list(obj.__dict__.items()):
                if hasattr(self, name):
                    if method == self.PIPE:
                        setattr(self, name, value)
                    elif method == System.SPARE:
                        continue
                    else:
                        raise MergeOverlapError(f"{type(self).__name__} and {name} both have the attribute: '{name}'."
                                                "You can specify the 'method=System.PIPE' parameter to overwrite the '{name}'"
                                                "attribute (and any further overlapping attributes. Alternatively, you can specify"
                                                "'method=System.SPARE' to leave overlapping attributes in their original form without changing them."
                        )
                else:
                    setattr(self, name, value)
    class BaseClass:
        def __init__(self) -> None:
            self.__name__ = type(self).__name__
        def __starter__(self, *_, **__) -> None:
            raise NotStartableError(
                f"{type(self).__name__.removeprefix("public__")} doesn't define a starter method, and therefore cannot be started.")
        def __repr__(self) -> str:
            name: str = type(self).__name__
            return f"{"public" if name.startswith("public__") else "local"} class {name.removeprefix("public__")} ({"startable" if hasattr(self, "__starter__") else "not startable"})"