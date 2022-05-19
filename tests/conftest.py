import subprocess
import time
from socket import socket as Socket

import pytest


@pytest.fixture(name="devnet_port")
def devnet_port_fixture() -> int:
    with Socket() as socket:
        socket.bind(("", 0))
        return socket.getsockname()[1]


@pytest.fixture(name="devnet_gateway_url")
def devnet_gateway_url_fixture(devnet_port: int):
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
