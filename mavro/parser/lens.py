import sys
from types import SimpleNamespace
from typing import Any, Callable
from uuid import uuid4

from .coding import identifyCode
from .lines import LineParser, LineParserResult
from .packaging import Package, PackageImportType


class LensParserResult(LineParserResult):
    def __init__(self, output: SimpleNamespace, code: int, error: Exception | None = None, line_errors: list[Exception] | None = None) -> None:
        super().__init__(output, code, error)
        self.line_errors = line_errors or []


class LensParser:
    LINE_LOADER_BEFORE: list[str] = """
from mavro.pkg.std import *
function _ignoredRaiseError exc
    raise exc
end
const callable print = lambda *_, **__: _ignoredRaiseError(SyntaxError("'print' is deprecated and cannot be used. Use 'Console.print' instead."))
const callable input = lambda *_, **__: _ignoredRaiseError(SyntaxError("'input' is deprecated and cannot be used. Use 'Console.input' instead."))
const callable exit = lambda *_, **__: _ignoredRaiseError(SyntaxError("'exit' is deprecated and cannot be used. Use 'System.exit' instead."))
""".split("\n")
    def __init__(self, cont: str, baseline: LineParser, line_loader: Callable | None = None) -> None:
        """The line_loader parameter shouldn't need to be changed."""
        self.cont: str = cont
        self.id: str = str(uuid4())
        self.lns: list[str | LineParserResult] = (line_loader or self.stdLoadLines)(self.cont)
        self.baseline: LineParser = baseline
    @staticmethod
    def stdLoadLines(cont: str) -> list[str]:
        AFTER: list[str] = """
import sys
try
    __entrypoint__
end
catch NameError
    raise SyntaxError('File has no entrypoint.')
end
only private
    .__entrypoint__
    System::exit(0)
end
""".split("\n")
        lns: list[str] = [*LensParser.LINE_LOADER_BEFORE,
                          *cont.split("\n"),
                          *AFTER
        ]
        return lns
    @staticmethod
    def stdLoadLinesWithoutEntrypoint(cont: str) -> list[str]:
        lns: list[str] = [*LensParser.LINE_LOADER_BEFORE,
                          *cont.split("\n")
        ]
        return lns
    @staticmethod
    def loadPackage(package: Package, import_type: PackageImportType, arg: str) -> str | Exception:
        if package.origin != "mavro/pkg":
            return ImportError("Tried retrieving a pkg that doesn't seem to originate from mavro's verified pkg source (mavro/pkg)")
        text: str | Exception = package.getImportStatement(import_type, arg)
        return text
    def parse(self) -> LensParserResult:
        def error(exc: Exception) -> LensParserResult:
            return LensParserResult(
                output=SimpleNamespace(),
                code=1,
                error=exc,
                line_errors=line_errors
            )
        output: dict[str, Any] = {
            "cont": ""
        }
        indent: int = 0
        line_errors: list[Exception] = []
        try:
            for ln_num, ln in enumerate(self.lns, start=1):
                if isinstance(ln, str):
                    parser: LineParser = self.baseline.next(ln)
                elif isinstance(ln, LineParser):
                    parser: LineParser = ln
                else:
                    raise TypeError(f"Invalid line type on stack n. {ln_num} most likely inserted due to a faulty suggestion by a line parser.\n"
                                    f"Expected type str or LineParserResult, got {type(ln).__name__}.")
                parser.applyIndentation(indent)
                result: LineParserResult = parser.parse()
                original_indent: int = indent
                if "--verbose" in sys.argv:
                    print(f"Parsing of stack n. {"0" * (3 - len(str(ln_num)))}{ln_num} indented {"0" * (2 - len(str(int(indent / 4))))}{int(indent / 4)} layers {identifyCode(result.code)} (returned code {result.code}) ~ {result.output.cont}")
                if result.error:
                    line_errors.append(result.error)
                    continue
                for suggestion in result.output.suggestions:
                    self.lns.insert(ln_num + 1, suggestion.apply(parser))
                if isinstance(result.output, SimpleNamespace):
                    cont: str = result.output.cont.strip()
                else:
                    print(f"Unexpected type for result.output: {type(result.output)}")
                    continue
                if cont.startswith("let ") or cont.startswith("const "):
                    parts: list[str] = cont.split(" ", 3)
                    try:
                        cont = f"{parts[2].rstrip(";")}: {parts[1]}{parts[3]}"
                    except IndexError:
                        raise TypeError(f"Not enough parameters for variable definition. Usage: `let|const <type> <name> = <value>`")
                elif cont.startswith("public const "):
                    parts: list[str] = cont.split(" ", 4)
                    try:
                        cont = f"public__{parts[3].rstrip(";")}: {parts[2]}{parts[4]}"
                    except IndexError:
                        raise TypeError(f"Not enough parameters for variable definition. Usage: `let|const <type> <name> = <value>`")
                elif cont.startswith("public let "):
                    raise TypeError("Variables declared with `let` cannot be public.")
                elif cont.startswith("function "):
                    parts: list[str] = cont.split(" ", 2)
                    cont = f"def {parts[1]}({parts[2] if len(parts) > 2 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("method "):
                    parts: list[str] = cont.split(" ", 2)
                    cont = f"def {parts[1]}(self, {parts[2] if len(parts) > 2 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("static function "):
                    parts: list[str] = cont.split(" ", 3)
                    cont = f"@staticmethod\n{" " * original_indent}def {parts[2]}({parts[3] if len(parts) > 3 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("self method "):
                    parts: list[str] = cont.split(" ", 3)
                    cont = f"def {parts[2]}(self, {parts[3] if len(parts) > 3 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("public function "):
                    parts: list[str] = cont.split(" ", 3)
                    cont = f"def public__{parts[2]}({parts[3] if len(parts) > 3 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("public method "):
                    parts: list[str] = cont.split(" ", 3)
                    cont = f"def public__{parts[2]}(self, {parts[3] if len(parts) > 3 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("require "):
                    parts: list[str] = cont.split(" ", 2)
                    if "import mavro.pkg.requiry as requiry" not in output["cont"]:
                        raise SyntaxError("Attempted fetching of Mavro module while the requiry package wasn't imported.")
                    cont = f"{parts[1]} = requiry.public__findService(\"{parts[1]}.mav\")"
                elif cont.startswith("def "):
                    raise SyntaxError("Python 'def' keyword is not supported in Mavro. Use 'function' instead")
                elif cont.startswith("if "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"if {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("else if "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"elif {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("elif "):
                    raise SyntaxError("Python 'elif' keyword is not supported in Mavro. Use 'else if' instead")
                elif cont == "else":
                    cont = f"else:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont == "try":
                    cont = f"try:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont == "finally":
                    cont = f"finally:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont == "entrypoint":
                    cont = f"def __entrypoint__() -> int:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont == "end":
                    cont = "# end"
                    indent -= 4
                elif cont == "only private":
                    cont = "if __name__ == \"__main__\":"
                    indent += 4
                elif cont == "only public":
                    cont = "if __name__ != \"__main__\":\n"
                    indent += 4
                elif cont == "savelocation":
                    cont = f"from types import SimpleNamespace\n{" " * original_indent}here = SimpleNamespace(**(globals() | locals()))\n{" " * original_indent}del SimpleNamespace"
                elif cont.startswith("catch "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"except {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("except "):
                    raise SyntaxError("Python 'except' keyword is not supported in Mavro. Use 'catch' instead")
                elif cont.startswith("while "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"while {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("for "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"for {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("constructor"):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"def __init__(self, {parts[1] if len(parts) > 1 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("starter"):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"def __starter__(self, {parts[1] if len(parts) > 1 else ""
                    }):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("startprocess "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"{parts[1]}.__starter__({parts[2] if len(parts) > 2 else ""})"
                elif cont.startswith("until "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"while not {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("class "):
                    parts: list[str] = cont.split(" ", 3)
                    if parts[2] == "extends" and len(parts) > 3:
                        cont = f"class {parts[1]}({parts[3]}):\n{" " * (original_indent + 4)}..."
                    else:
                        cont = f"class {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("public class "):
                    parts: list[str] = cont.split(" ", 4)
                    if parts[3] == "extends" and len(parts) > 3:
                        cont = f"class public__{parts[2]}({parts[4]}):\n{" " * (original_indent + 4)}..."
                    else:
                        cont = f"class public__{parts[2]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("manager "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"with {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("with "):
                    raise SyntaxError("Python 'with' keyword is not supported in Mavro. Use 'manager' instead")
                elif cont.startswith("openfile "):
                    parts: list[str] = cont.split(" ", 2)
                    cont = f"with open({parts[1]}, {parts[2]}) as file:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith(".") and cont != "...":
                    cont = cont.removeprefix(".").lstrip()
                    parts: list[str] = cont.split(" ", 1)
                    while True:
                        if parts[0] == "":
                            parts.pop(0)
                        else:
                            break
                    cont = f"{parts[0]}({parts[1] if len(parts) > 1 else ""})"
                elif cont.startswith("::"):
                    cont = cont.removeprefix("::").lstrip()
                    parts: list[str] = cont.split(" ", 1)
                    while True:
                        if parts[0] == "":
                            parts.pop(0)
                        else:
                            break
                    cont = f"public__{parts[0]}({parts[1] if len(parts) > 1 else ""})"
                elif cont.startswith("package "):
                    parts: list[str] = cont.split(" ", 1)
                    try:
                        package_name: str = parts[1]
                    except IndexError:
                        raise ImportError("Not enough arguments for package import.")
                    try:
                        package: Package = Package(
                            name=package_name,
                            origin="mavro/pkg"
                        )
                        package_result: str | Exception = self.loadPackage(package, PackageImportType.AS, package.name)
                        if isinstance(package_result, Exception):
                            raise package_result
                        cont = package_result
                    except Exception as exception:
                        raise exception
                cont = f"{" " * original_indent}{cont}"
                output["cont"] += cont + "\n" # NOQA
                indent += result.output.indent # NOQA
        except Exception as exception:  # NOQA
            if "--verbose" in sys.argv:
                raise exception
            return error(exception)
        else:
            return LensParserResult(output=SimpleNamespace(**output), code=0, line_errors=line_errors)