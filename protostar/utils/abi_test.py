import pytest
from starkware.cairo.lang.compiler.ast.cairo_types import TypeFelt
from starkware.starknet.compiler.compile import compile_starknet_codes
from starkware.starknet.public.abi import AbiType

from protostar.utils.abi import (
    AbiNotFoundException,
    get_abi_from_compiled_contract,
    get_function_parameters,
    has_function_parameters,
    AbiItemNotFoundException,
)


@pytest.fixture(name="abi", scope="module")
def abi_fixture() -> AbiType:
    code = """
%lang starknet

struct Point:
    member x : felt
    member y : felt
end

@external
func test_no_args():
    return ()
end

@external
func test_fuzz{syscall_ptr : felt*, range_check_ptr}(a, b : felt):
    return ()
end
"""
    abi = compile_starknet_codes([(code, "")]).abi
    assert abi is not None
    return abi


def test_has_function_parameters(abi: AbiType):
    assert not has_function_parameters(abi, "test_no_args")
    assert has_function_parameters(abi, "test_fuzz")


def test_has_function_parameters_raises_when_function_not_found(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        has_function_parameters(abi, "foobar")


def test_has_function_parameters_raises_when_asked_for_struct(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        has_function_parameters(abi, "Point")


def test_get_function_parameters(abi: AbiType):
    assert not get_function_parameters(abi, "test_no_args")

    # Order is important here.
    parameters = get_function_parameters(abi, "test_fuzz")
    assert list(parameters.items()) == [
        ("a", TypeFelt()),
        ("b", TypeFelt()),
    ]


def test_get_function_parameters_raises_when_function_not_found(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        get_function_parameters(abi, "foobar")


def test_get_function_parameters_raises_when_asked_for_struct(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        get_function_parameters(abi, "Point")


INVALID_COMPILED_CONTRACT = "I LOVE CAIRO"


def test_get_abi_from_compiled_contract_fail_json():
    with pytest.raises(AbiNotFoundException) as ex:
        get_abi_from_compiled_contract(INVALID_COMPILED_CONTRACT)
    assert str(ex.value) == "Couldn't parse given compiled contract JSON."


COMPILED_CONTRACT_NO_ABI = "{}"


def test_get_abi_from_compiled_contract_fail_no_abi():
    with pytest.raises(AbiNotFoundException) as ex:
        get_abi_from_compiled_contract(COMPILED_CONTRACT_NO_ABI)
    assert str(ex.value) == "Couldn't find ABI of the compiled contract."
