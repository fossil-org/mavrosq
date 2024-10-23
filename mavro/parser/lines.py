import sys
from typing import Any
from uuid import uuid4
from types import SimpleNamespace


class LineParserResult:
    def __init__(self, output: SimpleNamespace, code: int, error: Exception | None = None) -> None:
        self.output: SimpleNamespace = output
        self.code: int = code
        self.error: Exception | None = error


class LineParserNextSuggestion:
    def __init__(self, suggestion: str) -> None:
        self.suggestion: str = suggestion
    def apply(self, parser: "LineParser") -> "LineParser":
        return parser.next(self.suggestion)


class LineParser:
    def __init__(self, cont: str | None = None) -> None:
        self.id: str = str(uuid4())
        self.cont: str = self.id if cont is None else cont
        self.stack: list[LineParser] = []
    def hasCont(self) -> bool:
        return self.cont != self.id
    def next(self, cont: str) -> "LineParser":
        lp: LineParser = LineParser(cont)
        self.stack.append(lp)
        return lp
    def applyIndentation(self, indent: int) -> "LineParser":
        self.cont = " " * indent + self.cont.replace("\t", "    ").lstrip(" ")
        return self
    def parse(self) -> LineParserResult:
        self.cont = self.cont.rstrip(";")
        def error(exc: Exception) -> LineParserResult:
            return LineParserResult(
                output=SimpleNamespace(),
                code=1,
                error=exc
            )
        output: dict[str, Any] = {
            "cont": "",
            "indent": 0,
            "suggestions": []
        }
        try:
            if not self.hasCont():
                raise TypeError("Cannot parse using a baseline parser.")
            in_string: bool = False
            skip_next: int = 0
            for index, char in enumerate(self.cont):
                if skip_next > 0:
                    skip_next -= 1
                    continue
                try: nearest_char_left: str = self.cont[index - 1]
                except IndexError: nearest_char_left: str = ""
                try: nearest_char_right: str = self.cont[index + 1]
                except IndexError: nearest_char_right: str = ""
                ############################################################### CUSTOM FUNCTIONALITY
                # SERVICE GET FUNCTIONALITY
                if char == ":" and not in_string and (nearest_char_left.isalnum() or nearest_char_left in ")]") and nearest_char_right == ":" and index != 0:
                    output["cont"] += ".public__"
                    skip_next += 1
                else:
                    output["cont"] += char
        except Exception as exception: # NOQA
            if "--verbose" in sys.argv:
                raise exception
            return error(exception)
        else:
            return LineParserResult(output=SimpleNamespace(**output), code=0)