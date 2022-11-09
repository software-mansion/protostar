from typing import Any

from typing_extensions import Literal

import pytest

from protostar.starknet.data_transformer import (
    DataTransformerException,
    PythonData,
    CairoData,
    from_python_transformer,
    from_python_events_transformer,
    to_python_transformer,
    to_python_events_transformer,
)
from tests.integration.conftest import GetAbiFromContractFixture

from tests.integration.data_transformer.contracts import (
    DATA_TRANSFORMER_FELT_CONSTRUCTOR_CONTRACT,
    DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT,
    DATA_TRANSFORMER_UINT256_CONTRACT,
    DATA_TRANSFORMER_EVENT_CONTRACT,
    DATA_TRANSFORMER_LISTS_CONTRACT,
    DATA_TRANSFORMER_STRUCTS_CONTRACT,
    DATA_TRANSFORMER_TUPLE_CONTRACT,
)


@pytest.mark.parametrize(
    "contract,function_name,mode,data",
    [
        [
            DATA_TRANSFORMER_FELT_CONSTRUCTOR_CONTRACT,
            "constructor",
            "inputs",
            {"arg": 0xD00D00},
        ],
        [
            DATA_TRANSFORMER_UINT256_CONTRACT,
            "input_uint256",
            "inputs",
            {"arg": 1 << 237},
        ],
        [
            DATA_TRANSFORMER_UINT256_CONTRACT,
            "input_uint256",
            "inputs",
            {"arg": {"high": 101, "low": 102}},
        ],
        [
            DATA_TRANSFORMER_LISTS_CONTRACT,
            "input_lists",
            "inputs",
            {
                "felt_list": [1, 2, 3, 4, 5],
                "uint256_list": [1 << 217, {"high": 1, "low": 0x47}, 7],
            },
        ],
        [
            DATA_TRANSFORMER_TUPLE_CONTRACT,
            "input_tuple",
            "inputs",
            {"arg": (535345345, 61231231223)},
        ],
        [
            DATA_TRANSFORMER_STRUCTS_CONTRACT,
            "input_outer_struct",
            "inputs",
            {"arg": {"felt_field": 13, "inner_field": {"a": 0x1, "b": 0x2, "c": 0x3}}},
        ],
        [
            DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT,
            "output_felt",
            "outputs",
            {"res": 3732423423423},
        ],
        [
            DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT,
            "output_felt",
            "inputs",
            {},
        ],
    ],
)
def test_from_python_pass(
    get_abi_from_contract: GetAbiFromContractFixture,
    contract: str,
    function_name: str,
    mode: Literal["inputs", "outputs"],
    data: PythonData,
):
    abi = get_abi_from_contract(contract)
    from_python_transformer(abi, function_name, mode)(data)


@pytest.mark.parametrize(
    "contract,function_name,mode,data",
    [
        [
            DATA_TRANSFORMER_FELT_CONSTRUCTOR_CONTRACT,
            "constructor",
            "inputs",
            {},
        ],
        [
            DATA_TRANSFORMER_UINT256_CONTRACT,
            "input_uint256",
            "inputs",
            {"arg": 1 << 579},
        ],
        [
            DATA_TRANSFORMER_UINT256_CONTRACT,
            "input_uint256",
            "inputs",
            {"arg": {"high": 101}},
        ],
        [
            DATA_TRANSFORMER_LISTS_CONTRACT,
            "input_lists",
            "inputs",
            {
                "felt_list_len": 5,
                "felt_list": [1, 2, 3, 4, 5],
                "uint256_list": [1 << 217, {"high": 1, "low": 0x47}, 7],
            },
        ],
        [
            DATA_TRANSFORMER_TUPLE_CONTRACT,
            "input_tuple",
            "inputs",
            {"arg": (535345345, 61231231223, 324234234)},
        ],
        [
            DATA_TRANSFORMER_TUPLE_CONTRACT,
            "input_tuple",
            "inputs",
            {"arg": (535345345,)},
        ],
        [
            DATA_TRANSFORMER_STRUCTS_CONTRACT,
            "input_outer_struct",
            "inputs",
            {
                "arg": {
                    "felt_field": 13,
                    "inner_field": {"a": 0x1, "b": 0x2, "c": 1 << 506},
                }
            },
        ],
        [
            DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT,
            "output_felt",
            "outputs",
            {"res": Exception("Not a valid type")},
        ],
        [
            DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT,
            "output_felt",
            "inputs",
            {"arg": 3},
        ],
    ],
)
def test_from_python_fail(
    get_abi_from_contract: GetAbiFromContractFixture,
    contract: str,
    function_name: str,
    mode: Literal["inputs", "outputs"],
    data: PythonData,
):
    abi = get_abi_from_contract(contract)
    with pytest.raises(DataTransformerException):
        from_python_transformer(abi, function_name, mode)(data)


