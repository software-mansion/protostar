from starknet_py.net.signer import BaseSigner
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.client_models import Call as SNCall

from protostar.starknet import Address
from protostar.starknet_gateway.gateway_facade import Fee
from protostar.starknet_gateway.multicall.multicall_protocols import (
    InvokeUnsignedTransaction,
)

from .multicall import InvokeSignedTransaction, AccountManagerProtocol


class AccountManager(AccountManagerProtocol):
    def __init__(
        self,
        private_key: int,
        address: Address,
        signer: BaseSigner,
        gateway_url: str,
        max_fee: Fee,
    ):
        self._private_key = private_key
        self._signer = signer
        self._max_fee = max_fee
        gateway_client = GatewayClient(gateway_url)
        self._account_client = AccountClient(
            address=int(address),
            client=gateway_client,
            signer=signer,
            key_pair=KeyPair.from_private_key(private_key),
        )

    def get_account_address(self):
        return Address(self._account_client.address)

    async def sign_invoke_transaction(
        self, unsigned_transaction: InvokeUnsignedTransaction
    ) -> InvokeSignedTransaction:
        tx = await self._account_client.sign_invoke_transaction(
            calls=SNCall(
                calldata=unsigned_transaction.calldata,
                to_addr=int(unsigned_transaction.contract_address),
                selector=int(unsigned_transaction.selector),
            ),
            max_fee=self._max_fee if isinstance(self._max_fee, int) else None,
            auto_estimate=self._max_fee == "auto",
            version=self._account_client.supported_tx_version,
        )
        assert tx.nonce is not None
        return InvokeSignedTransaction.from_unsigned(
            unsigned_transaction,
            max_fee=tx.max_fee,
            nonce=tx.nonce,
            signature=tx.signature,
        )
