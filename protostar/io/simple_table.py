def format_as_table(data: dict) -> list[str]:
    max_key_length = 0
    for key in data:
        key_str = str(key)
        if len(key_str) > max_key_length:
            max_key_length = len(key_str)
    lines = [
        f"{str(key).ljust(max_key_length)}: {str(value)}" for key, value in data.items()
    ]
    return lines
