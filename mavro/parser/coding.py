from enum import Enum


class CodeType(Enum):
    OK = 0
    ERROR = 1


def identifyCode(code: int) -> str:
    if code == CodeType.OK.value:
        return "ran normally without errors"
    elif code == CodeType.ERROR.value:
        return "failed due to a fatal error"
    else:
        return "ended with an unknown formatted code, which couldn't be identified."