import subprocess
import time
from socket import socket as Socket
from typing import List

import pytest
import requests
from starknet_py.net import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer import BaseSigner

from protostar.cli.signable_command_util import PatchedStarkCurveSigner


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
        "--accounts",  # deploys specified number of accounts
        str(1),
        "--seed",  # generates same accounts each time
        str(1),
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
    if proc.stdout:
        appended_stdout = f"stdout: {proc.stdout.read()}"

    raise RuntimeError(
        f"Devnet failed to start on port {port}" + (appended_stdout or "")
    )


@pytest.fixture(name="devnet_port", scope="session")
def devnet_port_fixture() -> int:
    with Socket() as socket:
        socket.bind(("", 0))
        return socket.getsockname()[1]


@pytest.fixture(name="signing_credentials", scope="module")
def signing_credentials_fixture():  # The same account is generated each time
    testnet_account_private_key = "0xcd613e30d8f16adf91b7584a2265b1f5"
    testnet_account_address = (
        "0x7d2f37b75a5e779f7da01c22acee1b66c39e8ba470ee5448f05e1462afcedb4"
    )
    return (
        testnet_account_private_key,
        testnet_account_address,
    )


@pytest.fixture(name="signer", scope="module")
def signer_fixture(signing_credentials) -> BaseSigner:
    private_key, account_address = signing_credentials
    return PatchedStarkCurveSigner(
        account_address,
        KeyPair.from_private_key(int(private_key, 16)),
        StarknetChainId.TESTNET.value,
    )
