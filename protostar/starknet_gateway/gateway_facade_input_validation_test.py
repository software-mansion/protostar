import pytest
from .gateway_facade_input_validation import (
    JSONParsingErrorException,
    validate_deploy_input,
    InvalidInputException,
    get_abi_from_json,
)

COMPILED_CONTRACT_ABI_ONLY = """
{
    "abi": [
        {
            "members": [
                {
                    "name": "felt_field",
                    "offset": 0,
                    "type": "felt"
                },
                {
                    "name": "inner_field",
                    "offset": 1,
                    "type": "InnerStruct"
                }
            ],
            "name": "Test",
            "size": 4,
            "type": "struct"
        },
        {
            "members": [
                {
                    "name": "a",
                    "offset": 0,
                    "type": "felt"
                },
                {
                    "name": "b",
                    "offset": 1,
                    "type": "felt"
                },
                {
                    "name": "c",
                    "offset": 2,
                    "type": "felt"
                }
            ],
            "name": "InnerStruct",
            "size": 3,
            "type": "struct"
        },
        {
            "members": [
                {
                    "name": "low",
                    "offset": 0,
                    "type": "felt"
                },
                {
                    "name": "high",
                    "offset": 1,
                    "type": "felt"
                }
            ],
            "name": "Uint256",
            "size": 2,
            "type": "struct"
        },
        {
            "inputs": [
                {
                    "name": "amount",
                    "type": "felt"
                }
            ],
            "name": "increase_balance",
            "outputs": [],
            "type": "function"
        },
        {
            "inputs": [],
            "name": "get_balance",
            "outputs": [
                {
                    "name": "res",
                    "type": "felt"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "arg",
                    "type": "Test"
                },
                {
                    "name": "felt_arg",
                    "type": "felt"
                },
                {
                    "name": "uint256_arg",
                    "type": "Uint256"
                },
                {
                    "name": "felt_list_arg_len",
                    "type": "felt"
                },
                {
                    "name": "felt_list_arg",
                    "type": "felt*"
                },
                {
                    "name": "inst_list_arg_len",
                    "type": "felt"
                },
                {
                    "name": "inst_list_arg",
                    "type": "InnerStruct*"
                }
            ],
            "name": "constructor",
            "outputs": [],
            "type": "constructor"
        }
    ]
}
"""

COMPILED_CONTRACT_ABI_ONLY_NO_INPUTS = """
{
    "abi": [
        {
            "inputs": [],
            "name": "constructor",
            "outputs": [],
            "type": "constructor"
        }
    ]
}
"""

COMPILED_CONTRACT_ABI_ONLY_NO_CONSTRUCTOR = """
{
    "abi": []
}
"""


def test_validating_deploy_inputs_pass():
    inputs = [
        0x0,  # Test.felt_field
        0xA,  # Test.inner_field.a
        0xB,  # Test.inner_field.b
        0xC,  # Test.inner_field.c
        0x9,  # felt_arg
        0x1,  # Uint256.low
        0x2,  # Uint256.high
        5,  # len(felt_list_arg)
        0xA,  # |
        0xB,  # |
        0xC,  # |
        0xD,  # |
        0xE,  # | felt* (felt_list_arg)
        2,  # len(inst_list_arg)
        0xA,  # inst_list_arg[0].a
        0xB,  # inst_list_arg[0].b
        0xC,  # inst_list_arg[0].c
        0x1,  # inst_list_arg[1].a
        0x2,  # inst_list_arg[1].b
        0x3,  # inst_list_arg[1].c
    ]

    validate_deploy_input(COMPILED_CONTRACT_ABI_ONLY, inputs)


def test_validating_deploy_inputs_not_enough():
    inputs = [
        0x0,  # Test.felt_field
        0xA,  # Test.inner_field.a
        0xB,  # Test.inner_field.b
        0xC,  # Test.inner_field.c
        0x9,  # felt_arg
        0x1,  # Uint256.low
        0x2,  # Uint256.high
        999,  # len(felt_list_arg) !!!
        0xA,  # |
        0xB,  # |
        0xC,  # |
        0xD,  # |
        0xE,  # | felt* (felt_list_arg)
        2,  # len(inst_list_arg)
        0xA,  # inst_list_arg[0].a
        0xB,  # inst_list_arg[0].b
        0xC,  # inst_list_arg[0].c
        0x1,  # inst_list_arg[1].a
        0x2,  # inst_list_arg[1].b
        0x3,  # inst_list_arg[1].c
    ]

    with pytest.raises(InvalidInputException) as exc:
        validate_deploy_input(COMPILED_CONTRACT_ABI_ONLY, inputs)
    assert "Not enough constructor arguments provided." in str(exc.value)


def test_validating_deploy_inputs_too_many():
    inputs = [
        0x0,  # Test.felt_field
        0xA,  # Test.inner_field.a
        0xB,  # Test.inner_field.b
        0xC,  # Test.inner_field.c
        0x9,  # felt_arg
        0x1,  # Uint256.low
        0x2,  # Uint256.high
        5,  # len(felt_list_arg)
        0xA,  # |
        0xB,  # |
        0xC,  # |
        0xD,  # |
        0xE,  # | felt* (felt_list_arg)
        2,  # len(inst_list_arg)
        0xA,  # inst_list_arg[0].a
        0xB,  # inst_list_arg[0].b
        0xC,  # inst_list_arg[0].c
        0x1,  # inst_list_arg[1].a
        0x2,  # inst_list_arg[1].b
        0x3,  # inst_list_arg[1].c
        #
        0xDDDDDDDDDDDDD,
        0xDEADBEEF,
    ]

    with pytest.raises(InvalidInputException) as exc:
        validate_deploy_input(COMPILED_CONTRACT_ABI_ONLY, inputs)
    assert "Too many constructor arguments provided." in str(exc.value)


def test_validating_deploy_inputs_empty_not_enough():
    with pytest.raises(InvalidInputException) as exc:
        validate_deploy_input(COMPILED_CONTRACT_ABI_ONLY, [])
    assert "Not enough constructor arguments provided." in str(exc.value)


def test_validating_deploy_inputs_empty_pass():
    validate_deploy_input(COMPILED_CONTRACT_ABI_ONLY_NO_INPUTS, [])


def test_validating_deploy_inputs_too_many_on_empty():
    inputs = [1, 2, 3, 4, 5]

    with pytest.raises(InvalidInputException) as exc:
        validate_deploy_input(COMPILED_CONTRACT_ABI_ONLY_NO_INPUTS, inputs)
    assert "Too many constructor arguments provided." in str(exc.value)


def test_validating_deploy_no_constructor_no_input():
    validate_deploy_input(COMPILED_CONTRACT_ABI_ONLY_NO_CONSTRUCTOR, [])


def test_validating_deploy_no_constructor_input():
    inputs = [1, 2, 3, 4, 5]

    with pytest.raises(InvalidInputException) as exc:
        validate_deploy_input(COMPILED_CONTRACT_ABI_ONLY_NO_CONSTRUCTOR, inputs)
    assert "Too many constructor arguments provided." in str(exc.value)


def test_abi_from_json_parsing_error():
    with pytest.raises(JSONParsingErrorException) as exc:
        get_abi_from_json("I LOVE CAIRO")
    assert "Couldn't parse given contract JSON." in str(exc.value)


def test_abi_from_json_key_error():
    with pytest.raises(JSONParsingErrorException) as exc:
        get_abi_from_json('{"Definitely not ABI": []}')
    assert "No ABI found in the given compiled contract." in str(exc.value)
