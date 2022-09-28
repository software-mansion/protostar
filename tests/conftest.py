import json
import subprocess
import time
from dataclasses import dataclass
from socket import socket as Socket
from typing import List, NamedTuple

import pytest
import requests
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner

from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME


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


Credentials = NamedTuple(
    "Credentials", [("private_key", str), ("account_address", str)]
)


@pytest.fixture(name="signing_credentials", scope="module")
def signing_credentials_fixture() -> Credentials:  # The same account is generated each time
    testnet_account_private_key = "0xcd613e30d8f16adf91b7584a2265b1f5"
    testnet_account_address = (
        "0x7d2f37b75a5e779f7da01c22acee1b66c39e8ba470ee5448f05e1462afcedb4"
    )
    return Credentials(
        testnet_account_private_key,
        testnet_account_address,
    )


@dataclass
class DevnetAccount:
    address: str
    private_key: str
    public_key: str
    signer: StarkCurveSigner


@pytest.fixture(name="devnet_accounts")
def devnet_accounts_fixture(devnet_gateway_url: str) -> list[DevnetAccount]:
    response = requests.get(f"{devnet_gateway_url}/predeployed_accounts")
    devnet_account_dicts = json.loads(response.content)
    return [
        DevnetAccount(
            address=devnet_account_dict["address"],
            private_key=devnet_account_dict["private_key"],
            public_key=devnet_account_dict["public_key"],
            signer=StarkCurveSigner(
                account_address=devnet_account_dict["address"],
                key_pair=KeyPair(
                    private_key=int(devnet_account_dict["private_key"], base=16),
                    public_key=int(devnet_account_dict["public_key"], base=16),
                ),
                chain_id=StarknetChainId.TESTNET,
            ),
        )
        for devnet_account_dict in devnet_account_dicts
    ]


@pytest.fixture(name="alice_devnet_account")
def alice_devnet_account(
    devnet_accounts: list[DevnetAccount], monkeypatch: pytest.MonkeyPatch
) -> DevnetAccount:
    alice_devnet_account = devnet_accounts[0]
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, alice_devnet_account.private_key)
    return alice_devnet_account
