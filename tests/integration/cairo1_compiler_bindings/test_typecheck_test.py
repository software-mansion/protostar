from pathlib import Path

import pytest

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo_exceptions import CairoBindingException


def test_typecheck_basic(datadir: Path):
    test_collector_output = cairo1.collect_tests(datadir / "test_basic.cairo")
    assert test_collector_output.sierra_output
    assert test_collector_output.named_tests


def test_typecheck_with_args(datadir: Path):
    with pytest.raises(
        CairoBindingException, match=r"Invalid number of parameters for test"
    ):
        test_collector_output = cairo1.collect_tests(datadir / "test_with_args.cairo")
        assert test_collector_output.sierra_output
        assert test_collector_output.named_tests


def test_typecheck_with_return_values(datadir: Path):
    with pytest.raises(
        CairoBindingException,
        match=r"returns a value",
    ):
        test_collector_output = cairo1.collect_tests(
            datadir / "test_with_ret_vals.cairo"
        )
        assert test_collector_output.sierra_output
        assert test_collector_output.named_tests


def test_typecheck_with_no_panic(datadir: Path):
    with pytest.raises(CairoBindingException, match=r"must be panicable but it's not"):
        test_collector_output = cairo1.collect_tests(
            datadir / "test_with_no_panic.cairo"
        )
        assert test_collector_output.sierra_output
        assert test_collector_output.named_tests


def test_typecheck_without_panic(datadir: Path):
    with pytest.raises(CairoBindingException, match=r"must be panicable but it's not"):
        test_collector_output = cairo1.collect_tests(
            datadir / "test_without_panic.cairo"
        )
        assert test_collector_output.sierra_output
        assert test_collector_output.named_tests
