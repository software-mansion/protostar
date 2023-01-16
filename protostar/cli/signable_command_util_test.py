import re
from pathlib import Path
from types import SimpleNamespace
from typing import List, Callable, Union

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock import MockerFixture
from starknet_py.net.models import StarknetChainId, Transaction
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.utils.typed_data import TypedData

from protostar.starknet import Address
from protostar.cli.signable_command_util import (
    SignableCommandUtil,
    PRIVATE_KEY_ENV_VAR_NAME,
)
from protostar.protostar_exception import ProtostarException

PkeyFileFactoryFixture = Callable[[str], Path]


@pytest.fixture(name="pkey_file_factory")
def pkey_file_factory_fixture(tmp_path: Path) -> PkeyFileFactoryFixture:
    def factory(pkey: str) -> Path:
        pkey_file_path = tmp_path / "tmpfile.pkey"
        with open(pkey_file_path, mode="w+", encoding="utf-8") as file:
            file.write(pkey)
        return pkey_file_path

    return factory


class CustomSigner(BaseSigner):
    @property
    def public_key(self):
        return 1

    def sign_transaction(self, transaction: Transaction) -> List[int]:
        return [1, 2]

    def sign_message(
        self, typed_data: Union[dict, TypedData], account_address: int
    ) -> List[int]:
        return [1, 2]


def test_custom_signer_class(mocker: MockerFixture):
    args = SimpleNamespace()

    network_config = mocker.MagicMock()
    class_path = "protostar.cli.signable_command_util_test.CustomSigner"

    args.signer_class = class_path
    args.private_key_path = None
    args.account_address = None

    signer = SignableCommandUtil(args).get_signer(network_config)
    assert isinstance(signer, CustomSigner)


def test_default_signer_class(
    pkey_file_factory: PkeyFileFactoryFixture, mocker: MockerFixture
):
    args = SimpleNamespace()

    network_config = mocker.MagicMock()
    network_config.chain_id = StarknetChainId.TESTNET.value

    args.signer_class = None
    args.private_key_path = str(pkey_file_factory("0x123"))
    args.account_address = Address.from_user_input("0x123")

    signer = SignableCommandUtil(args).get_signer(network_config)
    assert isinstance(signer, StarkCurveSigner)


def test_wrong_format_of_private_key_env(
    monkeypatch: MonkeyPatch, mocker: MockerFixture
):
    args = SimpleNamespace()

    network_config = mocker.MagicMock()
    network_config.chain_id = StarknetChainId.TESTNET.value

    args.signer_class = None
    args.private_key_path = None
    args.account_address = "0x123"

    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, "thisiswrong")
    with pytest.raises(
        ProtostarException, match=re.escape("Invalid private key format")
    ):
        SignableCommandUtil(args).get_signer(network_config)


def test_wrong_format_of_private_key_file(
    mocker: MockerFixture, pkey_file_factory: PkeyFileFactoryFixture
):
    args = SimpleNamespace()

    network_config = mocker.MagicMock()
    network_config.chain_id = StarknetChainId.TESTNET.value

    args.signer_class = None
    args.private_key_path = str(pkey_file_factory("thisisplainlywrong"))
    args.account_address = "0x123"

    with pytest.raises(
        ProtostarException, match=re.escape("Invalid private key format")
    ):
        SignableCommandUtil(args).get_signer(network_config)


def test_account_wrong_format(
    mocker: MockerFixture, pkey_file_factory: PkeyFileFactoryFixture
):
    args = SimpleNamespace()

    network_config = mocker.MagicMock()
    network_config.chain_id = StarknetChainId.TESTNET.value

    args.signer_class = None
    args.private_key_path = str(pkey_file_factory("0x123"))
    args.account_address = "thisisplainlywrong"

    with pytest.raises(
        ProtostarException, match=re.escape("Invalid account address format")
    ):
        SignableCommandUtil(args).get_signer(network_config)
