import subprocess
import time
from socket import socket as Socket
from typing import List

import pytest
import requests


def ensure_devnet_alive(port: int, retries=5, base_backoff_time=2) -> bool:
    for i in range(retries):
        try:
            res = requests.get(f"http://localhost:{port}/is_alive")
            if res.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            backoff_time = base_backoff_time * (2 ** (i - 1))  # Use exp backoff
            time.sleep(backoff_time)
    return False


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
    is_alive = ensure_devnet_alive(port)
    if is_alive:
        return proc

    appended_stdout = None
    if proc.poll():
        appended_stdout = f"stdout: {proc.stdout.read()}"

    raise RuntimeError(
        f"Devnet failed to start on port {port}" + (appended_stdout or "")
    )


@pytest.fixture(name="devnet_port")
def devnet_port_fixture() -> int:
    with Socket() as socket:
        socket.bind(("", 0))
        return socket.getsockname()[1]
