from typing import cast

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.python.utils import as_non_optional
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.core.os.syscall_handler import BusinessLogicSyscallHandler

from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)


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
        # Prepare transaction info.
        signature = self.tx_execution_context.signature
        signature_start = self.allocate_segment(data=signature)
        tx_info = self.structs.TxInfo(
            version=self.tx_execution_context.version,
            account_contract_address=self.tx_execution_context.account_contract_address,
            max_fee=self.tx_execution_context.max_fee,
            signature_start=signature_start,
            signature_end=signature_start + len(signature),
            transaction_hash=self.tx_execution_context.transaction_hash,
            chain_id=self.general_config.chain_id.value,
            nonce=self.tx_execution_context.nonce,
        )
        # Gather all info.
        execution_info = self.structs.ExecutionInfo(
            block_info=self.allocate_segment(data=block_info),
            tx_info=self.allocate_segment(data=tx_info),
            caller_address=self.entry_point.caller_address,
            contract_address=self.entry_point.contract_address,
            selector=self.entry_point.entry_point_selector,
        )
        return self.allocate_segment(data=execution_info)
