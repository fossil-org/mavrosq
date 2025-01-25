def public__style(content: str) -> str:
    return str(content)\
    .replace("$red$", "\033[31m")\
    .replace("$green$", "\033[32m")\
    .replace("$yellow$", "\033[33m")\
    .replace("$blue$", "\033[34m")\
    .replace("$magenta$", "\033[35m")\
    .replace("$cyan$", "\033[36m")\
    .replace("$white$", "\033[37m")\
    .replace("$bold$", "\033[1m")\
    .replace("$reset$", "\033[0m")\
    + "\033[0m"
def public__paint(content: str, style: str) -> str:
    return public__style(f"${style}${content}")
def public__print(content: str) -> None:
    print(public__style(content))