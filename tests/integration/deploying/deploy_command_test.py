from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
from pytest_mock import MockerFixture

from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.utils.config.project import Project


@pytest.mark.asyncio
@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
@pytest.mark.usefixtures("compiled_contract_filepath")
async def test_deploying_contract(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    output_dir: Path,
):
    project_mock = mocker.MagicMock()
    cast(Project, project_mock).project_root = project_root_path
    deploy_command = DeployCommand(project_mock)

    args = SimpleNamespace()
    args.contract = "main_with_constructor"
    args.gateway_url = devnet_gateway_url
    args.build_output = output_dir
    args.inputs = ["42"]
    args.network = None
    args.token = None
    args.salt = None

    response = await deploy_command.run(args)

    assert response.address is not None
