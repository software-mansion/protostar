from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
from pytest_mock import MockerFixture

from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.utils.config.project import Project


@pytest.mark.asyncio
@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_deploying_contract(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    compiled_contract_filepath,
):
    project_mock = mocker.MagicMock()
    cast(Project, project_mock).project_root = project_root_path
    deploy_command = DeployCommand(project_mock)

    args = SimpleNamespace()
    args.compiled_contract = compiled_contract_filepath
    args.gateway_url = devnet_gateway_url
    args.inputs = ["42"]
    args.network = None
    args.token = None
    args.salt = None

    response = await deploy_command.run(args)

    assert response["address"] is not None
