from typing import Any


def tokenize(positional_args: list[Any], named_args: dict[str, Any]):
    tokens: list[str] = []
    for value in positional_args:
        if value is not None:
            tokens.append(str(value))
    for name, value in named_args.items():
        if value is None:
            continue
        if isinstance(value, bool):
            if value:
                tokens.append(f"--{name}")
            continue
        tokens.append(f"--{name}")
        if isinstance(value, list):
            for val in value:
                tokens.append(str(val))
            continue
        tokens.append(str(value))
    return tokens
