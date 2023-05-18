from typing import Callable, Optional, List

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers.transaction_info import (
    TransactionInfoController,
)
from protostar.starknet import Address


class StartSpoofHintLocal(CallableHintLocal):
    def __init__(self, transaction_info_controller: TransactionInfoController):
        self._transaction_info_controller = transaction_info_controller

    @property
    def name(self) -> str:
        return "start_spoof_impl"

    def _build(self) -> Callable:
        return self.start_spoof

    def start_spoof(
        self,
        contract_address: int,
        version: Optional[int],
        account_contract_address: Optional[int],
        max_fee: Optional[int],
        signature: Optional[List[int]],
        transaction_hash: Optional[int],
        chain_id: Optional[int],
        nonce: Optional[int],
    ):
        address = Address(contract_address)

        if version is not None:
            self._transaction_info_controller.set_version_for_contract(address, version)

        if account_contract_address is not None:
            self._transaction_info_controller.set_account_contract_address_for_contract(
                address, account_contract_address
            )

        if max_fee is not None:
            self._transaction_info_controller.set_max_fee_for_contract(address, max_fee)

        if signature is not None:
            self._transaction_info_controller.set_signature_for_contract(
                address, signature
            )

        if transaction_hash is not None:
            self._transaction_info_controller.set_transaction_hash_for_contract(
                address, transaction_hash
            )

        if chain_id is not None:
            self._transaction_info_controller.set_chain_id_for_contract(
                address, chain_id
            )

        if nonce is not None:
            self._transaction_info_controller.set_nonce_for_contract(address, nonce)
