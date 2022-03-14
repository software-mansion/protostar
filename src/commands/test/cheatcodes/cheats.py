from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List

from starkware.starknet.public.abi import get_selector_from_name

if TYPE_CHECKING:  # prevents circular dependency error
    from src.commands.test.cheatcodes.syscall_handler import CheatableSysCallHandler
    from src.commands.test.runner_test import TestRunner
else:
    TestRunner = Any
    CheatableSysCallHandler = Any


@dataclass
class ModifiableUnits:
    test_runner: TestRunner
    cheatable_syscall_handler: CheatableSysCallHandler


def inject_cheats_into_hint_locals(
    hint_locals: Dict[str, Any], modifiable_units: ModifiableUnits
):
    def register_cheatcode(func):
        hint_locals[func.__name__] = func
        return func

    @register_cheatcode
    def roll(blk_number: int):
        modifiable_units.cheatable_syscall_handler.set_block_number(blk_number)

    @register_cheatcode
    def warp(blk_timestamp: int):
        modifiable_units.cheatable_syscall_handler.set_block_timestamp(blk_timestamp)

    @register_cheatcode
    def start_prank(caller_address: int):
        modifiable_units.cheatable_syscall_handler.set_caller_address(caller_address)

    @register_cheatcode
    def stop_prank():
        modifiable_units.cheatable_syscall_handler.set_caller_address(None)

    @register_cheatcode
    def mock_call(contract_address: int, fn_name: str, ret_data: List[int]):
        selector = get_selector_from_name(fn_name)
        modifiable_units.cheatable_syscall_handler.register_mock_call(
            contract_address, selector=selector, ret_data=ret_data
        )

    @register_cheatcode
    def clear_mock_call(contract_address: int, fn_name: str):
        selector = get_selector_from_name(fn_name)
        modifiable_units.cheatable_syscall_handler.unregister_mock_call(
            contract_address, selector
        )

    @register_cheatcode
    def expect_revert():
        modifiable_units.test_runner.expect_revert()