@pytest.mark.parametrize(
    "contract,function_name,mode,data",
    [
        [
            DATA_TRANSFORMER_FELT_CONSTRUCTOR_CONTRACT,
            "constructor",
            "inputs",
            [0xD],
        ],
        [
            DATA_TRANSFORMER_UINT256_CONTRACT,
            "input_uint256",
            "inputs",
            [214324, 2325353452],
        ],
        [
            DATA_TRANSFORMER_LISTS_CONTRACT,
            "input_lists",
            "inputs",
            [
                5,  # len felt_list
                1,
                2,
                3,
                4,
                5,
                2,  # len uint256_list
                134,
                2342354235,
                123124,
                25245,
            ],
        ],
        [
            DATA_TRANSFORMER_TUPLE_CONTRACT,
            "input_tuple",
            "inputs",
            [535345345, 61231231223],
        ],
        [
            DATA_TRANSFORMER_STRUCTS_CONTRACT,
            "input_outer_struct",
            "inputs",
            [13, 1, 2, 3],
        ],
        [
            DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT,
            "output_felt",
            "outputs",
            [3732423423423],
        ],
        [
            DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT,
            "output_felt",
            "inputs",
            [],
        ],
    ],
)
def test_to_python_pass(
    get_abi_from_contract: GetAbiFromContractFixture,
    contract: str,
    function_name: str,
    mode: Literal["inputs", "outputs"],
    data: CairoData,
):
    abi = get_abi_from_contract(contract)
    to_python_transformer(abi, function_name, mode)(data)


@pytest.mark.parametrize(
    "contract,function_name,mode,data",
    [
        [
            DATA_TRANSFORMER_UINT256_CONTRACT,
            "input_uint256",
            "inputs",
            [1 << 216],
        ],
        [
            DATA_TRANSFORMER_LISTS_CONTRACT,
            "input_lists",
            "inputs",
            [
                5,  # len felt_list
                1,
                2,
                3,
                4,
                5,
                999,  # len uint256_list
                134,
                2342354235,
                123124,
                25245,
            ],
        ],
        [
            DATA_TRANSFORMER_STRUCTS_CONTRACT,
            "input_outer_struct",
            "inputs",
            [13, 3],
        ],
    ],
)
def test_to_python_fail_generic(
    get_abi_from_contract: GetAbiFromContractFixture,
    contract: str,
    function_name: str,
    mode: Literal["inputs", "outputs"],
    data: CairoData,
):
    abi = get_abi_from_contract(contract)
    with pytest.raises(DataTransformerException):
        to_python_transformer(abi, function_name, mode)(data)


@pytest.mark.skip("https://github.com/software-mansion/starknet.py/issues/325")
@pytest.mark.parametrize(
    "contract,function_name,mode,data",
    [
        [
            DATA_TRANSFORMER_FELT_CONSTRUCTOR_CONTRACT,
            "constructor",
            "inputs",
            ["very very very very long string"],
        ],
        [
            DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT,
            "output_felt",
            "outputs",
            [1 << 561],
        ],
    ],
)
def test_to_python_fail_range_check(
    get_abi_from_contract: GetAbiFromContractFixture,
    contract: str,
    function_name: str,
    mode: Literal["inputs", "outputs"],
    data: CairoData,
):
    abi = get_abi_from_contract(contract)
    with pytest.raises(DataTransformerException):
        to_python_transformer(abi, function_name, mode)(data)


