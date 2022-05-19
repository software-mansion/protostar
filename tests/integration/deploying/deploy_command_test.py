from pathlib import Path
from typing import cast

import pytest
from pytest_mock import MockerFixture

from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.utils.config.project import Project


@pytest.mark.asyncio
@pytest.mark.usefixtures("compiled_contract_file")
async def test_deploying_contract(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    output_path: Path,
):
    project_mock = mocker.MagicMock()
    cast(Project, project_mock).project_root = project_root_path
    deploy_command = DeployCommand(project_mock)

    response = await deploy_command.deploy(
        contract_name="main", gateway_url=devnet_gateway_url, output_dir=output_path
    )

    assert response.address is not None
