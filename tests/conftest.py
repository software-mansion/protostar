import subprocess
import time
from socket import socket as Socket
from typing import List

import pytest


def run_devnet(devnet: List[str], port: int) -> subprocess.Popen:
    command = devnet + [
        "--host",
        "localhost",
        "--port",
        str(port),
    ]
    # pylint: disable=consider-using-with
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    time.sleep(5)

    return proc


@pytest.fixture(name="devnet_port")
def devnet_port_fixture() -> int:
    with Socket() as socket:
        socket.bind(("", 0))
        return socket.getsockname()[1]
