import os, shutil

from pathlib import Path as PlPath
from .std import System
from .string import String

class WsPath(System.BaseClass):
    def __init__(self, path: str) -> None:
        super().__init__()
        self.__path: str = path
    def to(self, *path: str) -> "WsPath":
        return WsPath(os.path.join(self.__path, *path))
    def back(self, times: int = 1) -> "WsPath":
        path: str = self.__path
        for _ in range(times):
            path = str(PlPath(path).parent)
        return WsPath(path)
    def isDirectory(self) -> bool:
        return os.path.isdir(self.__path)
    def isFile(self) -> bool:
        return not self.isDirectory()
    def public__read(self) -> String:
        with open(self.__path) as file:
            content: str = file.read()
        return String(content)
    def public__write(self, s: str) -> None:
        with open(self.__path, "w") as file:
            file.write(s)
    def public__append(self, s: str) -> None:
        with open(self.__path, "a") as file:
            file.write(s)
    def public__rm(self) -> None:
        os.remove(self.__path)
    def public__mkdir(self) -> None:
        os.mkdir(self.__path)
    def public__rmdir(self) -> None:
        shutil.rmtree(self.__path)
    def toString(self) -> String:
        return String(self.__path)
    def __str__(self) -> str:
        return str(self.toString())

class Workspace(System.BaseClass):
    def public__getPath(self, *path: str) -> WsPath:
        return WsPath(os.path.join(os.path.abspath("."), *path))
    def public__getRes(self, *path: str) -> WsPath:
        return self.public__getPath("res", *path)
    def public__getPathFromRoot(self, *path: str) -> WsPath:
        return WsPath(os.path.join("C:\\" if os.name == "nt" else "/", *path))
    def __str__(self) -> str:
        return str(self.public__getPath())