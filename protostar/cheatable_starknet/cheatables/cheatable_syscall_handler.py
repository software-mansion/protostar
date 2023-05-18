from typing import cast

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.python.utils import as_non_optional
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.core.os.syscall_handler import BusinessLogicSyscallHandler

from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.controllers.transaction_info import (
    TransactionInfoController,
)
from protostar.starknet import Address


class CheatableSyscallHandler(BusinessLogicSyscallHandler):
    def _get_execution_info_ptr(self) -> RelocatableValue:
        # region: Modified starknet code
        # Prepare block info.
        state_syncifier = cast(StateSyncifier, self.storage.state)
        cheatable_state = cast(CheatableCachedState, state_syncifier.async_state)
        python_block_info = cheatable_state.get_block_info(
            self.entry_point.contract_address
        )
        # endregion
        block_info = self.structs.BlockInfo(
            block_number=python_block_info.block_number,
            block_timestamp=python_block_info.block_timestamp,
            sequencer_address=as_non_optional(python_block_info.sequencer_address),
        )
        # region: Modified starknet code
        # Prepare transaction info.
        transaction_info_controller = TransactionInfoController(
            cheatable_state=cheatable_state
        )
        tx_info = transaction_info_controller.get_for_contract(
            Address(self.entry_point.contract_address)
        )

        signature = tx_info.signature
        signature_start = self.allocate_segment(data=signature)

        tx_info = self.structs.TxInfo(
            version=tx_info.version,
            account_contract_address=tx_info.account_contract_address,
            max_fee=self.tx_execution_context.max_fee,
            signature_start=signature_start,
            signature_end=signature_start + len(signature),
            transaction_hash=tx_info.transaction_hash,
            chain_id=tx_info.chain_id,
            nonce=tx_info.nonce,
        )
        # endregion
        # Gather all info.
        execution_info = self.structs.ExecutionInfo(
            block_info=self.allocate_segment(data=block_info),
            tx_info=self.allocate_segment(data=tx_info),
            caller_address=self.entry_point.caller_address,
            contract_address=self.entry_point.contract_address,
            selector=self.entry_point.entry_point_selector,
        )
        return self.allocate_segment(data=execution_info)
