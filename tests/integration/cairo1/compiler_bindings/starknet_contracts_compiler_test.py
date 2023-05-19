from pathlib import Path
import pytest

import protostar.cairo.bindings.cairo_bindings as cairo1


def test_contract_to_casm(datadir: Path):
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "basic_starknet_project"
    )
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "test_starknet_project"
    )

    basic_starknet_project_casm_path = datadir / "basic_starknet_project.casm"
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "basic_starknet_project",
        output_path=basic_starknet_project_casm_path,
    )
    assert basic_starknet_project_casm_path.exists()
    assert basic_starknet_project_casm_path.read_text()

    test_starknet_project_casm_path = datadir / "test_starknet_project.casm"
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "test_starknet_project",
        output_path=test_starknet_project_casm_path,
    )
    assert test_starknet_project_casm_path.exists()
    assert test_starknet_project_casm_path.read_text()


def test_contract_to_sierra_to_casm_from_sierra_code(datadir: Path):
    basic_sierra_compiled = cairo1.compile_starknet_contract_to_sierra_from_path(
        input_path=datadir / "basic_starknet_project",
        output_path=datadir / "basic_starknet_project.sierra",
    )
    test_sierra_compiled = cairo1.compile_starknet_contract_to_sierra_from_path(
        input_path=datadir / "test_starknet_project",
        output_path=datadir / "test_starknet_project.sierra",
    )
    basic_casm = cairo1.compile_starknet_contract_sierra_to_casm_from_sierra_code(
        basic_sierra_compiled
    )
    test_casm = cairo1.compile_starknet_contract_sierra_to_casm_from_sierra_code(
        test_sierra_compiled
    )

    assert basic_casm == cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "basic_starknet_project"
    )
    assert test_casm == cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "test_starknet_project"
    )


def test_contract_to_sierra_to_casm_from_path(datadir: Path):
    assert cairo1.compile_starknet_contract_to_sierra_from_path(
        input_path=datadir / "basic_starknet_project",
        output_path=datadir / "basic_starknet_project.sierra",
    )
    assert cairo1.compile_starknet_contract_to_sierra_from_path(
        input_path=datadir / "test_starknet_project",
        output_path=datadir / "test_starknet_project.sierra",
    )
    basic_starknet_casm = cairo1.compile_starknet_contract_sierra_to_casm_from_path(
        datadir / "basic_starknet_project.sierra"
    )
    test_starknet_casm = cairo1.compile_starknet_contract_sierra_to_casm_from_path(
        datadir / "test_starknet_project.sierra"
    )
    assert basic_starknet_casm == cairo1.compile_starknet_contract_to_casm_from_path(
        datadir / "basic_starknet_project"
    )
    assert test_starknet_casm == cairo1.compile_starknet_contract_to_casm_from_path(
        datadir / "test_starknet_project"
    )


def test_contract_with_builtins_to_casm(datadir: Path):
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        datadir / "builtins_starknet_project"
    )


def test_cairo_path_for_starknet_contract(datadir: Path, shared_datadir: Path):
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "deps_starknet_project",
        cairo_path=[shared_datadir / "external_lib_foo"],
    )

    with pytest.raises(Exception):
        cairo1.compile_starknet_contract_to_casm_from_path(
            input_path=datadir / "deps_starknet_project",
        )


def test_cairo_path_for_starknet_contract_nested_deps(
    datadir: Path, shared_datadir: Path
):
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "nested_deps_starknet_project",
        cairo_path=[
            shared_datadir / "external_lib_foo",
            shared_datadir / "external_lib_bar",
        ],
    )

    with pytest.raises(Exception):
        cairo1.compile_starknet_contract_to_casm_from_path(
            input_path=datadir / "nested_deps_starknet_project",
        )

    with pytest.raises(Exception):
        cairo1.compile_starknet_contract_to_casm_from_path(
            input_path=datadir / "nested_deps_starknet_project",
            cairo_path=[shared_datadir / "external_lib_bar"],
        )
