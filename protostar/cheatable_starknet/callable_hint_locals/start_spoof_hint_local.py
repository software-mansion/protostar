from typing import Callable, Optional, List

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)


class StartSpoofHintLocal(CallableHintLocal):
    @property
    def name(self) -> str:
        return "start_spoof_impl"

    def _build(self) -> Callable:
        return self.start_spoof

    def start_spoof(
        self,
        version: Optional[int],
        account_contract_address: Optional[int],
        max_fee: Optional[int],
        signature: Optional[List[int]],
        transaction_hash: Optional[int],
        chain_id: Optional[int],
        nonce: Optional[int],
    ):
        pass
