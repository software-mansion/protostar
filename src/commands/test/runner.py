import asyncio
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.testing.contract import StarknetContract
from starkware.starkware_utils.error_handling import StarkException


from src.commands.test.cases import BrokenTest, FailedCase, PassedCase
from src.commands.test.cheatable_syscall_handler import CheatableSysCallHandler
from src.commands.test.forkable_starknet import ForkableStarknet
from src.commands.test.reporter import Reporter
from src.commands.test.test_environment_exceptions import (
    ExpectedRevertException,
    ExpectedRevertMismatchException,
    ReportedException,
    RevertableException,
    StarknetRevertableException,
)
from src.commands.test.utils import ExpectedEvent, TestSubject
from src.utils.modules import replace_class
from src.utils.starknet_compilation import StarknetCompiler

current_directory = Path(__file__).parent

logger = getLogger()


class TestRunner:
    include_paths: Optional[List[str]] = None
    _collected_count: Optional[int] = None

    def __init__(
        self,
        reporter: Reporter,
        include_paths: Optional[List[str]] = None,
    ):
        self.reporter = reporter
        self.include_paths = []

        if include_paths:
            self.include_paths.extend(include_paths)

    @replace_class(
        "starkware.starknet.core.os.syscall_utils.BusinessLogicSysCallHandler",
        CheatableSysCallHandler,
    )
    async def run_test_subject(self, test_subject):
        assert self.include_paths is not None, "Uninitialized paths list in test runner"

        compiled_test = StarknetCompiler(
            include_paths=self.include_paths,
            disable_hint_validation=True,
        ).compile_contract(test_subject.test_path, add_debug_info=True)

        await self._run_test_functions(
            test_contract=compiled_test,
            test_subject=test_subject,
            functions=test_subject.test_functions,
        )

    async def _run_test_functions(
        self,
        test_contract: ContractDefinition,
        test_subject: TestSubject,
        functions: List[dict],
    ):
        assert self.reporter, "Uninitialized reporter!"

        try:
            env_base = await TestExecutionEnvironment.empty(
                test_contract, self.include_paths
            )
        except StarkException as err:
            self.reporter.report(
                subject=test_subject,
                case_result=BrokenTest(file_path=test_subject.test_path, exception=err),
            )
            return

        for function in functions:
            env = env_base.fork()
            try:
                call_result = await env.invoke_test_function(function["name"])
                self.reporter.report(
                    subject=test_subject,
                    case_result=PassedCase(
                        file_path=test_subject.test_path,
                        function_name=function["name"],
                        tx_info=call_result,
                    ),
                )
            except ReportedException as err:
                self.reporter.report(
                    subject=test_subject,
                    case_result=FailedCase(
                        file_path=test_subject.test_path,
                        function_name=function["name"],
                        exception=err,
                    ),
                )


class TestExecutionEnvironment:
    def __init__(self, include_paths: List[str]):
        self.starknet = None
        self.test_contract: Optional[StarknetContract] = None
        self._expected_error: Optional[RevertableException] = None
        self._include_paths = include_paths
        self._test_finish_hooks: Set[Callable[[], None]] = set()

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

    async def invoke_test_function(self, function_name: str):
        original_run_from_entrypoint = CairoFunctionRunner.run_from_entrypoint
        CairoFunctionRunner.run_from_entrypoint = (
            self._get_run_from_entrypoint_with_custom_hint_locals(
                CairoFunctionRunner.run_from_entrypoint
            )
        )

        try:
            await self._call_test_function(function_name)
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

    async def _call_test_function(self, function_name: str):
        try:
            func = getattr(self.test_contract, function_name)
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

            return fn_run_from_entrypoint(
                *args,
                **kwargs,
            )

        return modified_run_from_entrypoint

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
        def roll(blk_number: int):
            cheatable_syscall_handler.set_block_number(blk_number)

        @register_cheatcode
        def warp(blk_timestamp: int):
            cheatable_syscall_handler.set_block_timestamp(blk_timestamp)

        @register_cheatcode
        def start_prank(caller_address: int, target: Optional[int] = None):
            cheatable_syscall_handler.set_caller_address(caller_address, target=target)
            def stop_started_prank():
                cheatable_syscall_handler.reset_caller_address(target=target)
            return stop_started_prank

        @register_cheatcode
        def stop_prank(target: Optional[int] = None):
            logger.warning("Using stop_prank() is deprecated, instead use a function returned by start_prank()")
            cheatable_syscall_handler.reset_caller_address(target=target)
        

        @register_cheatcode
        def mock_call(contract_address: int, fn_name: str, ret_data: List[int]):
            selector = get_selector_from_name(fn_name)
            cheatable_syscall_handler.register_mock_call(
                contract_address, selector=selector, ret_data=ret_data
            )

        @register_cheatcode
        def clear_mock_call(contract_address: int, fn_name: str):
            selector = get_selector_from_name(fn_name)
            cheatable_syscall_handler.unregister_mock_call(contract_address, selector)

        @register_cheatcode
        def expect_revert(
            error_type: Optional[str] = None, error_message: Optional[str] = None
        ):
            return self.expect_revert(
                RevertableException(error_type=error_type, error_message=error_message)
            )

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


class DeployedContract:
    def __init__(self, starknet_contract: StarknetContract):
        self._starknet_contract = starknet_contract

    @property
    def contract_address(self):
        return self._starknet_contract.contract_address

