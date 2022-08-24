import pytest
from .gateway_response import (
    SuccessfulDeclareResponse,
    SuccessfulDeployResponse,
    format_successful_declare_response,
    format_successful_deploy_response,
)


@pytest.mark.parametrize(
    "test_input",
    [
        SuccessfulDeployResponse("", 123, 456),
        SuccessfulDeployResponse("", 0, 0),
        SuccessfulDeployResponse("", 123, 123),
    ],
)
def test_deploy_response_formatting(test_input: SuccessfulDeployResponse):
    formatted = format_successful_deploy_response(test_input).split("\n")
    assert formatted[0] == "Deploy transaction was sent."

    address = formatted[1][formatted[1].find(":") + 1 :].strip()
    transaction_hash = formatted[2][formatted[2].find(":") + 1 :].strip()

    assert address == f"0x{test_input.address:064x}"
    assert int(address, 16) == test_input.address

    assert transaction_hash == f"0x{test_input.transaction_hash:064x}"
    assert int(transaction_hash, 16) == test_input.transaction_hash


@pytest.mark.parametrize(
    "test_input",
    [
        SuccessfulDeclareResponse("", 123, 456),
        SuccessfulDeclareResponse("", 0, 0),
        SuccessfulDeclareResponse("", 123, 123),
    ],
)
def test_declare_response_formatting(test_input: SuccessfulDeclareResponse):
    formatted = format_successful_declare_response(test_input).split("\n")
    assert formatted[0] == "Declare transaction was sent."

    class_hash = formatted[1][formatted[1].find(":") + 1 :].strip()
    transaction_hash = formatted[2][formatted[2].find(":") + 1 :].strip()

    assert class_hash == f"0x{test_input.class_hash:064x}"
    assert int(class_hash, 16) == test_input.class_hash

    assert transaction_hash == f"0x{test_input.transaction_hash:064x}"
    assert int(transaction_hash, 16) == test_input.transaction_hash
