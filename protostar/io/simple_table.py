from typing import Any


def format_as_table(data: dict[str, Any]) -> str:
    max_key_length = 0
    for key in data:
        if len(key) > max_key_length:
            max_key_length = len(key)
    lines = [
        f"{key.ljust(max_key_length)}: {str(value)}" for key, value in data.items()
    ]
    return "\n".join(lines)
