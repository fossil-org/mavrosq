from typing import Any as _Any

from .std import System as _System


class Base(_System.BaseClass):
    ORIGIN: _Any = None
    def __init__(self) -> None:
        super().__init__()
    def __int__(self) -> int:
        return self.to(int)
    def __str__(self) -> str:
        return self.to(str)
    def to(self, type_) -> _Any:
        return type_(self.ORIGIN)