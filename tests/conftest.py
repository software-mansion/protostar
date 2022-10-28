import json
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from socket import socket as Socket
from typing import ContextManager, List, NamedTuple, Protocol, Union

import pkg_resources
import pytest
import requests
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner

from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from tests._conftest.compiled_account import read_compiled_account_contract

from ._conftest import DevnetAccountPreparator, FaucetContract

MAX_FEE = int(1e20)


def ensure_devnet_alive(
    port: int, retries: int = 5, base_backoff_time: float = 2
) -> bool:
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


@pytest.fixture(name="devnet_account")
def devnet_account(devnet_accounts: list[DevnetAccount]) -> DevnetAccount:
    return devnet_accounts[0]


class SetPrivateKeyEnvVarFixture(Protocol):
    def __call__(self, private_key: str) -> ContextManager[None]:
        ...


@pytest.fixture(name="set_private_key_env_var")
def set_private_key_env_var_fixture(
    monkeypatch: pytest.MonkeyPatch,
) -> SetPrivateKeyEnvVarFixture:
    @contextmanager
    def set_private_key_env_var(private_key: str):
        monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)
        yield
        monkeypatch.delenv(PRIVATE_KEY_ENV_VAR_NAME)

    return set_private_key_env_var


PathStr = str
FileContent = str
FileStructureSchema = dict[PathStr, Union["FileStructureSchema", FileContent]]


def create_file_structure(root_path: Path, file_structure_schema: FileStructureSchema):
    for path_str, composite in file_structure_schema.items():
        if isinstance(composite, str):
            file_content = composite
            # pylint: disable=unspecified-encoding
            (root_path / Path(path_str)).write_text(file_content)
        else:
            new_root_path = root_path / Path(path_str)
            new_root_path.mkdir()
            create_file_structure(new_root_path, file_structure_schema=composite)


@pytest.fixture
def devnet_account_preparator(devnet_gateway_url: str, devnet_account: DevnetAccount):
    compiled_account_contract = read_compiled_account_contract()
    gateway_client = GatewayClient(
        devnet_gateway_url,
    )
    predeployed_account_client = AccountClient(
        address=devnet_account.address,
        client=gateway_client,
        key_pair=KeyPair(
            private_key=int(devnet_account.private_key, base=0),
            public_key=int(devnet_account.public_key, base=0),
        ),
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )
    faucet_contract = FaucetContract(
        predeployed_account_client=predeployed_account_client
    )
    return DevnetAccountPreparator(
        compiled_account_contract=compiled_account_contract,
        predeployed_account_client=predeployed_account_client,
        faucet_contract=faucet_contract,
    )
