import os
import os as _os
import os.path as _path
from importlib import import_module as _import_module
from types import ModuleType as _ModuleType

from mavro.parser.lens import LensParser as _LensParser


def public__findService(module: str) -> _ModuleType | None:
    pyname: str = f"{module.removesuffix(".mav")}_requiry.py"
    try:
        if not _path.exists(module):
            raise ImportError(f"Mavro module '{module}' not found in '{_os.getcwd()}'")
        from ..internal.build import build
        build(
            usage="python.exe",
            path=module,
            dist_path=pyname,
            no_delete=True,
            line_loader=_LensParser.stdLoadLinesWithoutEntrypoint,
            run=False
        )
        module_literal: _ModuleType = _import_module(pyname.removesuffix(".py"))
    finally:
        try:
            os.remove(pyname)
        except FileNotFoundError:
            print(f"module error: could not clean {pyname}")
            return
    return module_literal