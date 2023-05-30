CairoShortString = int


def short_string_to_str(value: CairoShortString) -> str:
    """
    Reverse of starkware.cairo.lang.compiler.test_utils.short_string_to_felt
    """
    return value.to_bytes(length=32, byteorder="big").decode("ascii").lstrip("\x00")
