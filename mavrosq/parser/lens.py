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
from mavrosq.pkg.std import *
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
""".strip().split("\n")
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
""".strip().split("\n")
    def __init__(self, content: str, baseline: LineParser, line_loader: Callable | None = None) -> None:
        """The line_loader parameter shouldn't need to be changed."""
        self.content: str = content
        self.id: str = str(uuid4())
        self.lns: list[str | LineParserResult] = (line_loader or self.stdLoadLines)(self.content)
        self.baseline: LineParser = baseline
    @staticmethod
    def stdLoadLines(content: str) -> list[str]:
        lns: list[str] = [*LensParser.LINE_LOADER_BEFORE,
                          *content.split("\n"),
                          *LensParser.LINE_LOADER_AFTER
        ]
        return lns
    @staticmethod
    def stdLoadLinesWithoutEntrypoint(content: str) -> list[str]:
        lns: list[str] = [*LensParser.LINE_LOADER_BEFORE,
                          *content.split("\n")
        ]
        return lns
    @staticmethod
    def loadPackage(package: Package, import_type: PackageImportType, arg: str) -> str | Exception:
        if package.origin != "mavrosq/pkg":
            return ImportError("Tried retrieving a pkg that doesn't seem to originate from mavro²'s verified pkg source (mavrosq/pkg)")
        text: str | Exception = package.getImportStatement(import_type, arg)
        return text
    @staticmethod
    def _includeKwCheck(content: str) -> bool:
        import keyword
        kws: list[str] = list(keyword.kwlist)

        for kw in kws:
            if content.startswith(f"{kw} ") or content == kw:
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
            "content": ""
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
                    print(f"Parsing of stack n. {"0" * (3 - len(str(ln_num)))}{ln_num} indented {"0" * (2 - len(str(int(indent / 4))))}{int(indent / 4)} layers {identifyCode(result.code)} (returned code {result.code}) ~ {result.output.content}")
                if result.error:
                    line_errors.append(result.error)
                    continue
                for suggestion in result.output.suggestions:
                    self.lns.insert(ln_num + 1, suggestion.apply(parser))
                if isinstance(result.output, SimpleNamespace):
                    content: str = result.output.content.strip().removeprefix("local ")
                else:
                    print(f"Unexpected type for result.output: {type(result.output)}")
                    continue
                if content.startswith("let ") or content.startswith("const "):
                    parts: list[str] = content.split(" ", 2)
                    try:
                        content = f"{parts[2][:parts[2].index("=")]}: {parts[1]}{parts[2][parts[2].index("="):]}"
                        if parts[1] == "str":
                            content = f"str()"
                    except IndexError:
                        raise TypeError(f"Not enough parameters for variable definition. Usage: {parts[0]} <type> <name> = <value>`")
                elif content.startswith("remark "):
                    content = content.removeprefix("remark ")
                elif content.startswith("import "):
                    parts: list[str] = content.split(" ", 4)
                    if "import mavrosq.pkg.requiry as requiry" in output["content"] and "." not in parts[1]:
                        alias: str = ""
                        if len(parts) > 2:
                            if parts[2] == "as":
                                alias = parts[3]
                        content = f"{alias or parts[1]} = System.public__ensure(lambda: System.public__importPython('{parts[1]}'), None, ModuleNotFoundError) or requiry.public__findService('{parts[1]}.mav')"
                    dependencies.append(parts[1])
                elif content.startswith("upload "):
                    parts: list[str] = content.split(" ", 1)
                    content = f"self.{parts[1]} = {parts[1]}"
                elif content.startswith("from "):
                    parts: list[str] = content.split(" ", 6)
                    if parts[2] != "import":
                        raise SyntaxError("'from' keyword expected 'import'")
                    if "import mavrosq.pkg.requiry as requiry" in output["content"] and "." not in parts[1]:
                        alias: str = ""
                        if len(parts) > 4:
                            if parts[4] == "as":
                                alias = parts[5]
                        content = f"{alias or parts[3]} = (System.public__ensure(lambda: System.public__importPython('{parts[1]}'), None, ModuleNotFoundError) or requiry.public__findService('{parts[1]}.mav')).{parts[3]}"
                    dependencies.append(parts[1])
                elif content.startswith("public const "):
                    parts: list[str] = content.split(" ", 4)
                    try:
                        content = f"public__{parts[3][:parts[3].index("=")]}: {parts[2]}{parts[3][parts[3].index("="):]}"
                        if parts[2] == "str":
                            content = f"str()"
                    except IndexError:
                        raise TypeError(f"Not enough parameters for public variable definition. Usage: `public {parts[1]} <type> <name> = <value>`")
                elif content.startswith("public let "):
                    raise TypeError("Variables declared with 'let' cannot be public.")
                elif content.startswith("function "):
                    parts: list[str] = content.split(" ", 2)
                    content = f"def {parts[1]}({parts[2] if len(parts) > 2 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("method "):
                    parts: list[str] = content.split(" ", 2)
                    content = f"def {parts[1]}(self, {parts[2] if len(parts) > 2 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("apply "):
                    parts: list[str] = content.split(" ", 1)
                    content = f"@{parts[1]}"
                elif content.startswith("remote "):
                    parts: list[str] = content.split(" ", 3)
                    content = f"@lambda _: _()\n{" " * original_indent}class {parts[2]}({parts[1]}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("root "):
                    parts: list[str] = content.split(" ", 2)
                    if parts[1] == "...":
                        content = ""
                    else:
                        content = f"@{parts[1]}"
                    self.lns.insert(ln_num, parts[2])
                elif content.startswith("special method "):
                    parts: list[str] = content.split(" ", 3)
                    content = f"def {parts[2]}(self, {parts[3] if len(parts) > 3 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("public function "):
                    parts: list[str] = content.split(" ", 3)
                    content = f"def public__{parts[2]}({parts[3] if len(parts) > 3 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("public method "):
                    parts: list[str] = content.split(" ", 3)
                    content = f"def public__{parts[2]}(self, {parts[3] if len(parts) > 3 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("require "):
                    parts: list[str] = content.split(" ", 2)
                    if "import mavrosq.pkg.requiry as requiry" not in output["content"]:
                        raise SyntaxError("Attempted fetching of Mavro module while the requiry package wasn't imported.")
                    content = f"{parts[1]} = requiry.public__findService('{parts[1]}.mav')"
                elif content.startswith("def "):
                    raise SyntaxError("Python 'def' keyword is not supported in Mavro. Use 'function' instead")
                elif content.startswith("if "):
                    parts: list[str] = content.split(" ", 1)
                    content = f"if {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("else if "):
                    original_indent -= 4
                    parts: list[str] = content.split(" ", 1)
                    content = f"elif {parts[1]}:\n{" " * (original_indent + 4)}..."
                elif content.startswith("elif "):
                    raise SyntaxError("Python 'elif' keyword is not supported in Mavro. Use 'else if' instead")
                elif content == "else":
                    original_indent -= 4
                    content = f"else:\n{" " * (original_indent + 4)}..."
                elif content == "try":
                    content = f"try:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content == "finally":
                    original_indent -= 4
                    content = f"finally:\n{" " * (original_indent + 4)}..."
                elif content == "entrypoint":
                    content = f"def __entrypoint__() -> int:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content == "end":
                    content = f"# end"
                    indent -= 4
                elif content.startswith("end "):
                    self.lns.insert(ln_num + 1, content.removeprefix("end "))
                    indent -= 4
                elif content == "only private":
                    content = "if __name__ == \"__main__\":"
                    indent += 4
                elif content == "only public":
                    content = "if __name__ != \"__main__\":\n"
                    indent += 4
                elif content == "savelocation":
                    content = f"from types import SimpleNamespace\n{" " * original_indent}here = SimpleNamespace(**(globals() | locals()))\n{" " * original_indent}del SimpleNamespace"
                elif content.startswith("catch "):
                    original_indent -= 4
                    parts: list[str] = content.split(" ", 1)
                    content = f"except {parts[1]}:\n{" " * (original_indent + 4)}..."
                elif content.startswith("except "):
                    raise SyntaxError("Python 'except' keyword is not supported in Mavro. Use 'catch' instead")
                elif content.startswith("while "):
                    parts: list[str] = content.split(" ", 1)
                    content = f"while {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("for "):
                    parts: list[str] = content.split(" ", 1)
                    content = f"for {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("constructor"):
                    parts: list[str] = content.split(" ", 1)
                    content = f"def __init__(self, {parts[1] if len(parts) > 1 else ""}):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("extends constructor"):
                    parts: list[str] = content.split(" ", 2)
                    content = f"def __init__(self, {parts[2] if len(parts) > 2 else ""}):\n{" " * (original_indent + 4)}super().__init__({parts[2] if len(parts) > 2 else ""})"
                    indent += 4
                elif content.startswith("starter"):
                    parts: list[str] = content.split(" ", 1)
                    content = f"def __starter__(self, {parts[1] if len(parts) > 1 else ""
                    }):\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("startprocess "):
                    parts: list[str] = content.split(" ", 1)
                    content = f"{parts[1]}.__starter__({parts[2] if len(parts) > 2 else ""})"
                elif content.startswith("until "):
                    parts: list[str] = content.split(" ", 1)
                    content = f"while not {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("class "):
                    parts: list[str] = content.split(" ", 3)
                    if parts[2] == "extends" and len(parts) > 3:
                        content = f"class {parts[1]}({parts[3]}):\n{" " * (original_indent + 4)}..."
                    else:
                        content = f"class {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("public class "):
                    parts: list[str] = content.split(" ", 4)
                    if parts[3] == "extends" and len(parts) > 3:
                        content = f"class public__{parts[2]}({parts[4]}):\n{" " * (original_indent + 4)}..."
                    else:
                        content = f"class public__{parts[2]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("manager "):
                    parts: list[str] = content.split(" ", 1)
                    content = f"with {parts[1]}:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("with "):
                    raise SyntaxError("Python 'with' keyword is not supported in Mavro. Use 'manager' instead")
                elif content.startswith("openfile "):
                    parts: list[str] = content.split(" ", 2)
                    content = f"with open({parts[1]}, {parts[2]}) as file:\n{" " * (original_indent + 4)}..."
                    indent += 4
                elif content.startswith("package "):
                    parts: list[str] = content.split(" ", 1)
                    try:
                        package_name: str = parts[1]
                    except IndexError:
                        raise ImportError("Not enough arguments for package import.")
                    try:
                        package: Package = Package(
                            name=package_name,
                            origin="mavrosq/pkg"
                        )
                        package_result: str | Exception = self.loadPackage(package, PackageImportType.AS, package.name)
                        if isinstance(package_result, Exception):
                            raise package_result
                        content = package_result
                    except Exception as exception:
                        raise exception
                elif self._includeKwCheck(content):
                    ...
                else:
                    parts: list[str] = content.split(" ", 1)
                    content = f"{parts[0]}({parts[1] if len(parts) > 1 else ""})"
                content = f"{" " * original_indent}{content}"
                output["content"] += content + "\n" # NOQA
                indent += result.output.indent # NOQA
        except Exception as exception:  # NOQA
            if "--verbose" in sys.argv:
                raise exception
            return error(exception)
        else:
            return LensParserResult(output=SimpleNamespace(**output), code=0, line_errors=line_errors)