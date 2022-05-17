# pylint: disable=consider-using-with
import subprocess
import time
from distutils.file_util import copy_file
from pathlib import Path
from socket import socket as Socket

import pytest


def get_available_port() -> int:
    with Socket() as socket:
        socket.bind(("", 0))
        return socket.getsockname()[1]


@pytest.fixture(name="devnet_gateway_url")
def devnet_gateway_url_fixture():
    devnet_port = get_available_port()

    command = [
        "poetry",
        "run",
        "starknet-devnet",
        "--host",
        "localhost",
        "--port",
        str(devnet_port),
    ]
    # pylint: disable=consider-using-with
    proc = subprocess.Popen(command)
    time.sleep(5)
    yield f"http://localhost:{devnet_port}"
    proc.kill()


@pytest.fixture(name="output_path")
def output_path_fixture(tmpdir) -> Path:
    return Path(tmpdir)


@pytest.fixture(name="compiled_contract_file")
def compiled_contract_file_fixture(output_path):
    copy_file(
        str(Path(__file__).parent / "data" / "main.json"),
        str(output_path / "main.json"),
    )

    file_handle = open(output_path / "main.json", "r", encoding="utf_8")
    yield file_handle
    file_handle.close()
