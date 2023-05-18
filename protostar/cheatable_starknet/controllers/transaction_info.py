from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from starkware.starknet.definitions.general_config import StarknetChainId

from protostar.starknet import Address

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
        CheatableCachedState,
    )


@dataclass
class TxInfo:
    version: int
    account_contract_address: int
    max_fee: int
    signature: List[int]
    transaction_hash: int
    chain_id: int
    nonce: int


class TransactionInfoController:
    def __init__(self, cheatable_state: "CheatableCachedState"):
        self.state = cheatable_state

    def get_for_contract(self, contract_address: Address) -> TxInfo:
        return TxInfo(
            version=self.state.contract_address_to_version.get(contract_address, 1),
            account_contract_address=self.state.contract_address_to_account_contract_address.get(
                contract_address, 0
            ),
            max_fee=self.state.contract_address_to_max_fee.get(contract_address, 0),
            signature=self.state.contract_address_to_signature.get(
                contract_address, []
            ),
            transaction_hash=self.state.contract_address_to_transaction_hash.get(
                contract_address, 0
            ),
            # TODO verify if this is a good default value
            chain_id=self.state.contract_address_to_chain_id.get(
                contract_address, StarknetChainId.TESTNET.value
            ),
            nonce=self.state.contract_address_to_nonce.get(contract_address, 0),
        )

    def set_for_contract(self, contract_address: Address, tx_info: TxInfo):
        self.set_version_for_contract(contract_address, tx_info.version)
        self.set_account_contract_address_for_contract(
            contract_address, tx_info.account_contract_address
        )
        self.set_max_fee_for_contract(contract_address, tx_info.max_fee)
        self.set_signature_for_contract(contract_address, tx_info.signature)
        self.set_transaction_hash_for_contract(
            contract_address, tx_info.transaction_hash
        )
        self.set_chain_id_for_contract(contract_address, tx_info.chain_id)
        self.set_nonce_for_contract(contract_address, tx_info.nonce)

    def set_version_for_contract(self, contract_address: Address, version: int):
        self.state.contract_address_to_version[contract_address] = version

    def set_account_contract_address_for_contract(
        self, contract_address: Address, account_contract_address: int
    ):
        self.state.contract_address_to_account_contract_address[
            contract_address
        ] = account_contract_address

    def set_max_fee_for_contract(self, contract_address: Address, max_fee: int):
        self.state.contract_address_to_max_fee[contract_address] = max_fee

    def set_signature_for_contract(
        self, contract_address: Address, signature: List[int]
    ):
        self.state.contract_address_to_signature[contract_address] = signature

    def set_transaction_hash_for_contract(
        self, contract_address: Address, transaction_hash: int
    ):
        self.state.contract_address_to_transaction_hash[
            contract_address
        ] = transaction_hash

    def set_chain_id_for_contract(self, contract_address: Address, chain_id: int):
        self.state.contract_address_to_chain_id[contract_address] = chain_id

    def set_nonce_for_contract(self, contract_address: Address, nonce: int):
        self.state.contract_address_to_nonce[contract_address] = nonce
