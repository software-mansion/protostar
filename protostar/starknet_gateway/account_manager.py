from dataclasses import dataclass

from starknet_py.net.signer import BaseSigner
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.client_models import Call as SNCall

from protostar.starknet import Address
from protostar.protostar_exception import ProtostarException

from .gateway_facade import Fee
from .multicall.multicall_protocols import UnsignedMulticallTransaction
from .multicall import SignedMulticallTransaction, MulticallAccountManagerProtocol
from .account_tx_version_detector import AccountTxVersionDetector


@dataclass
class Account:
    private_key: int
    address: Address
    signer: BaseSigner


class AccountManager(MulticallAccountManagerProtocol):
    def __init__(
        self,
        account: Account,
        max_fee: Fee,
        gateway_url: str,
    ):
        self._account = account
        self._max_fee = max_fee
        gateway_client = GatewayClient(gateway_url)
        self._account_tx_version_detector = AccountTxVersionDetector(gateway_client)
        self._account_client = AccountClient(
            address=int(account.address),
            client=gateway_client,
            signer=account.signer,
            key_pair=KeyPair.from_private_key(account.private_key),
            supported_tx_version=1,
        )

    def get_account_address(self):
        return Address(self._account_client.address)

    async def sign_multicall_transaction(
        self, unsigned_transaction: UnsignedMulticallTransaction
    ) -> SignedMulticallTransaction:
        await self._ensure_account_is_valid()
        tx = await self._account_client.sign_invoke_transaction(
            calls=[
                SNCall(
                    to_addr=int(call.address),
                    selector=int(call.selector),
                    calldata=call.calldata,
                )
                for call in unsigned_transaction.calls
            ],
            max_fee=self._max_fee if isinstance(self._max_fee, int) else None,
            auto_estimate=self._max_fee == "auto",
            version=1,
        )
        return SignedMulticallTransaction(
            contract_address=Address(tx.contract_address),
            calldata=tx.calldata,
            max_fee=tx.max_fee,
            nonce=tx.nonce,
            signature=tx.signature,
        )

    async def _ensure_account_is_valid(self):
        actual_account_version = await self._account_tx_version_detector.detect(
            self._account.address
        )
        if actual_account_version != self._account_client.supported_tx_version:
            raise UnsupportedAccountVersionException(actual_account_version)


class UnsupportedAccountVersionException(ProtostarException):
    def __init__(self, version: int):
        super().__init__(message=f"Unsupported account version: {version}")
