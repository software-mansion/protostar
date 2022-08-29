from copy import deepcopy
from typing_extensions import Literal

import pytest

from .data_transformer import (
    DataTransformerException,
    PythonData,
    CairoData,
    from_python_transformer,
    from_python_events_transformer,
    to_python_transformer,
    to_python_events_transformer,
)

TEST_ABI = [
    {
        "members": [
            {"name": "felt_field", "offset": 0, "type": "felt"},
            {"name": "inner_field", "offset": 1, "type": "InnerStruct"},
        ],
        "name": "Test",
        "size": 4,
        "type": "struct",
    },
    {
        "members": [
            {"name": "a", "offset": 0, "type": "felt"},
            {"name": "b", "offset": 1, "type": "felt"},
            {"name": "c", "offset": 2, "type": "felt"},
        ],
        "name": "InnerStruct",
        "size": 3,
        "type": "struct",
    },
    {
        "members": [
            {"name": "low", "offset": 0, "type": "felt"},
            {"name": "high", "offset": 1, "type": "felt"},
        ],
        "name": "Uint256",
        "size": 2,
        "type": "struct",
    },
    {
        "inputs": [{"name": "amount", "type": "felt"}],
        "name": "increase_balance",
        "outputs": [],
        "type": "function",
    },
    {
        "inputs": [],
        "name": "get_balance",
        "outputs": [{"name": "res", "type": "felt"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "arg", "type": "Test"},
            {"name": "felt_arg", "type": "felt"},
            {"name": "uint256_arg", "type": "Uint256"},
            {"name": "felt_list_arg_len", "type": "felt"},
            {"name": "felt_list_arg", "type": "felt*"},
            {"name": "inst_list_arg_len", "type": "felt"},
            {"name": "inst_list_arg", "type": "InnerStruct*"},
        ],
        "name": "constructor",
        "outputs": [],
        "type": "constructor",
    },
    {
        "data": [
            {"name": "arg", "type": "Test"},
            {"name": "felt_arg", "type": "felt"},
            {"name": "uint256_arg", "type": "Uint256"},
            {"name": "felt_list_arg_len", "type": "felt"},
            {"name": "felt_list_arg", "type": "felt*"},
            {"name": "inst_list_arg_len", "type": "felt"},
            {"name": "inst_list_arg", "type": "InnerStruct*"},
        ],
        "name": "constructor_event",
        "type": "event",
        "from_address": "0",
    },
    {
        "data": [{"name": "input", "type": "(felt, felt)"}],
        "name": "tuple_event",
        "type": "event",
        "from_address": "0",
    },
]

UINT256_SINGLE = 0x00001000000000000000000000000000_00000000000000000000000000000111
UINT256_DICT = {
    "high": 0x00001000000000000000000000000000,
    "low": 0x00000000000000000000000000000111,
}

VALID_CONSTRUCTOR_PYTHON_INPUT = {
    "arg": {"felt_field": 321, "inner_field": {"a": 0xA, "b": 0xB, "c": 0xC}},
    "felt_arg": 123,
    "uint256_arg": UINT256_SINGLE,
    #    "felt_list_arg_len": 3,
    "felt_list_arg": [1, 2, 3],
    #    "inst_list_arg_len": 2,
    "inst_list_arg": [{"a": 4, "b": 5, "c": 6}, {"a": 7, "b": 8, "c": 9}],
}

VALID_CONSTRUCTOR_CAIRO_INPUT = [
    0xFE17,
    0xA,
    0xB,
    0xC,
    0xFE17_2,
    101,
    102,
    3,
    0x1,
    0x2,
    0x3,
    2,
    0xA,
    0xB,
    0xC,
    0xA2,
    0xB2,
    0xC2,
]


@pytest.mark.parametrize(
    "name,mode,data",
    [
        ["constructor", "inputs", {**VALID_CONSTRUCTOR_PYTHON_INPUT, "evil_arg": 42}],
        ["increase_balance", "outputs", {"???": 0xBAD_C0DE}],
        [
            "get_balance",
            "outputs",
            {"res": "String definitely longer than 31 characters"},
        ],
        ["get_balance", "outputs", {"res": Exception("Definitely not a valid output")}],
    ],
)
def test_from_python_fail(
    name: str, mode: Literal["inputs", "outputs"], data: PythonData
):
    with pytest.raises(DataTransformerException):
        from_python_transformer(TEST_ABI, name, mode)(data)


