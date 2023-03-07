from pathlib import Path

import pytest

import protostar.cairo.cairo_bindings as cairo1


def test_typecheck_basic(datadir: Path):
    test_collector_output = cairo1.collect_tests(datadir / "test_basic.cairo")
    assert test_collector_output.sierra_output
    assert test_collector_output.test_names


def test_typecheck_with_args(datadir: Path):
    with pytest.raises(RuntimeError, match=r"Invalid number of parameters for test"):
        test_collector_output = cairo1.collect_tests(datadir / "test_with_args.cairo")
        assert test_collector_output.sierra_output
        assert test_collector_output.test_names


def test_typecheck_with_return_values(datadir: Path):
    with pytest.raises(
        RuntimeError,
        match=r"returns a value, it is required that test functions do not return values",
    ):
        test_collector_output = cairo1.collect_tests(
            datadir / "test_with_ret_vals.cairo"
        )
        assert test_collector_output.sierra_output
        assert test_collector_output.test_names


def test_typecheck_with_no_panic(datadir: Path):
    # TODO this should raise an error!!
    # with pytest.raises(RuntimeError, match=r"..."):
    test_collector_output = cairo1.collect_tests(datadir / "test_with_no_panic.cairo")
    assert test_collector_output.sierra_output
    assert test_collector_output.test_names
