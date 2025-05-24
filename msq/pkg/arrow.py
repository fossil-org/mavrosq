from typing import Any

class Arrow:
    def __init__(self) -> None:
        self.__value: Any = None
    def __add__(self, type_: type) -> Any:
        value: Any = self.__value
        self.__value = None
        return type_(value)
    def __rsub__(self, value: Any) -> "Arrow":
        self.__value = value
        return self