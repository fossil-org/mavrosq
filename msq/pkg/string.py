from typing import Iterator

from .std import System


class String(str):
    def equals(self, other: str) -> bool:
        return self == other
    def length(self) -> int:
        return len(self)

class BaseString(String):
    ORIGIN: str = ""