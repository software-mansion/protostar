import pytest
from starkware.cairo.lang.compiler.ast.cairo_types import TypeFelt
from starkware.starknet.compiler.compile import compile_starknet_codes
from starkware.starknet.public.abi import AbiType

from protostar.utils import DataTransformerFacade
from protostar.utils.data_transformer_facade import AbiItemNotFoundException


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
    assert not DataTransformerFacade.has_function_parameters(abi, "test_no_args")
    assert DataTransformerFacade.has_function_parameters(abi, "test_fuzz")


def test_has_function_parameters_raises_when_function_not_found(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        DataTransformerFacade.has_function_parameters(abi, "foobar")


def test_has_function_parameters_raises_when_asked_for_struct(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        DataTransformerFacade.has_function_parameters(abi, "Point")


def test_get_function_parameters(abi: AbiType):
    assert not DataTransformerFacade.get_function_parameters(abi, "test_no_args")

    # Order is important here.
    parameters = DataTransformerFacade.get_function_parameters(abi, "test_fuzz")
    assert list(parameters.items()) == [
        ("a", TypeFelt()),
        ("b", TypeFelt()),
    ]


def test_get_function_parameters_raises_when_function_not_found(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        DataTransformerFacade.get_function_parameters(abi, "foobar")


def test_get_function_parameters_raises_when_asked_for_struct(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        DataTransformerFacade.get_function_parameters(abi, "Point")
