from starknet_py.net.signer import BaseSigner
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.client_models import Call as SNCall

from protostar.starknet import Address
from protostar.starknet_gateway.gateway_facade import Fee
from protostar.starknet_gateway.multicall.multicall_protocols import (
    UnsignedMulticallTransaction,
)

from .multicall import SignedMulticallTransaction, MulticallAccountManagerProtocol


class AccountManager(MulticallAccountManagerProtocol):
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
            supported_tx_version=1,
        )

    def get_account_address(self):
        return Address(self._account_client.address)

    async def sign_multicall_transaction(
        self, unsigned_transaction: UnsignedMulticallTransaction
    ) -> SignedMulticallTransaction:
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
            version=self._account_client.supported_tx_version,
        )
        assert tx.nonce is not None
        return SignedMulticallTransaction(
            contract_address=Address(tx.contract_address),
            calldata=tx.calldata,
            max_fee=tx.max_fee,
            nonce=tx.nonce,
            signature=tx.signature,
        )