@pytest.mark.parametrize(
    "name,mode,data",
    [
        ["constructor", "inputs", VALID_CONSTRUCTOR_PYTHON_INPUT],
        ["increase_balance", "outputs", {}],
        ["get_balance", "outputs", {"res": 0x42}],
    ],
)
def test_from_python_pass(
    name: str, mode: Literal["inputs", "outputs"], data: PythonData
):
    from_python_transformer(TEST_ABI, name, mode)(data)


@pytest.mark.parametrize(
    "name,data",
    [
        ["constructor_event", {**VALID_CONSTRUCTOR_PYTHON_INPUT, "evil_arg": 42}],
        # ENABLE AFTER STARKNET.PY PR        ["tuple_event", {"input": (42, 24, 42)}],
        ["tuple_event", {"input": (42,)}],
    ],
)
def test_from_python_event_fail(name: str, data: PythonData):
    with pytest.raises(DataTransformerException):
        from_python_events_transformer(TEST_ABI, name)(data)


@pytest.mark.parametrize(
    "name,data",
    [
        ["constructor_event", VALID_CONSTRUCTOR_PYTHON_INPUT],
        ["tuple_event", {"input": (42, 24)}],
    ],
)
def test_from_python_event_pass(name: str, data: PythonData):
    from_python_events_transformer(TEST_ABI, name)(data)


@pytest.mark.parametrize(
    "name,mode,data",
    [
        # ENABLE AFTER STARKNET.PY PR323        ["constructor", "inputs", VALID_CONSTRUCTOR_CAIRO_INPUT + [0xBAD_C0DE]],
        # ENABLE AFTER STARKNET.PY PR323        ["increase_balance", "outputs", [1, 2, 3]],
        ["get_balance", "outputs", []],
    ],
)
def test_to_python_fail(name: str, mode: Literal["inputs", "outputs"], data: CairoData):
    with pytest.raises(DataTransformerException):
        to_python_transformer(TEST_ABI, name, mode)(data)


@pytest.mark.parametrize(
    "name,mode,data",
    [
        ["constructor", "inputs", VALID_CONSTRUCTOR_CAIRO_INPUT],
        ["increase_balance", "outputs", []],
        ["get_balance", "outputs", [0xD]],
    ],
)
def test_to_python_pass(name: str, mode: Literal["inputs", "outputs"], data: CairoData):
    to_python_transformer(TEST_ABI, name, mode)(data)


@pytest.mark.parametrize(
    "name,data",
    [
        # ENABLE AFTER STARKNET.PY PR323        ["constructor_event", VALID_CONSTRUCTOR_CAIRO_INPUT + [0xBAD_C0DE]],
        # ENABLE AFTER STARKNET.PY PR323        ["tuple_event", [1, 2, 3]],
        ["tuple_event", [1]],
    ],
)
def test_to_python_event_fail(name: str, data: CairoData):
    with pytest.raises(DataTransformerException):
        to_python_events_transformer(TEST_ABI, name)(data)


@pytest.mark.parametrize(
    "name,data",
    [
        ["constructor_event", VALID_CONSTRUCTOR_CAIRO_INPUT],
        ["tuple_event", [1, 2]],
    ],
)
def test_to_python_event_pass(name: str, data: CairoData):
    to_python_events_transformer(TEST_ABI, name)(data)


def test_data_transformer_from_python():
    from_python = from_python_transformer(TEST_ABI, "constructor", "inputs")
    to_python = to_python_transformer(TEST_ABI, "constructor", "inputs")

    python_data = VALID_CONSTRUCTOR_PYTHON_INPUT
    cairo_data = from_python(python_data)
    assert_is_int_list(cairo_data)
    python_data2 = to_python(cairo_data)

    print(python_data2["uint256_arg"], type(python_data2["uint256_arg"]))
    assert python_data == python_data2


def test_data_transformer_to_python():
    from_python = from_python_transformer(TEST_ABI, "constructor", "inputs")
    to_python = to_python_transformer(TEST_ABI, "constructor", "inputs")

    cairo_data = VALID_CONSTRUCTOR_CAIRO_INPUT
    python_data = to_python(cairo_data)
    assert isinstance(python_data, dict)
    cairo_data2 = from_python(python_data)
    assert cairo_data == cairo_data2


def test_uint256_as_2_felts():
    from_python = from_python_transformer(TEST_ABI, "constructor", "inputs")
    new_input = deepcopy(VALID_CONSTRUCTOR_PYTHON_INPUT)
    new_input["uint256_arg"] = UINT256_DICT  # type: ignore
    assert from_python(new_input) == from_python(VALID_CONSTRUCTOR_PYTHON_INPUT)


def assert_is_int_list(unknown):
    assert isinstance(unknown, list)
    assert all(isinstance(x, int) for x in unknown)
