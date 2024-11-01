import os
import sys
from typing import Callable

from ..parser.lens import LensParser, LensParserResult
from ..parser.packaging import Package, PackageImportType


def strap(parser: LensParser, print: Callable = print, *packages: Package, return_dependencies: bool = False) -> str | tuple[str, list[str]]: # NOQA
    parser.loadPackage(
        Package("std", "mavro/pkg"),
        PackageImportType.WILDCARD,
        ""
    )
    for package in packages:
        parser.loadPackage(package, PackageImportType.STD, "")
    result: LensParserResult = parser.parse()
    for error in result.line_errors:
        print(f"internal error (minor): \033[31m{error}\033[0m")
        if "--strict-verbose":
            raise error
    if result.error:
        print(f"internal error (fatal): \033[31m{result.error}\033[0m")
        try:
            input("  press return to submit an issue, or ctrl-c to skip this.")
            os.system("start https://github.com/astridot/mavro/issues/new")
        except KeyboardInterrupt:
            ...
        if "--verbose" in sys.argv:
            raise result.error
    cont: str = result.output.cont if not result.error else ""
    if return_dependencies:
        return cont, result.dependencies
    return cont