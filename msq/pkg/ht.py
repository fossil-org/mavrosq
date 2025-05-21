import os, sys, uuid
from typing import Callable

from .std import System as System
from .requiry import public__findService

class Ht(System.BaseClass):
    def __init__(self) -> None:
        super().__init__()
    def __call__(self, s: str) -> str:
        filename: str = str(uuid.uuid4())
        with open(filename, "w") as file:
            file.write("function main\n" + s + "\nend")
        try:
            main: Callable = public__findService(filename).main()
            return main
        finally:
            os.remove(filename)