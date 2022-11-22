from dataclasses import dataclass

from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner

from protostar.starknet import Address

from .devnet_account import DevnetAccount
from .faucet_contract import FaucetContract


@dataclass
class PreparedDevnetAccount(DevnetAccount):
    class_hash: int


class DevnetAccountPreparator:
    def __init__(
        self,
        compiled_account_contract: str,
        predeployed_account_client: AccountClient,
        faucet_contract: FaucetContract,
    ) -> None:
        self._compiled_account_contract = compiled_account_contract
        self._predeployed_account_client = predeployed_account_client
        self._faucet_contract = faucet_contract

    async def prepare(self, salt: int, private_key: int) -> PreparedDevnetAccount:
        class_hash = await self._declare()
        key_pair = KeyPair.from_private_key(private_key)

        address = Address.from_class_hash(
            class_hash=class_hash, constructor_calldata=[key_pair.public_key], salt=salt
        )
        await self._prefund(address)
        return PreparedDevnetAccount(
            class_hash=class_hash,
            address=Address.from_class_hash(
                class_hash=class_hash,
                constructor_calldata=[key_pair.public_key],
                salt=salt,
            ),
            private_key=str(key_pair.private_key),
            public_key=str(key_pair.public_key),
            signer=StarkCurveSigner(
                account_address=str(address),
                key_pair=key_pair,
                chain_id=StarknetChainId.TESTNET,
            ),
        )

    async def _declare(self) -> int:
        declare_tx = await self._predeployed_account_client.sign_declare_transaction(
            compiled_contract=self._compiled_account_contract,
            max_fee=int(1e16),
        )
        resp = await self._predeployed_account_client.declare(transaction=declare_tx)
        await self._predeployed_account_client.wait_for_tx(resp.transaction_hash)
        return resp.class_hash

    async def _prefund(self, account_address: Address):
        await self._faucet_contract.transfer(
            recipient=account_address, amount=int(1e15)
        )
