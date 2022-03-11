from typing import TYPE_CHECKING, Any, Dict, List

from starkware.starknet.public.abi import get_selector_from_name
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from src.commands.test.cheatcodes.syscall_handler import CheatableSysCallHandler
    from src.commands.test.runner_test import TestRunner
else:
    TestRunner = Any
    CheatableSysCallHandler = Any


class ModifiedUnits(TypedDict):
    test_runner: TestRunner
    cheatable_syscall_handler: CheatableSysCallHandler


def inject_cheats_into_hint_locals(
    hint_locals: Dict[str, Any], modified_units: ModifiedUnits
):
    def register_cheatcode(func):
        hint_locals[func.__name__] = func
        return func

    # func roll(blk_number : felt):
    #     %{ syscall_handler.set_block_number(ids.blk_number) %}
    #     return ()
    # end

    # func warp(blk_timestamp : felt):
    #     %{ syscall_handler.set_block_timestamp(ids.blk_timestamp) %}
    #     return ()
    # end

    # func start_prank(caller_address : felt):
    #     %{ syscall_handler.set_caller_address(ids.caller_address) %}
    #     return ()
    # end

    # func stop_prank():
    #     %{ syscall_handler.set_caller_address(None) %}
    #     return ()
    # end

    @register_cheatcode
    def mock_call(contract_address: int, fn_name: str, ret_data: List[int]):
        selector = get_selector_from_name(fn_name)
        modified_units["cheatable_syscall_handler"].register_mock_call(
            contract_address, selector=selector, ret_data=ret_data
        )
