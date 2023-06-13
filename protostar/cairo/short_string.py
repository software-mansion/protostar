CairoShortString = int

LAST_ASCII_CHAR_DEC_VAL = 127


def short_string_to_str(value: CairoShortString) -> str:
    """
    Reverse of starkware.cairo.lang.compiler.test_utils.short_string_to_felt
    """
    return _to_bytes(value).decode("ascii").lstrip("\x00")


def is_decodable_to_ascii(value: int) -> bool:
    for byte in _to_bytes(value):
        if byte > LAST_ASCII_CHAR_DEC_VAL:
            return False
    return True


def _to_bytes(value: int) -> bytes:
    return value.to_bytes(length=32, byteorder="big")
