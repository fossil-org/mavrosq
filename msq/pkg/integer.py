from .remote import Base

class BaseInteger(Base, int):
    ORIGIN: int = 0