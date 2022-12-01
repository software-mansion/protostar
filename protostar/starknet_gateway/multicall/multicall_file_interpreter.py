import tomlkit as toml

from .multicall_structs import CallBase


def interpret_multicall_file_content(toml_content: str) -> list[CallBase]:
    doc = toml.loads(toml_content)
    calls = doc.get("calls")
    return []
