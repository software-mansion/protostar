import json
import re
import shutil
import os
from distutils.file_util import copy_file
from pathlib import Path

import pytest
from re_assert import Matches
from starkware.starknet.definitions.general_config import StarknetChainId

from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.e2e.conftest import ProtostarFixture

HASH = Matches(r"0x[0-9a-f]{64}")


@pytest.mark.usefixtures("init_cairo0")
def test_deploying_and_interacting_with_contract(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    datadir: Path,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"),
        dst="./src/main.cairo",
    )

    protostar(["build-cairo0"])
    with set_private_key_env_var(devnet_account.private_key):
        result = protostar(
            [
                "--no-color",
                "declare",
                "./build/main.json",
                "--gateway-url",
                devnet_gateway_url,
                "--account-address",
                str(devnet_account.address),
                "--max-fee",
                "auto",
                "--chain-id",
                str(StarknetChainId.TESTNET.value),
                "--json",
            ],
            ignore_stderr=True,
        )
        class_hash = json.loads(result)["class_hash"]

        result = protostar(
            [
                "--no-color",
                "deploy",
                class_hash,
                "--inputs",
                "0x42",
                "--gateway-url",
                devnet_gateway_url,
                "--account-address",
                str(devnet_account.address),
                "--max-fee",
                "auto",
                "--chain-id",
                str(StarknetChainId.TESTNET.value),
                "--json",
            ],
            ignore_stderr=True,
        )

        response_dict = json.loads(result)
        assert "contract_address" in response_dict
        contract_address = response_dict["contract_address"]

        assert re.compile(r"0x[0-9a-f]{64}").match(contract_address)

        result = protostar(
            [
                "--no-color",
                "invoke",
                "--gateway-url",
                devnet_gateway_url,
                "--chain-id",
                str(StarknetChainId.TESTNET.value),
                "--account-address",
                str(devnet_account.address),
                "--max-fee",
                "auto",
                "--contract-address",
                contract_address,
                "--function",
                "increase_balance",
                "--inputs",
                "100",
                "--json",
            ],
            ignore_stderr=True,
        )
        messages = [json.loads(msg) for msg in result.splitlines()]
        assert {"type": "INVOKE_TRANSACTION_SENT", "transaction_hash": HASH} in messages

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

    assert json.loads(result) == {
        "raw_output": [166],
        "transformed_output": {"res": 166},
    }


@pytest.mark.usefixtures("init_cairo0")
@pytest.mark.parametrize("protostar_version", ["0.0.0"])
def test_deploying_contract_with_constructor_and_inputs_defined_in_config_file(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    datadir: Path,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    devnet_account: DevnetAccount,
):
    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"),
        dst="./src/main.cairo",
    )
    copy_file(
        src=str(datadir / "protostar_toml_with_constructor_args.toml"),
        dst="./protostar.toml",
    )
    protostar(["build-cairo0"])

    with set_private_key_env_var(devnet_account.private_key):
        result = protostar(
            [
                "--no-color",
                "declare",
                "./build/main.json",
                "--gateway-url",
                devnet_gateway_url,
                "--account-address",
                str(devnet_account.address),
                "--max-fee",
                "auto",
                "--chain-id",
                str(StarknetChainId.TESTNET.value),
                "--json",
            ],
            ignore_stderr=True,
        )

        class_hash = json.loads(result)["class_hash"]

        result = protostar(
            [
                "--no-color",
                "deploy",
                class_hash,
                "--gateway-url",
                devnet_gateway_url,
                "--account-address",
                str(devnet_account.address),
                "--max-fee",
                "auto",
                "--chain-id",
                str(StarknetChainId.TESTNET.value),
                "--json",
            ],
            ignore_stderr=True,
        )

    assert {
        "contract_address": HASH,
        "transaction_hash": HASH,
    } == json.loads(result)


@pytest.mark.usefixtures("init_cairo0")
def test_declaring_contract(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    datadir: Path,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    devnet_account: DevnetAccount,
):
    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"),
        dst="./src/main.cairo",
    )
    protostar(["build-cairo0"])
    with set_private_key_env_var(devnet_account.private_key):
        result = protostar(
            [
                "--no-color",
                "declare",
                "./build/main.json",
                "--gateway-url",
                devnet_gateway_url,
                "--account-address",
                str(devnet_account.address),
                "--max-fee",
                "auto",
                "--chain-id",
                str(StarknetChainId.TESTNET.value),
                "--json",
            ],
            ignore_stderr=True,
        )

    assert json.loads(result) == {
        "class_hash": HASH,
        "transaction_hash": HASH,
    }


def test_declaring_cairo1_contract(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    datadir: Path,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    devnet_account: DevnetAccount,
):
    shutil.copytree(datadir / "cairo1_project", "cairo1_project")
    os.chdir("cairo1_project")

    with set_private_key_env_var(devnet_account.private_key):
        result = protostar(
            [
                "--no-color",
                "declare-cairo1",
                "balance",
                "--gateway-url",
                devnet_gateway_url,
                "--account-address",
                str(devnet_account.address),
                "--max-fee",
                "auto",
                "--chain-id",
                str(StarknetChainId.TESTNET.value),
                "--json",
            ],
            ignore_stderr=True,
        )

    assert json.loads(result) == {
        "class_hash": HASH,
        "transaction_hash": HASH,
    }


def test_deploy_account_is_available(protostar: ProtostarFixture):
    assert "Sends deploy-account transaction" in protostar(
        ["--no-color", "deploy-account", "--help"]
    )


def test_calculate_account_address_is_available(protostar: ProtostarFixture):
    def run(structured_format: bool):
        optionals = []
        if structured_format:
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
            ],
            ignore_stderr=True,
        )

    human_output = run(structured_format=False)
    json_output = run(structured_format=True)

    assert (
        "Address: 0x033f7162354afe9442cc91d8f62a09613d33558c9fcdaf8a97912895e3f7ce93\n"
        == human_output
    )

    assert json.loads(json_output) == {
        "address": "0x033f7162354afe9442cc91d8f62a09613d33558c9fcdaf8a97912895e3f7ce93"
    }


def test_multicall_command_is_available(protostar: ProtostarFixture):
    assert (
        "Execute multiple deploy (via UDC) or invoke calls in a single transaction ensuring atomicity"
        in protostar(["--no-color", "multicall", "--help"])
    )
