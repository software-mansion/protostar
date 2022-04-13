import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Pattern
from uuid import UUID
from uuid import uuid4 as uuid

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from src.commands.test.cases import BrokenTest, FailedCase, PassedCase
from src.commands.test.cheatable_syscall_handler import CheatableSysCallHandler
from src.commands.test.collector import TestCollector
from src.commands.test.reporter import TestReporter
from src.commands.test.test_environment_exceptions import (
    ExpectedRevertMismatchException,
    ReportedException,
    RevertableException,
    StandardReportedException,
)
from src.commands.test.utils import TestSubject, extract_core_info_from_stark_ex_message
from src.utils.modules import replace_class
from src.utils.starknet_compilation import StarknetCompiler

if TYPE_CHECKING:
    from src.utils.config.project import Project


current_directory = Path(__file__).parent


class TestRunner:
    reporter: Optional[TestReporter] = None
    include_paths: Optional[List[str]] = None
    _collected_count: Optional[int] = None

    def __init__(
        self,
        project: Optional["Project"] = None,
        include_paths: Optional[List[str]] = None,
        is_test_fail_enabled=False,
    ):
        self._is_test_fail_enabled = is_test_fail_enabled

        self.include_paths = []
        if project:
            self.include_paths.extend(project.get_include_paths())

        if include_paths:
            self.include_paths.extend(include_paths)

    @replace_class(
        "starkware.starknet.core.os.syscall_utils.BusinessLogicSysCallHandler",
        CheatableSysCallHandler,
    )
    async def run_tests_in(
        self,
        src: Path,
        match_pattern: Optional[Pattern] = None,
        omit_pattern: Optional[Pattern] = None,
    ):
        self.reporter = TestReporter(src)
        assert self.include_paths is not None, "Uninitialized paths list in test runner"
        test_subjects = TestCollector(
            target=src,
            include_paths=self.include_paths,
        ).collect(
            match_pattern=match_pattern,
            omit_pattern=omit_pattern,
        )
        self.reporter.report_collected(test_subjects)
        for test_subject in test_subjects:

            compiled_test = StarknetCompiler(
                include_paths=self.include_paths,
                disable_hint_validation=True,
            ).compile_contract(test_subject.test_path, add_debug_info=True)

            self.reporter.file_entry(test_subject.test_path.name)
            await self._run_test_functions(
                test_contract=compiled_test,
                test_subject=test_subject,
                functions=test_subject.test_functions,
            )
        self.reporter.report_summary()

    async def _run_test_functions(
        self,
        test_contract: ContractDefinition,
        test_subject: TestSubject,
        functions: List[dict],
    ):
        assert self.reporter, "Uninitialized reporter!"

        for function in functions:
            try:
                env = await TestExecutionEnvironment.empty(
                    test_contract, self._is_test_fail_enabled, self.include_paths
                )
            except StarkException as err:
                self.reporter.report(
                    subject=test_subject,
                    case_result=BrokenTest(
                        file_path=test_subject.test_path, exception=err
                    ),
                )
                return

            try:
                call_result = await env.invoke_test_function(function["name"])
                self.reporter.report(
                    subject=test_subject,
                    case_result=PassedCase(tx_info=call_result),
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
    def __init__(self, is_test_fail_enabled: bool, include_paths: List[str]):
        self.starknet = None
        self.test_contract = None
        self._expected_error: Optional[RevertableException] = None
        self._is_test_fail_enabled = is_test_fail_enabled
        self._include_paths = include_paths
        self._test_finished_listener_map: Dict[UUID, Optional[Callable[[], None]]] = {}

    @classmethod
    async def empty(
        cls,
        test_contract: ContractDefinition,
        is_test_fail_enabled: bool,
        include_paths: Optional[List[str]] = None,
    ):
        env = cls(is_test_fail_enabled, include_paths or [])
        env.starknet = await Starknet.empty()
        env.test_contract = await env.starknet.deploy(contract_def=test_contract)
        return env

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

        func = getattr(self.test_contract, function_name)

        # TODO: Improve stacktrace
        try:
            try:
                call_result = await func().invoke()
                if self._expected_error is not None:
                    raise StandardReportedException(
                        f"Expected an exception matching the following error:\n{self._expected_error}"
                    )

                for listener in self._test_finished_listener_map.values():
                    if listener:
                        listener()
                return call_result
            except StarkException as ex:
                raise RevertableException(
                    error_type=ex.code.name,
                    error_message=extract_core_info_from_stark_ex_message(ex.message),
                    exception=ex,
                ) from ex

        except RevertableException as ex:
            if self._expected_error:
                if self._expected_error != ex:
                    raise ExpectedRevertMismatchException(
                        expected=self._expected_error,
                        received=ex,
                    ) from ex
            else:
                if ex.original_exception:
                    raise ex.original_exception
        finally:
            CairoFunctionRunner.run_from_entrypoint = original_run_from_entrypoint
            self._expected_error = None

    def subscribe_to_test_finish(
        self, listener: Callable[[], None]
    ) -> Callable[[], None]:
        listener_id = uuid()
        self._test_finished_listener_map[listener_id] = listener

        def unsubscribe():
            self._test_finished_listener_map[listener_id] = None

        return unsubscribe

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
        def start_prank(caller_address: int):
            cheatable_syscall_handler.set_caller_address(caller_address)

        @register_cheatcode
        def stop_prank():
            cheatable_syscall_handler.set_caller_address(None)

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
        ) -> Callable[[], None]:
            return self.expect_revert(
                RevertableException(error_type=error_type, error_message=error_message)
            )

        @register_cheatcode
        def expect_emit(
            event_name: str,
            event_data: Optional[List[int]] = None,
            order: Optional[int] = None,
        ) -> Callable[[], None]:
            already_emitted_events_count: Optional[int] = len(
                cheatable_syscall_handler.events
            )

            def stop_expecting_emit():
                unsubscribe_listening_to_test_finish()
                for event in cheatable_syscall_handler.events[
                    already_emitted_events_count:
                ]:
                    assert len(event.keys) > 0

                    is_event_expected = (
                        get_selector_from_name(event_name) == event.keys[0]
                        and (event_data is None or event_data == event.data)
                        and (order is None or event.order == order)
                    )

                    if is_event_expected:
                        return

                raise RevertableException(
                    error_type="EXPECTED_EMIT",
                    error_message=f"event_name: {event_name}, event_data: {event_data}, order: {order}",
                )

            unsubscribe_listening_to_test_finish = self.subscribe_to_test_finish(
                stop_expecting_emit
            )
            return stop_expecting_emit

        @register_cheatcode
        def deploy_contract(
            contract_path: str, constructor_calldata: Optional[List[int]] = None
        ):
            return self.deploy_in_env(contract_path, constructor_calldata)

    def expect_revert(self, expected_error: RevertableException) -> Callable[[], None]:
        if self._expected_error is not None:
            raise StandardReportedException(
                f"Protostar is already expecting an exception matching the following error: {self._expected_error}"
            )

        self._expected_error = expected_error

        def stop_expecting_revert():
            if self._expected_error is not None:
                raise StandardReportedException(
                    "Expected a transaction to be reverted before cancelling expect_revert"
                )

        return stop_expecting_revert


class DeployedContract:
    def __init__(self, starknet_contract: StarknetContract):
        self._starknet_contract = starknet_contract

    @property
    def contract_address(self):
        return self._starknet_contract.contract_address
