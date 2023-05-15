from pathlib import Path
import pytest

import protostar.cairo.cairo_bindings as cairo1


def test_contract_to_casm(datadir: Path):
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        datadir / "basic_starknet_project"
    )
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        datadir / "test_starknet_project"
    )


def test_contract_to_sierra_to_casm(datadir: Path):
    cairo1.compile_starknet_contract_to_sierra_from_path(
        input_path=datadir / "basic_starknet_project",
        output_path=datadir / "basic_starknet_project.sierra",
    )
    cairo1.compile_starknet_contract_to_sierra_from_path(
        input_path=datadir / "test_starknet_project",
        output_path=datadir / "test_starknet_project.sierra",
    )
    assert cairo1.compile_starknet_contract_sierra_to_casm_from_path(
        datadir / "basic_starknet_project.sierra"
    )
    assert cairo1.compile_starknet_contract_sierra_to_casm_from_path(
        datadir / "test_starknet_project.sierra"
    )


def test_contract_with_builtins_to_casm(datadir: Path):
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        datadir / "builtins_starknet_project"
    )


def test_cairo_path_for_starknet_contract(datadir: Path, shared_datadir: Path):
    assert cairo1.compile_starknet_contract_to_casm_from_path(
        input_path=datadir / "deps_starknet_project",
        maybe_cairo_paths=[(shared_datadir / "external_lib_foo", "external_lib_foo")],
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
        maybe_cairo_paths=[
            (shared_datadir / "external_lib_foo", "external_lib_foo"),
            (shared_datadir / "external_lib_bar", "external_lib_bar"),
        ],
    )

    with pytest.raises(Exception):
        cairo1.compile_starknet_contract_to_casm_from_path(
            input_path=datadir / "nested_deps_starknet_project",
        )

    with pytest.raises(Exception):
        cairo1.compile_starknet_contract_to_casm_from_path(
            input_path=datadir / "nested_deps_starknet_project",
            maybe_cairo_paths=[
                (shared_datadir / "external_lib_bar", "external_lib_bar")
            ],
        )
