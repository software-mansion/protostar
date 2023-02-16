from pathlib import Path
from typing import Callable
import pytest

from protostar.cairo.cairo_bindings import (
    call_starknet_contract_compiler,
)

def test_cairo_to_sierra_to_casm(datadir: Path):
    result = call_starknet_contract_compiler(
        datadir / "basic_starknet_contract.cairo",
    )
    assert result
    result = call_starknet_contract_compiler(
        datadir / "basic_starknet_test.cairo"
    )
    assert result