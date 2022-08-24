import re
from typing import cast, Dict, Any
import pytest
from .starknet_request import StarknetRequest


@pytest.mark.parametrize(
    "test_input",
    [
        {"transaction_hash": 123, "not_hex": 0xDEADBEEF, "not_hex2": "foo"},
        {"class_hash": 456, "not_hex": 0xAD0BE_BAD, "not_hex2": "bar"},
        {"contract_address": 789, "not_hex": 42, "not_hex2": "baz"},
    ],
)
def test_payload_converting_to_hex(test_input: Dict[str, Any]):
    payload = cast(StarknetRequest.Payload, test_input)
    formatted = StarknetRequest.prettify_payload(None, payload)

    valid_hex = r"^0x[0-9a-f]{64}$"

    for key in payload.keys():
        data = formatted[formatted.find(key) + len(key) :]
        data = data[: data.find("\n")].strip()

        if key in StarknetRequest.AS_HEX:
            assert re.match(valid_hex, data)
        else:
            assert not re.match(valid_hex, data)
