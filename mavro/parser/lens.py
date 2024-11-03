import sys
from types import SimpleNamespace
from typing import Any, Callable
from uuid import uuid4

from .coding import identifyCode
from .lines import LineParser, LineParserResult
from .packaging import Package, PackageImportType


class LensParserResult(LineParserResult):
    def __init__(self, output: SimpleNamespace, code: int, error: Exception | None = None, line_errors: list[Exception] | None = None, dependencies: list[str] | None = None) -> None:
        super().__init__(output, code, error)
        self.line_errors: list[Exception] = line_errors or []
        self.dependencies: list[str] = dependencies or []


class LensParser:
    LINE_LOADER_BEFORE: list[str] = """
from mavro.pkg.std import *
const System System = System()
package console
package string
System::merge console.Console, method=System.ORIGIN
System::merge string, method=System.SPARE
startprocess System.Console
const console.Console Console = System.Console
const string.String String = System.String
savelocation

function _deprecated name, sub=null
    function wrapper *_, **__
        raise DeprecationError("'{name}' is deprecated and cannot be used. {'Use \\'{}\\' instead.'.format(sub) if sub else ''}")
    end
    return wrapper
end
const callable print = _deprecated("print", "Console::print")
const callable input = _deprecated("input", "Console::input")
const callable exit = _deprecated("exit", "System::exit")
const callable str = _deprecated("str", "System.String")
del console, string
""".split("\n")
    LINE_LOADER_AFTER: list[str] = """
try
    remark __entrypoint__
catch NameError
else
    only private
        __entrypoint__
        System::exit 0
    end
end
""".split("\n")
    def __init__(self, cont: str, baseline: LineParser, line_loader: Callable | None = None) -> None:
        """The line_loader parameter shouldn't need to be changed."""
        self.cont: str = cont
        self.id: str = str(uuid4())
        self.lns: list[str | LineParserResult] = (line_loader or self.stdLoadLines)(self.cont)
        self.baseline: LineParser = baseline
    @staticmethod
    def stdLoadLines(cont: str) -> list[str]:
        lns: list[str] = [*LensParser.LINE_LOADER_BEFORE,
                          *cont.split("\n"),
                          *LensParser.LINE_LOADER_AFTER
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
    @staticmethod
    def _includeKwCheck(cont: str) -> bool:
        import keyword
        kws: list[str] = list(keyword.kwlist)

        for kw in kws:
            if cont.startswith(f"{kw} ") or cont == kw:
                return True
        return False
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
        dependencies: list[str] = []
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
                    cont: str = result.output.cont.strip().removeprefix("local ")
                else:
                    print(f"Unexpected type for result.output: {type(result.output)}")
                    continue
                if cont.startswith("let ") or cont.startswith("const "):
                    parts: list[str] = cont.split(" ", 2)
                    try:
                        cont = f"{parts[2][:parts[2].index("=")]}: {parts[1]}{parts[2][parts[2].index("="):]}"
                        if parts[1] == "str":
                            cont = f"str()"
                    except IndexError:
                        raise TypeError(f"Not enough parameters for variable definition. Usage: {parts[0]} <type> <name> = <value>`")
                elif cont.startswith("remark "):
                    cont = cont.removeprefix("remark ")
                elif cont.startswith("import "):
                    parts: list[str] = cont.split(" ", 4)
                    if "import mavro.pkg.requiry as requiry" in output["cont"] and "." not in parts[1]:
                        alias: str = ""
                        if len(parts) > 2:
                            if parts[2] == "as":
                                alias = parts[3]
                        cont = f"{alias or parts[1]} = System.public__ensure(lambda: System.public__importPython('{parts[1]}'), None, ModuleNotFoundError) or requiry.public__findService('{parts[1]}.mav')"
                    dependencies.append(parts[1])
                elif cont.startswith("from "):
                    parts: list[str] = cont.split(" ", 6)
                    if parts[2] != "import":
                        raise SyntaxError("'from' keyword expected 'import'")
                    if "import mavro.pkg.requiry as requiry" in output["cont"] and "." not in parts[1]:
                        alias: str = ""
                        if len(parts) > 4:
                            if parts[4] == "as":
                                alias = parts[5]
                        cont = f"{alias or parts[3]} = (System.public__ensure(lambda: System.public__importPython('{parts[1]}'), None, ModuleNotFoundError) or requiry.public__findService('{parts[1]}.mav')).{parts[3]}"
                    dependencies.append(parts[1])
                elif cont.startswith("public const "):
                    parts: list[str] = cont.split(" ", 4)
                    try:
                        cont = f"public__{parts[3][:parts[3].index("=")]}: {parts[2]}{parts[3][parts[3].index("="):]}"
                        if parts[2] == "str":
                            cont = f"str()"
                    except IndexError:
                        raise TypeError(f"Not enough parameters for public variable definition. Usage: `public {parts[1]} <type> <name> = <value>`")
                elif cont.startswith("public let "):
                    raise TypeError("Variables declared with 'let' cannot be public.")
                elif cont.startswith("function "):
                    parts: list[str] = cont.split(" ", 2)
                    cont = f"def {parts[1]}({parts[2] if len(parts) > 2 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("method "):
                    parts: list[str] = cont.split(" ", 2)
                    cont = f"def {parts[1]}(self, {parts[2] if len(parts) > 2 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("apply "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"@{parts[1]}"
                elif cont.startswith("remote "):
                    parts: list[str] = cont.split(" ", 3)
                    cont = f"@lambda _: _()\n{" " * original_indent}class {parts[2]}({parts[1]}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("root "):
                    parts: list[str] = cont.split(" ", 2)
                    if parts[1] == "...":
                        cont = ""
                    else:
                        cont = f"@{parts[1]}"
                    self.lns.insert(ln_num, parts[2])
                elif cont.startswith("special method "):
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
                    cont = f"{parts[1]} = requiry.public__findService('{parts[1]}.mav')"
                elif cont.startswith("def "):
                    raise SyntaxError("Python 'def' keyword is not supported in Mavro. Use 'function' instead")
                elif cont.startswith("if "):
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"if {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont.startswith("else if "):
                    original_indent -= 4
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"elif {parts[1]}:\n{" " * (original_indent + 4)}..."
                elif cont.startswith("elif "):
                    raise SyntaxError("Python 'elif' keyword is not supported in Mavro. Use 'else if' instead")
                elif cont == "else":
                    original_indent -= 4
                    cont = f"else:\n{" " * (original_indent + 4)}..."
                elif cont == "try":
                    cont = f"try:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont == "finally":
                    original_indent -= 4
                    cont = f"finally:\n{" " * (original_indent + 4)}..."
                elif cont == "entrypoint":
                    cont = f"def __entrypoint__() -> int:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif cont == "end":
                    cont = f"# end"
                    indent -= 4
                elif cont.startswith("end "):
                    self.lns.insert(ln_num + 1, cont.removeprefix("end "))
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
                    original_indent -= 4
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"except {parts[1]}:\n{" " * (original_indent + 4)}..."
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
                elif cont.startswith("extends constructor"):
                    parts: list[str] = cont.split(" ", 2)
                    cont = f"def __init__(self, {parts[2] if len(parts) > 2 else ""}):\n{" " * (original_indent + 4)}super().__init__({parts[2] if len(parts) > 2 else ""})"
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
                elif self._includeKwCheck(cont):
                    ...
                else:
                    parts: list[str] = cont.split(" ", 1)
                    cont = f"{parts[0]}({parts[1] if len(parts) > 1 else ""})"
                cont = f"{" " * original_indent}{cont}"
                output["cont"] += cont + "\n" # NOQA
                indent += result.output.indent # NOQA
        except Exception as exception:  # NOQA
            if "--verbose" in sys.argv:
                raise exception
            return error(exception)
        else:
            return LensParserResult(output=SimpleNamespace(**output), code=0, line_errors=line_errors)