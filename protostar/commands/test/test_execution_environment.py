import asyncio
from collections.abc import Mapping
from copy import deepcopy
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.testing.contract import StarknetContract
from starkware.starkware_utils.error_handling import StarkException
from starkware.starknet.testing.contract import DeclaredClass

from protostar.commands.test.cheatcodes_legacy import (
    Cheatcode,
    ExpectRevertCheatcode,
    RollCheatcode,
)

from protostar.commands.test.expected_event import ExpectedEvent
from protostar.commands.test.starkware import (
    CheatableStarknetGeneralConfig,
)

from protostar.commands.test.starkware.cheatable_syscall_handler import (
    CheatableSysCallHandler,
    CheatableSysCallHandlerException,
)
from protostar.commands.test.starkware.forkable_starknet import ForkableStarknet
from protostar.commands.test.test_context import TestContext


from protostar.commands.test.test_environment_exceptions import (
    CheatcodeException,
    ExpectedEventMissingException,
    ExpectedRevertException,
    ExpectedRevertMismatchException,
    RevertableException,
    SimpleReportedException,
    StarknetRevertableException,
)
from protostar.utils.data_transformer_facade import DataTransformerFacade
from protostar.utils.starknet_compilation import StarknetCompiler

logger = getLogger()


class DeployedContract:
    def __init__(self, starknet_contract: StarknetContract):
        self._starknet_contract = starknet_contract

    @property
    def contract_address(self):
        return self._starknet_contract.contract_address


class ProtostarDeclaredClass:
    def __init__(self, declared_class: DeclaredClass):
        self._declared_class = declared_class

    @property
    def class_hash(self):
        return self._declared_class.class_hash


class TestExecutionEnvironment:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        include_paths: List[str],
        forkable_starknet: ForkableStarknet,
        test_contract: StarknetContract,
        test_context: TestContext,
        starknet_compiler: StarknetCompiler,
    ):
        self.starknet = forkable_starknet
        self.test_contract: StarknetContract = test_contract
        self.test_context = test_context
        self._expected_error: Optional[RevertableException] = None
        self._include_paths = include_paths
        self._test_finish_hooks: Set[Callable[[], None]] = set()
        self._starknet_compiler = starknet_compiler

    @classmethod
    async def from_test_suite_definition(
        cls,
        starknet_compiler: StarknetCompiler,
        test_suite_definition: ContractClass,
        include_paths: Optional[List[str]] = None,
    ):
        general_config = CheatableStarknetGeneralConfig(
            cheatcodes_cairo_path=include_paths
        )
        starknet = await ForkableStarknet.empty(general_config=general_config)

        starknet_contract = await starknet.deploy(contract_class=test_suite_definition)

        return cls(
            include_paths or [],
            forkable_starknet=starknet,
            test_contract=starknet_contract,
            test_context=TestContext(),
            starknet_compiler=starknet_compiler,
        )

    def fork(self):
        starknet_fork = self.starknet.fork()
        new_env = TestExecutionEnvironment(
            include_paths=self._include_paths,
            forkable_starknet=starknet_fork,
            test_contract=starknet_fork.copy_and_adapt_contract(self.test_contract),
            test_context=deepcopy(self.test_context),
            starknet_compiler=self._starknet_compiler,
        )
        return new_env

    def deploy_in_env(
        self, contract_path: str, constructor_calldata: Optional[List[int]] = None
    ):

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

    def declare_in_env(self, contract_path: str):
        contract = ProtostarDeclaredClass(
            asyncio.run(
                self.starknet.declare(
                    source=contract_path,
                    cairo_path=self._include_paths,
                )
            )
        )
        return contract

    async def invoke_setup_hook(self, fn_name: str) -> None:
        await self.invoke_test_case(fn_name)

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
                self._inject_cheats_into_hint_locals(
                    kwargs["hint_locals"], kwargs["hint_locals"]["syscall_handler"]
                )
                self._inject_test_context_into_hint_locals(kwargs["hint_locals"])

            return fn_run_from_entrypoint(
                *args,
                **kwargs,
            )

        return modified_run_from_entrypoint

    def _inject_test_context_into_hint_locals(self, hint_locals: Dict[str, Any]):
        hint_locals["context"] = self.test_context

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
                "Using stop_prank() is deprecated, instead call a function returned by start_prank()"
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
            try:
                cheatable_syscall_handler.register_mock_call(
                    contract_address, selector=selector, ret_data=ret_data
                )
            except CheatableSysCallHandlerException as err:
                raise CheatcodeException("mock_call", err.message) from err

            def clear_mock_call():
                try:
                    cheatable_syscall_handler.unregister_mock_call(
                        contract_address, selector
                    )
                except CheatableSysCallHandlerException as err:
                    raise CheatcodeException("clear_mock_call", err.message) from err

            return clear_mock_call

        @register_cheatcode
        def clear_mock_call(contract_address: int, fn_name: str):
            logger.warning(
                "Using clear_mock_call() is deprecated, instead call a function returned by mock_call()"
            )
            selector = get_selector_from_name(fn_name)
            try:
                cheatable_syscall_handler.unregister_mock_call(
                    contract_address, selector
                )
            except CheatableSysCallHandlerException as err:
                raise CheatcodeException("clear_mock_call", err.message) from err

        @register_cheatcode
        def expect_events(
            *raw_expected_events: ExpectedEvent.CheatcodeInputType,
        ) -> None:
            def compare_expected_and_emitted_events():

                expected_events = list(map(ExpectedEvent, raw_expected_events))

                (
                    matches,
                    missing,
                ) = ExpectedEvent.match_state_events_to_expected_to_events(
                    expected_events,
                    self.starknet.state.events,
                )

                if len(missing) > 0:
                    raise ExpectedEventMissingException(
                        matches=matches,
                        missing=missing,
                        # pylint: disable=line-too-long
                        event_selector_to_name_map=self.starknet.state.cheatable_carried_state.event_selector_to_name_map,
                    )

            self.add_test_finish_hook(compare_expected_and_emitted_events)

        @register_cheatcode
        def deploy_contract(
            contract_path: str,
            constructor_calldata: Optional[Union[List[int], Dict]] = None,
        ):
            if isinstance(constructor_calldata, Mapping):
                fn_name = "constructor"
                constructor_calldata = DataTransformerFacade.from_contract_path(
                    Path(contract_path), self._starknet_compiler
                ).from_python(fn_name, **constructor_calldata)

            return self.deploy_in_env(contract_path, constructor_calldata)

        @register_cheatcode
        def declare_contract(contract_path: str):
            return self.declare_in_env(contract_path)

        cheatcodes: List[Cheatcode] = [
            ExpectRevertCheatcode(self),
            RollCheatcode(cheatable_syscall_handler),
        ]

        for cheatcode in cheatcodes:
            hint_locals[cheatcode.name] = cheatcode.build()

    def expect_revert(self, expected_error: RevertableException) -> Callable[[], None]:
        if self._expected_error is not None:
            raise SimpleReportedException(
                f"Protostar is already expecting an exception matching the following error: {self._expected_error}"
            )

        self._expected_error = expected_error

        def stop_expecting_revert():
            logger.warning(
                "The callback returned by the `expect_revert` is deprecated."
            )
            if self._expected_error is not None:
                raise SimpleReportedException(
                    "Expected a transaction to be reverted before cancelling expect_revert"
                )

        return stop_expecting_revert
