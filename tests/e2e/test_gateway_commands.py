import json
import re
from distutils.file_util import copy_file
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch
from starkware.starknet.definitions.general_config import StarknetChainId

from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from tests.conftest import Credentials
from tests.e2e.conftest import ProtostarFixture


@pytest.mark.usefixtures("init")
def test_deploying_and_calling_contract(
    protostar: ProtostarFixture, devnet_gateway_url: str, datadir: Path
):
    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"),
        dst="./src/main.cairo",
    )
    protostar(["build"])

    result = protostar(
        [
            "deploy",
            "./build/main.json",
            "--inputs",
            "0x42",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
        ]
    )

    assert "Deploy transaction was sent" in result
    assert re.search(r"Transaction hash: 0x[0-9a-f]{64}", result), result

    m = re.search(r"Contract address: (0x[0-9a-f]{64})", result)
    assert m, result
    contract_address = m[1]

    result = protostar(
        [
            "--no-color",
            "call",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
            "--contract-address",
            contract_address,
            "--function",
            "get_balance",
        ],
        ignore_stderr=True,
    )

    assert (
        result
        == """\
Call successful.
Response:
{
    "res": 66
}
"""
    )

    result = protostar(
        [
            "call",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
            "--contract-address",
            contract_address,
            "--function",
            "get_balance",
            "--json",
        ],
        ignore_stderr=True,
    )

    assert result == '{"res":66}\n'


@pytest.mark.usefixtures("init")
@pytest.mark.parametrize("protostar_version", ["0.0.0"])
def test_deploying_contract_with_constructor_and_inputs_defined_in_config_file(
    protostar: ProtostarFixture, devnet_gateway_url: str, datadir: Path
):
    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"),
        dst="./src/main.cairo",
    )
    copy_file(
        src=str(datadir / "protostar_toml_with_constructor_args.toml"),
        dst="./protostar.toml",
    )
    protostar(["build"])

    result = protostar(
        [
            "--no-color",
            "deploy",
            "./build/main.json",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
        ]
    )

    assert "Deploy transaction was sent" in result
    assert count_hex64(result) == 2


@pytest.mark.usefixtures("init")
def test_declaring_contract(
    protostar: ProtostarFixture, devnet_gateway_url: str, datadir: Path
):
    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"),
        dst="./src/main.cairo",
    )
    protostar(["build"])

    result = protostar(
        [
            "--no-color",
            "declare",
            "./build/main.json",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
        ]
    )

    assert "Declare transaction was sent" in result
    assert count_hex64(result) == 2


@pytest.mark.usefixtures("init")
def test_declaring_contract_with_signature(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    datadir: Path,
    signing_credentials: Credentials,
    monkeypatch: MonkeyPatch,
):
    private_key, account_address = signing_credentials

    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"),
        dst="./src/main.cairo",
    )
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)

    protostar(["build"])

    result = protostar(
        [
            "--no-color",
            "declare",
            "./build/main.json",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
            "--account-address",
            account_address,
            "--max-fee",
            "auto",
        ]
    )

    assert "Declare transaction was sent" in result
    assert count_hex64(result) == 2


@pytest.mark.usefixtures("init")
def test_invoke_command_is_available(protostar: ProtostarFixture):
    assert "Sends an invoke transaction" in protostar(
        ["--no-color", "invoke", "--help"]
    )


@pytest.mark.usefixtures("init")
def test_deploy_account_is_available(protostar: ProtostarFixture):
    assert "Sends deploy-account transaction" in protostar(
        ["--no-color", "deploy-account", "--help"]
    )


@pytest.mark.usefixtures("init")
def test_calculate_account_address_is_available(protostar: ProtostarFixture):
    def run(json: bool):
        optionals = []
        if json:
            optionals.append("--json")
        return protostar(
            [
                "--no-color",
                "calculate-account-address",
                "--account-class-hash",
                "1",
                "--account-address-salt",
                "1",
                *optionals,
            ]
        )

    human_output = run(json=False)
    json_output = run(json=True)

    assert "0x033f7162354afe9442cc91d8f62a09613d33558c9fcdaf8a97912895e3f7ce93" in (
        human_output
    )
    assert (
        '{"account_address":"0x033f7162354afe9442cc91d8f62a09613d33558c9fcdaf8a97912895e3f7ce93"}'
    ) in json_output


def count_hex64(x: str) -> int:
    return len(re.findall(r"0x[0-9a-f]{64}", x))
