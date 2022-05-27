import asyncio
from copy import copy
from logging import getLogger
from typing import Any, Callable, Dict, List, Optional, Set

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.testing.contract import StarknetContract
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.cheatcodes import (
    Cheatcode,
    ExpectRevertCheatcode,
    RollCheatcode,
)
from protostar.commands.test.expected_event import ExpectedEvent
from protostar.commands.test.starkware.cheatable_syscall_handler import (
    CheatableSysCallHandler,
    CheatableSysCallHandlerException,
)
from protostar.commands.test.starkware.forkable_starknet import ForkableStarknet
from protostar.commands.test.test_environment_exceptions import (
    CheatcodeException,
    ExpectedRevertException,
    ExpectedRevertMismatchException,
    ReportedException,
    RevertableException,
    StarknetRevertableException,
)
from protostar.utils.modules import replace_class

logger = getLogger()


class DeployedContract:
    def __init__(self, starknet_contract: StarknetContract):
        self._starknet_contract = starknet_contract

    @property
    def contract_address(self):
        return self._starknet_contract.contract_address


class TestExecutionEnvironment:
    def __init__(self, include_paths: List[str]):
        self.starknet = None
        self.test_contract: Optional[StarknetContract] = None
        self.tmp_state: Dict[str, str] = {}
        self._expected_error: Optional[RevertableException] = None
        self._include_paths = include_paths
        self._test_finish_hooks: Set[Callable[[], None]] = set()
        self._hijacked_hint_locals: Optional[Dict[str, Any]] = {}

    @classmethod
    async def empty(
        cls,
        test_contract: ContractDefinition,
        include_paths: Optional[List[str]] = None,
    ):
        env = cls(include_paths or [])
        env.starknet = await ForkableStarknet.empty()
        env.test_contract = await env.starknet.deploy(contract_def=test_contract)
        return env

    def fork(self):
        assert self.starknet
        assert self.test_contract

        new_env = TestExecutionEnvironment(
            include_paths=self._include_paths,
        )
        new_env.starknet = self.starknet.fork()
        new_env.test_contract = new_env.starknet.copy_and_adapt_contract(
            self.test_contract
        )
        new_env.tmp_state = copy(
            self.tmp_state
        )  # NOTE: `deepcopy`` could freeze Protostar
        return new_env

    def deploy_in_env(
        self, contract_path: str, constructor_calldata: Optional[List[int]] = None
    ):
        assert self.starknet
        contract = DeployedContract(
            asyncio.run(
                self.starknet.deploy(
                    source=contract_path,
                    constructor_calldata=constructor_calldata,
                    cairo_path=self._include_paths,
                )
            )
        )
        return contract

    async def invoke_setup_state(self, fn_name: str) -> None:
        await self.invoke_test_case(fn_name)
        assert self._hijacked_hint_locals is not None

        self.tmp_state = (
            self._hijacked_hint_locals["tmp_state"]
            if "tmp_state" in self._hijacked_hint_locals
            else {}
        )

    @replace_class(
        "starkware.starknet.core.os.syscall_utils.BusinessLogicSysCallHandler",
        CheatableSysCallHandler,
    )
    async def invoke_test_case(self, test_case_name: str):
        original_run_from_entrypoint = CairoFunctionRunner.run_from_entrypoint
        CairoFunctionRunner.run_from_entrypoint = (
            self._get_run_from_entrypoint_with_custom_hint_locals(
                CairoFunctionRunner.run_from_entrypoint
            )
        )

        try:
            await self._call_test_case_fn(test_case_name)
            for hook in self._test_finish_hooks:
                hook()
            if self._expected_error is not None:
                raise ExpectedRevertException(self._expected_error)
        except RevertableException as ex:
            if self._expected_error:
                if not self._expected_error.match(ex):
                    raise ExpectedRevertMismatchException(
                        expected=self._expected_error,
                        received=ex,
                    ) from ex
            else:
                raise ex
        finally:
            CairoFunctionRunner.run_from_entrypoint = original_run_from_entrypoint
            self._expected_error = None
            self._test_finish_hooks.clear()

    async def _call_test_case_fn(self, test_case_name: str):
        try:
            func = getattr(self.test_contract, test_case_name)
            return await func().invoke()
        except StarkException as ex:
            raise StarknetRevertableException(
                error_message=StarknetRevertableException.extract_error_messages_from_stark_ex_message(
                    ex.message
                ),
                error_type=ex.code.name,
                code=ex.code.value,
                details=ex.message,
            ) from ex

    def add_test_finish_hook(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._test_finish_hooks.add(listener)

        def remove_hook():
            self._test_finish_hooks.remove(listener)

        return remove_hook

    def _get_run_from_entrypoint_with_custom_hint_locals(
        self, fn_run_from_entrypoint: Any
    ):
        def modified_run_from_entrypoint(
            *args,
            **kwargs,
        ):
            if "hint_locals" in kwargs and kwargs["hint_locals"] is not None:
                self._hijacked_hint_locals = kwargs["hint_locals"]
                self._inject_cheats_into_hint_locals(
                    kwargs["hint_locals"], kwargs["hint_locals"]["syscall_handler"]
                )
                self._inject_state_into_hint_locals(kwargs["hint_locals"])

            return fn_run_from_entrypoint(
                *args,
                **kwargs,
            )

        return modified_run_from_entrypoint

    def _inject_state_into_hint_locals(self, hint_locals: Dict[str, Any]):
        hint_locals["tmp_state"] = self.tmp_state

    def _inject_cheats_into_hint_locals(
        self,
        hint_locals: Dict[str, Any],
        cheatable_syscall_handler: CheatableSysCallHandler,
    ):
        assert cheatable_syscall_handler is not None

        def register_cheatcode(func):
            hint_locals[func.__name__] = func
            return func

        @register_cheatcode
        def warp(blk_timestamp: int):
            cheatable_syscall_handler.set_block_timestamp(blk_timestamp)

        @register_cheatcode
        def start_prank(
            caller_address: int, target_contract_address: Optional[int] = None
        ):
            try:
                cheatable_syscall_handler.set_caller_address(
                    caller_address, target_contract_address=target_contract_address
                )
            except CheatableSysCallHandlerException as err:
                raise CheatcodeException("start_prank", err.message) from err

            def stop_started_prank():
                try:
                    cheatable_syscall_handler.reset_caller_address(
                        target_contract_address=target_contract_address
                    )
                except CheatableSysCallHandlerException as err:
                    raise CheatcodeException("start_prank", err.message) from err

            return stop_started_prank

        @register_cheatcode
        def stop_prank(target_contract_address: Optional[int] = None):
            logger.warning(
                "Using stop_prank() is deprecated, instead use a function returned by start_prank()"
            )
            try:
                cheatable_syscall_handler.reset_caller_address(
                    target_contract_address=target_contract_address
                )
            except CheatableSysCallHandlerException as err:
                raise CheatcodeException("stop_prank", err.message) from err

        @register_cheatcode
        def mock_call(contract_address: int, fn_name: str, ret_data: List[int]):
            selector = get_selector_from_name(fn_name)
            cheatable_syscall_handler.register_mock_call(
                contract_address, selector=selector, ret_data=ret_data
            )

        @register_cheatcode
        def clear_mock_call(contract_address: int, fn_name: str):
            selector = get_selector_from_name(fn_name)
            try:
                cheatable_syscall_handler.unregister_mock_call(
                    contract_address, selector
                )
            except CheatableSysCallHandlerException as err:
                raise CheatcodeException("stop_prank", err.message) from err

        @register_cheatcode
        def expect_events(
            *raw_expected_events: ExpectedEvent.CheatcodeInputType,
        ) -> None:
            assert self.starknet is not None

            def compare_expected_and_emitted_events():
                assert self.starknet is not None

                expected_events = list(map(ExpectedEvent, raw_expected_events))
                not_found_expected_event = ExpectedEvent.find_first_expected_event_not_included_in_state_events(
                    expected_events,
                    self.starknet.state.events,
                )
                if not_found_expected_event:
                    raise RevertableException(
                        error_type="EXPECTED_EVENT",
                        error_message=f"Expected the following event: {str(not_found_expected_event)}",
                    )

            self.add_test_finish_hook(compare_expected_and_emitted_events)

        @register_cheatcode
        def deploy_contract(
            contract_path: str, constructor_calldata: Optional[List[int]] = None
        ):
            return self.deploy_in_env(contract_path, constructor_calldata)

        cheatcodes: List[Cheatcode] = [
            ExpectRevertCheatcode(self),
            RollCheatcode(cheatable_syscall_handler),
        ]

        for cheatcode in cheatcodes:
            hint_locals[cheatcode.name] = cheatcode.build()

    def expect_revert(self, expected_error: RevertableException) -> Callable[[], None]:
        if self._expected_error is not None:
            raise ReportedException(
                f"Protostar is already expecting an exception matching the following error: {self._expected_error}"
            )

        self._expected_error = expected_error

        def stop_expecting_revert():
            logger.warning(
                "The callback returned by the `expect_revert` is deprecated."
            )
            if self._expected_error is not None:
                raise ReportedException(
                    "Expected a transaction to be reverted before cancelling expect_revert"
                )

        return stop_expecting_revert
