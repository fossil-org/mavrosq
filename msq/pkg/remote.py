from typing import Any as Any

from .std import System


class Base(System.BaseClass):
    ORIGIN: Any = None
    def __init__(self) -> None:
        super().__init__()
    def __int__(self) -> int:
        return int(self.ORIGIN)
    def __str__(self) -> str:
        return str(self.ORIGIN)