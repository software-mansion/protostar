from pathlib import Path
from types import SimpleNamespace
from typing import List, Optional

import pytest
from starknet_py.net.models import StarknetChainId, Transaction
from starknet_py.net.models.typed_data import TypedData
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner

from protostar.cli.signable_command_util import (
    PRIVATE_KEY_ENV_VAR_NAME,
    create_account_config_from_args,
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


def create_signer(
    signer_class: Optional[str] = None,
    private_key_path: Optional[Path] = None,
    account_address: Optional[str] = None,
):
    args = SimpleNamespace()
    args.signer_class = signer_class
    args.private_key_path = private_key_path
    args.account_address = account_address
    account_config = create_account_config_from_args(
        args, chain_id=StarknetChainId.TESTNET
    )
    assert account_config is not None
    return account_config.signer


def test_custom_signer_class():
    signer = create_signer(
        signer_class="protostar.cli.signable_command_util_test.CustomSigner"
    )
    assert isinstance(signer, CustomSigner)


def test_default_signer_class(pkey_file_factory):
    signer = create_signer(
        account_address="0x123", private_key_path=pkey_file_factory("0x123")
    )
    assert isinstance(signer, StarkCurveSigner)


def test_wrong_format_of_private_key_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, "INVALID_PRIVATE_KEY")

    with pytest.raises(ProtostarException, match="Invalid private key format"):
        create_signer(account_address="0x123")


def test_wrong_format_of_private_key_file(pkey_file_factory):
    with pytest.raises(ProtostarException, match="Invalid private key format"):
        create_signer(
            account_address="0x123",
            private_key_path=pkey_file_factory("INVALID_PRIVATE_KEY"),
        )


def test_account_wrong_format(pkey_file_factory):
    with pytest.raises(ProtostarException, match="Invalid account address format"):
        create_signer(
            account_address="INVALID_ACCOUNT_ADDRESS",
            private_key_path=pkey_file_factory("0x123"),
        )
