from pathlib import Path
import pytest

import protostar.cairo.cairo_bindings as cairo1


def test_contract_to_casm(datadir: Path):
    result = cairo1.compile_starknet_contract_from_path(
        datadir / "basic_starknet_contract.cairo",
    )
    assert result
    result = cairo1.compile_starknet_contract_from_path(
        datadir / "basic_starknet_test.cairo"
    )
    assert result


def test_cairo_path_for_starknet_contract(datadir: Path, shared_datadir: Path):
    casm_contents = cairo1.compile_starknet_contract_from_path(
        input_path=datadir / "starknet_project" / "basic_starknet_contract.cairo",
        cairo_path=[shared_datadir / "external_lib_foo"],
    )
    assert casm_contents

    with pytest.raises(Exception):
        cairo1.compile_starknet_contract_from_path(
            input_path=datadir / "starknet_project" / "basic_starknet_contract.cairo",
        )


def test_cairo_path_for_starknet_contract_nested_deps(
    datadir: Path, shared_datadir: Path
):
    casm_contents = cairo1.compile_starknet_contract_from_path(
        input_path=datadir
        / "starknet_project"
        / "basic_starknet_contract_nested_deps.cairo",
        cairo_path=[
            shared_datadir / "external_lib_foo",
            shared_datadir / "external_lib_bar",
        ],
    )
    assert casm_contents

    with pytest.raises(Exception):
        cairo1.compile_starknet_contract_from_path(
            input_path=datadir / "starknet_project" / "basic_starknet_contract.cairo"
        )

    with pytest.raises(Exception):
        cairo1.compile_starknet_contract_from_path(
            input_path=datadir / "starknet_project" / "basic_starknet_contract.cairo",
            cairo_path=[shared_datadir / "external_lib_bar"],
        )
