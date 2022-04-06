import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Pattern

from attr import dataclass
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
    MissingExceptException,
    ReportedException,
    StarkReportedException,
    TestNotFailedException,
)
from src.commands.test.utils import TestSubject
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
            ).compile_contract(test_subject.test_path)

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

            except ReportedException as err:
                self.reporter.report(
                    subject=test_subject,
                    case_result=FailedCase(
                        file_path=test_subject.test_path,
                        function_name=function["name"],
                        exception=err,
                    ),
                )
                return

            self.reporter.report(
                subject=test_subject,
                case_result=PassedCase(tx_info=call_result),
            )


@dataclass
class ExpectedError:
    name: Optional[str]
    message: Optional[str]


class TestExecutionEnvironment:
    def __init__(self, is_test_fail_enabled: bool, include_paths):
        self.starknet = None
        self.test_contract = None
        self._expected_error: Optional[ExpectedError] = None
        self._is_test_fail_enabled = is_test_fail_enabled
        self._include_paths = include_paths

    @classmethod
    async def empty(
        cls,
        test_contract: ContractDefinition,
        is_test_fail_enabled: bool,
        include_paths: Optional[List[str]] = None,
    ):
        env = cls(is_test_fail_enabled, include_paths)
        env.starknet = await Starknet.empty()
        env.test_contract = await env.starknet.deploy(contract_def=test_contract)
        return env

    def deploy_in_env(
        self, contract_path: str, constructor_calldata: Optional[List[int]] = None
    ):
        assert self.starknet
        contract = DeployedContact(
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
        is_failure_expected = (
            function_name.startswith("test_fail_") and self._is_test_fail_enabled
        )

        # TODO: Improve stacktrace
        try:
            try:
                call_result = await func().invoke()
                if self._expected_error is not None:
                    raise MissingExceptException(
                        f"Expected an exception matching the following regex: {self._expected_error.name}"
                    )
                if is_failure_expected:
                    raise TestNotFailedException()
                return call_result

            except StarkException as ex:
                is_ex_unexpected = self._expected_error is None or (
                    self._expected_error.name == ex.code.name
                    and self._expected_error.message == ex.message
                )

                if is_ex_unexpected:
                    raise StarkReportedException(ex) from ex

                if is_failure_expected:
                    raise TestNotFailedException() from ex
        except TestNotFailedException as ex:
            raise ex
        except ReportedException as ex:
            if not is_failure_expected:
                raise ex
        finally:
            CairoFunctionRunner.run_from_entrypoint = original_run_from_entrypoint
            self._expected_error = None

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
                ExpectedError(name=error_type, message=error_message)
            )

        @register_cheatcode
        def deploy_contract(
            contract_path: str, constructor_calldata: Optional[List[int]] = None
        ):
            return self.deploy_in_env(contract_path, constructor_calldata)

    def expect_revert(self, expected_error: ExpectedError) -> Callable[[], None]:
        if self._expected_error is not None:
            raise MissingExceptException(
                f"Protostar is already expecting an exception matching the following regex: {self._expected_error.name}"
            )

        self._expected_error = expected_error

        def stop_expecting_revert():
            if self._expected_error is not None:
                raise MissingExceptException(
                    "Expected a transaction to be reverted before cancelling expect_revert"
                )

        return stop_expecting_revert


class DeployedContact:
    def __init__(self, starknet_contract: StarknetContract):
        self._starknet_contract = starknet_contract

    @property
    def contract_address(self):
        return self._starknet_contract.contract_address
