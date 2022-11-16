import pytest

from protostar.starknet_gateway import FakeBlockExplorer, SuccessfulDeployResponse
from protostar.starknet import Address

from .deploy_command import format_successful_deploy_response


@pytest.mark.parametrize(
    "test_input",
    [
        SuccessfulDeployResponse("", Address(123), 456),
        SuccessfulDeployResponse("", Address(0), 0),
        SuccessfulDeployResponse("", Address(123), 123),
    ],
)
def test_deploy_response_formatting(test_input: SuccessfulDeployResponse):
    formatted_response = format_successful_deploy_response(
        test_input, block_explorer=FakeBlockExplorer()
    )
    assert "Deploy transaction was sent." in formatted_response
    assert str(test_input.address) in formatted_response
    assert f"0x{test_input.transaction_hash:064x}" in formatted_response
