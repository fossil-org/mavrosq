from .remote import Base as _Base

class BaseInteger(_Base, int):
    ORIGIN: int = 0
    def toInt(self) -> int:
        return self.to(int)