@pytest.mark.skip("https://github.com/software-mansion/starknet.py/pull/323")
@pytest.mark.parametrize(
    "contract,function_name,mode,data",
    [
        [
            DATA_TRANSFORMER_FELT_CONSTRUCTOR_CONTRACT,
            "constructor",
            "inputs",
            [0x2342, 0x24],
        ],
        [
            DATA_TRANSFORMER_TUPLE_CONTRACT,
            "input_tuple",
            "inputs",
            [535345345, 61231231223, 234234243234],
        ],
    ],
)
def test_to_python_fail_too_many_args(
    get_abi_from_contract: GetAbiFromContractFixture,
    contract: str,
    function_name: str,
    mode: Literal["inputs", "outputs"],
    data: CairoData,
):
    abi = get_abi_from_contract(contract)
    with pytest.raises(DataTransformerException):
        to_python_transformer(abi, function_name, mode)(data)


def test_from_python_event_pass(get_abi_from_contract: GetAbiFromContractFixture):
    abi = get_abi_from_contract(DATA_TRANSFORMER_EVENT_CONTRACT)
    from_python_events_transformer(abi, "event1")({"arg1": 1, "arg2": 2})


def test_from_python_event_fail(get_abi_from_contract: GetAbiFromContractFixture):
    abi = get_abi_from_contract(DATA_TRANSFORMER_EVENT_CONTRACT)
    with pytest.raises(DataTransformerException):
        from_python_events_transformer(abi, "event1")({"arg1": 1, "arg47": 2})


def test_to_python_event_pass(get_abi_from_contract: GetAbiFromContractFixture):
    abi = get_abi_from_contract(DATA_TRANSFORMER_EVENT_CONTRACT)
    to_python_events_transformer(abi, "event1")([1, 2])


def test_to_python_event_fail(get_abi_from_contract: GetAbiFromContractFixture):
    abi = get_abi_from_contract(DATA_TRANSFORMER_EVENT_CONTRACT)
    with pytest.raises(DataTransformerException):
        to_python_events_transformer(abi, "event1")([1])


def test_data_transformer_from_python(get_abi_from_contract: GetAbiFromContractFixture):
    abi = get_abi_from_contract(DATA_TRANSFORMER_STRUCTS_CONTRACT)
    from_python = from_python_transformer(abi, "input_outer_struct", "inputs")
    to_python = to_python_transformer(abi, "input_outer_struct", "inputs")

    python_data = {"arg": {"felt_field": 13, "inner_field": {"a": 1, "b": 2, "c": 3}}}
    cairo_data = from_python(python_data)
    assert_is_int_list(cairo_data)
    python_data2 = to_python(cairo_data)
    assert python_data == python_data2


def test_data_transformer_to_python(get_abi_from_contract: GetAbiFromContractFixture):
    abi = get_abi_from_contract(DATA_TRANSFORMER_STRUCTS_CONTRACT)
    from_python = from_python_transformer(abi, "input_outer_struct", "inputs")
    to_python = to_python_transformer(abi, "input_outer_struct", "inputs")

    cairo_data = [0, 1, 2, 3]
    python_data = to_python(cairo_data)
    assert isinstance(python_data, dict)
    cairo_data2 = from_python(python_data)
    assert cairo_data == cairo_data2


def test_uint256_as_2_felts(get_abi_from_contract: GetAbiFromContractFixture):
    abi = get_abi_from_contract(DATA_TRANSFORMER_UINT256_CONTRACT)
    from_python = from_python_transformer(abi, "input_uint256", "inputs")

    UINT256_SINGLE = 0x00001000000000000000000000000000_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    UINT256_DICT = {
        "high": 0x00001000000000000000000000000000,
        "low": 0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,
    }

    assert from_python({"arg": UINT256_SINGLE}) == from_python({"arg": UINT256_DICT})


def assert_is_int_list(unknown: Any):
    assert isinstance(unknown, list)
    assert all(isinstance(x, int) for x in unknown)
