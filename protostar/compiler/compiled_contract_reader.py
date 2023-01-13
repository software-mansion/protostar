import json
from pathlib import Path

from starkware.starknet.public.abi import AbiType


def load_abi(abi_path: Path) -> AbiType:
    assert abi_path.suffix == ".json"
    return json.loads(abi_path.read_text())
