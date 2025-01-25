from .std import System as _System
class Console(_System.BaseClass):
    def __init__(self) -> None:
        self.__activated: bool = False
    def __assertActivated(self, fn: str | None = None) -> None:
        if not self.__activated:
            raise BlockingIOError(f"Could not execute 'Console::{fn or "unknownService"}' because the Console service is not activated.")
    def __starter__(self) -> None:
        self.__activated = True
    def public__print(self, obj: any) -> None:
        self.__assertActivated("print")
        print(obj)
    def public__input(self, obj: any) -> str:
        self.__assertActivated("input")
        print(obj, end="")
        return input()

Console = Console()