from typing import Any
from .std import System

class Console(System.BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self.__activated: bool = False
    def __assertActivated(self, fn: str | None = None) -> None:
        if not self.__activated:
            raise BlockingIOError(f"Could not execute 'Console::{fn or "unknownService"}' because the Console service is not activated.")
    def __starter__(self) -> None:
        self.__activated = True
    def public__print(self, obj: Any) -> None:
        self.__assertActivated("print")
        print(obj)
    def public__reprint(self, times: int, obj: Any) -> None:
        self.__assertActivated("reprint")
        for time in range(times):
            self.public__print(obj)
    def public__input(self, obj: Any) -> str:
        self.__assertActivated("input")
        print(obj, end="")
        return input()
    def public__br(self, times: int = 1) -> None:
        self.__assertActivated("br")
        print("\n" * times, end="")