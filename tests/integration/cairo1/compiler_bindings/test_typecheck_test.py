from pathlib import Path

import pytest

import protostar.cairo.bindings.cairo_bindings as cairo1
from protostar.cairo.bindings.cairo_bindings import CairoBindingException


def test_typecheck_basic(datadir: Path):
    test_collector_output = cairo1.collect_tests(
        input_path=datadir / "test_basic.cairo",
        maybe_cairo_paths=[(datadir / "test_basic.cairo", "test_basic")],
    )
    assert test_collector_output.sierra_output
    assert test_collector_output.collected_tests


def test_typecheck_with_args(datadir: Path):
    with pytest.raises(
        CairoBindingException, match=r"Invalid number of parameters for test"
    ):
        test_collector_output = cairo1.collect_tests(
            input_path=datadir / "test_with_args.cairo",
            maybe_cairo_paths=[(datadir / "test_with_args.cairo", "test_with_args")],
        )
        assert test_collector_output.sierra_output
        assert test_collector_output.collected_tests


def test_typecheck_with_return_values(datadir: Path):
    with pytest.raises(
        CairoBindingException,
        match=r"returns a value",
    ):
        test_collector_output = cairo1.collect_tests(
            input_path=datadir / "test_with_ret_vals.cairo",
            maybe_cairo_paths=[
                (datadir / "test_with_ret_vals.cairo", "test_with_ret_vals")
            ],
        )
        assert test_collector_output.sierra_output
        assert test_collector_output.collected_tests


def test_typecheck_with_no_panic(datadir: Path):
    with pytest.raises(CairoBindingException, match=r"must be panicable but it's not"):
        test_collector_output = cairo1.collect_tests(
            input_path=datadir / "test_with_no_panic.cairo",
            maybe_cairo_paths=[
                (datadir / "test_with_no_panic.cairo", "test_with_no_panic")
            ],
        )
        assert test_collector_output.sierra_output
        assert test_collector_output.collected_tests


def test_typecheck_without_panic(datadir: Path):
    with pytest.raises(CairoBindingException, match=r"must be panicable but it's not"):
        test_collector_output = cairo1.collect_tests(
            input_path=datadir / "test_without_panic.cairo",
            maybe_cairo_paths=[
                (datadir / "test_without_panic.cairo", "test_without_panic")
            ],
        )
        assert test_collector_output.sierra_output
        assert test_collector_output.collected_tests
