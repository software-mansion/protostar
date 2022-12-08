def format_as_table(data: dict) -> list[str]:
    max_key_length = max({len(str(key)) for key in data})
    lines = [
        f"{str(key).ljust(max_key_length)}: {str(value)}" for key, value in data.items()
    ]
    return lines
