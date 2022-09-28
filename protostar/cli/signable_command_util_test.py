from pathlib import Path
from types import SimpleNamespace
from typing import List

import pytest
from starknet_py.net.models import StarknetChainId, Transaction
from starknet_py.net.models.typed_data import TypedData
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner

from protostar.cli.signable_command_util import (
    SignableCommandUtil,
    PRIVATE_KEY_ENV_VAR_NAME,
)
from protostar.protostar_exception import ProtostarException


@pytest.fixture(name="pkey_file_factory")
def pkey_file_factory_fixture(tmpdir):
    def factory(pkey: str) -> Path:
        pkey_file_path = tmpdir / "tmpfile.pkey"
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

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        return [1, 2]


def test_custom_signer_class(mocker):
    args = SimpleNamespace()

    logger = mocker.MagicMock()
    network_config = mocker.MagicMock()
    class_path = "protostar.cli.signable_command_util_test.CustomSigner"

    args.signer_class = class_path
    args.private_key_path = None
    args.account_address = None

    signer = SignableCommandUtil(args, logger).get_signer(network_config)
    assert isinstance(signer, CustomSigner)


def test_default_signer_class(pkey_file_factory, mocker):
    args = SimpleNamespace()

    logger = mocker.MagicMock()
    network_config = mocker.MagicMock()
    network_config.chain_id = StarknetChainId.TESTNET.value

    args.signer_class = None
    args.private_key_path = str(pkey_file_factory("0x123"))
    args.account_address = "0x123"

    signer = SignableCommandUtil(args, logger).get_signer(network_config)
    assert isinstance(signer, StarkCurveSigner)


def test_wrong_format_of_private_key_env(monkeypatch, mocker):
    args = SimpleNamespace()

    logger = mocker.MagicMock()
    network_config = mocker.MagicMock()
    network_config.chain_id = StarknetChainId.TESTNET.value

    args.signer_class = None
    args.private_key_path = None
    args.account_address = "0x123"

    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, "thisiswrong")
    with pytest.raises(ProtostarException) as p_exc:
        SignableCommandUtil(args, logger).get_signer(network_config)

    assert "Invalid private key format" in p_exc.value.message


def test_wrong_format_of_private_key_file(mocker, pkey_file_factory):
    args = SimpleNamespace()

    logger = mocker.MagicMock()
    network_config = mocker.MagicMock()
    network_config.chain_id = StarknetChainId.TESTNET.value

    args.signer_class = None
    args.private_key_path = str(pkey_file_factory("thisisplainlywrong"))
    args.account_address = "0x123"

    with pytest.raises(ProtostarException) as p_exc:
        SignableCommandUtil(args, logger).get_signer(network_config)

    assert "Invalid private key format" in p_exc.value.message


def test_account_wrong_format(mocker, pkey_file_factory):
    args = SimpleNamespace()

    logger = mocker.MagicMock()
    network_config = mocker.MagicMock()
    network_config.chain_id = StarknetChainId.TESTNET.value

    args.signer_class = None
    args.private_key_path = str(pkey_file_factory("0x123"))
    args.account_address = "thisisplainlywrong"

    with pytest.raises(ProtostarException) as p_exc:
        SignableCommandUtil(args, logger).get_signer(network_config)

    assert "Invalid account address format" in p_exc.value.message
