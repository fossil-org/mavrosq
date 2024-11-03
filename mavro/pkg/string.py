from typing import Iterator

from .std import System as _System
from .remote import Base as _Base


class String(str):
    def equals(self, other: str) -> bool:
        return self == other

class BaseString(_Base, String):
    ORIGIN: str = ""
    def toStr(self) -> str:
        return self.to(str)