import pytest

from protostar.starknet_gateway import FakeBlockExplorer, SuccessfulDeployResponse

from .deploy_command import format_successful_deploy_response


@pytest.mark.parametrize(
    "test_input",
    [
        SuccessfulDeployResponse("", 123, 456),
        SuccessfulDeployResponse("", 0, 0),
        SuccessfulDeployResponse("", 123, 123),
    ],
)
def test_deploy_response_formatting(test_input: SuccessfulDeployResponse):
    formatted_response = format_successful_deploy_response(
        test_input, block_explorer=FakeBlockExplorer()
    )
    assert "Deploy transaction was sent." in formatted_response
    assert f"0x{test_input.address:064x}" in formatted_response
    assert f"0x{test_input.transaction_hash:064x}" in formatted_response
