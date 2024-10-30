from typing import Iterator

from .std import System as _System
from .remote import Base as _Base


class String:
    def __init__(self, content: str | None = None) -> None:
        self.__content: str = content or ""
    def __str__(self) -> str:
        return self.__content
    def __getattr__(self, name: str) -> any:
        return getattr(self.__content, name)
    def __iter__(self) -> Iterator[str]:
        return self.__content.__iter__()
    def __add__(self, other: str) -> str:
        return self.__content + other
    def __mul__(self, other: int) -> str:
        return self.__content * other
    def print(self, value: str, console) -> None:
        console.public__print(value.replace("$$", self.__content))
    def __starter__(self) -> None:
        _System.BaseClass.__starter__(self) # NOQA

class BaseString(_Base, String):
    ORIGIN: str = ""
    def toStr(self) -> str:
        return self.to(str)