from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from protostar.commands.deploy.deploy_command import DeployCommand


@pytest.mark.asyncio
@pytest.mark.usefixtures("compiled_contract_file")
async def test_deploying_contract(
    mocker: MockerFixture, devnet_gateway_url: str, output_path: Path
):
    project_mock = mocker.MagicMock()
    project_mock.load_argument = mocker.MagicMock()
    project_mock.load_argument.return_value = devnet_gateway_url
    deploy_command = DeployCommand(project_mock)

    response = await deploy_command.deploy(
        contract_name="main", network="", output_dir=output_path
    )

    assert response["address"] is not None
