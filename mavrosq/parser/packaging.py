from enum import Enum, auto
from importlib import import_module
from types import ModuleType
from typing import Any


class PackageImportType(Enum):
    WILDCARD = auto()
    FROM = auto()
    STD = auto()
    AS = auto()


class Package:
    def __init__(self, name: str, origin: str | None = None) -> None:
        self.name: str = name
        self.origin: str | None = origin
    def __repr__(self) -> str:
        return f"{self.origin.replace("/", ".").replace("\\", ".")}.{self.name}"
    def getImportStatement(self, import_type: PackageImportType, arg: str) -> str:
        match import_type:
            case PackageImportType.WILDCARD:
                return f"from {repr(self)} import *"
            case PackageImportType.FROM:
                return f"from {repr(self)} import {arg}"
            case PackageImportType.STD:
                return f"import {repr(self)}"
            case PackageImportType.AS:
                return f"import {repr(self)} as {arg}"
            case _:
                raise ValueError(f"Unsupported or incorrect import type: {import_type}")
    def getModule(self) -> ModuleType | Exception:
        try: return import_module(repr(self), __package__)
        except ModuleNotFoundError: return ImportError(f"Package '{self.name}' from origin '{self.origin}' does not exist.")
    def getModuleItem(self, item: str) -> Any | Exception:
        module: ModuleType | Exception = self.getModule()
        if isinstance(module, Exception):
            raise module
        if hasattr(module, item):
            return getattr(module, item)
        else:
            return AttributeError(f"Package '{self.name}' from origin '{self.origin}' does not have an attribute with the name '{item}'.")