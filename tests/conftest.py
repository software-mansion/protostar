import subprocess
import time
from pathlib import Path
from socket import socket as Socket

import pytest


def run_devnet(devnet_path: Path, port: int) -> subprocess.Popen:
    command = [
        str(devnet_path),
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


@pytest.fixture(name="devnet_port", scope="session")
def devnet_port_fixture() -> int:
    with Socket() as socket:
        socket.bind(("", 0))
        return socket.getsockname()[1]
