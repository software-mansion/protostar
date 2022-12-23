from typing import Any


def tokenize(positional_args: list[Any], named_args: dict[str, Any]):
    tokens = [str(item) for item in positional_args if item is not None]
    for name, value in named_args.items():
        if value is None:
            continue
        if isinstance(value, bool):
            if value:
                tokens.append(f"--{name}")
            continue
        tokens.append(f"--{name}")
        if isinstance(value, list):
            tokens += [str(item) for item in value]
            continue
        tokens.append(str(value))
    return tokens
