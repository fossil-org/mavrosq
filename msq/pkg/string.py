from typing import Iterator

from .std import System
from .remote import Base


class String(str):
    def equals(self, other: str) -> bool:
        return self == other
    def length(self) -> int:
        return len(self)

class BaseString(Base, String):
    ORIGIN: str = ""
    def toStr(self) -> str:
        return self.to(str)