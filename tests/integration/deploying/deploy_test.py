# pylint: disable=consider-using-with
import subprocess
import time
from pathlib import Path
from socket import socket as Socket

import pytest

from protostar.commands.deploy.starkware.starknet_cli import deploy


@pytest.fixture(name="devnet_gateway_port", scope="session")
def devnet_gateway_port_fixture() -> int:
    with Socket() as socket:
        socket.bind(("", 0))
        return socket.getsockname()[1]


@pytest.fixture(name="devnet_gateway_url", scope="session")
def devnet_gateway_url_fixture(devnet_gateway_port: int):
    command = [
        "poetry",
        "run",
        "starknet-devnet",
        "--host",
        "localhost",
        "--port",
        str(devnet_gateway_port),
    ]
    # pylint: disable=consider-using-with
    proc = subprocess.Popen(command)
    time.sleep(5)
    yield f"http://localhost:{devnet_gateway_port}"
    proc.kill()


@pytest.fixture(name="compiled_contract_file")
def compiled_contract_file_fixture(shared_datadir: Path):
    file_handle = open(shared_datadir / "main.json", "r", encoding="utf_8")
    yield file_handle
    file_handle.close()


@pytest.mark.asyncio
async def test_deploying_contract(devnet_gateway_url: str, compiled_contract_file):
    response = await deploy(
        gateway_url=devnet_gateway_url, compiled_contract_file=compiled_contract_file
    )

    assert response["address"] is not None
