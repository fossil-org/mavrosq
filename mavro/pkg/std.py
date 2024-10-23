from types import ModuleType as requirement
from typing import Any as any # NOQA
from typing import Any as unknown # NOQA
from typing import Callable as callable # NOQA
true: True = True
false: False = False
null: None = None
class baseclass:
    def __starter__(self, *_, **__) -> None:
        raise NotImplementedError(f"{type(self).__name__.removeprefix("public__")} doesn't define a starter method, and therefore cannot be started.")