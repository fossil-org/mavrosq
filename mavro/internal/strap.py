import os
import sys
from typing import Callable

from ..parser.lens import LensParser, LensParserResult
from ..parser.packaging import Package, PackageImportType


def strap(parser: LensParser, print: Callable = print, *packages: Package) -> str: # NOQA
    parser.loadPackage(
        Package("std", "mavro/pkg"),
        PackageImportType.WILDCARD,
        ""
    )
    for package in packages:
        parser.loadPackage(package, PackageImportType.STD, "")
    result: LensParserResult = parser.parse()
    for error in result.line_errors:
        print(f"minor error (internal): \033[31m{error}\033[0m")
        if "--strict-verbose":
            raise error
    if result.error:
        print(f"fatal error (internal): \033[31m{result.error}\033[0m")
        try:
            input("  press return to submit an issue, or ctrl-c to skip this.")
            os.system("start https://github.com/elemenom/mavro/issues/new")
        except KeyboardInterrupt:
            ...
        if "--verbose" in sys.argv:
            raise result.error
    return result.output.cont if not result.error else ""