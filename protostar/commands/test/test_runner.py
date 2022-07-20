import asyncio
import traceback
from dataclasses import dataclass
from logging import getLogger
from typing import List, Optional

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.environments.factory import invoke_setup, invoke_test_case
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_cases import (
    BrokenTestSuite,
    FailedTestCase,
    PassedTestCase,
    UnexpectedExceptionTestSuiteResult,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_output_recorder import OutputName
from protostar.commands.test.test_shared_tests_state import SharedTestsState
from protostar.commands.test.test_suite import TestSuite
from protostar.protostar_exception import ProtostarException
from protostar.utils.compiler.pass_managers import ProtostarPassMangerFactory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler

logger = getLogger()


class TestRunner:
    def __init__(
        self,
        shared_tests_state: SharedTestsState,
        include_paths: Optional[List[str]] = None,
        disable_hint_validation_in_user_contracts=False,
    ):
        self.shared_tests_state = shared_tests_state
        include_paths = include_paths or []

        self.tests_compiler = StarknetCompiler(
            config=CompilerConfig(
                include_paths=include_paths, disable_hint_validation=True
            ),
            pass_manager_factory=ProtostarPassMangerFactory,
        )

        self.user_contracts_compiler = StarknetCompiler(
            config=CompilerConfig(
                include_paths=include_paths,
                disable_hint_validation=disable_hint_validation_in_user_contracts,
            ),
            pass_manager_factory=ProtostarPassMangerFactory,
        )

    @dataclass
    class WorkerArgs:
        test_suite: TestSuite
        shared_tests_state: SharedTestsState
        include_paths: List[str]
        disable_hint_validation_in_user_contracts: bool

    @classmethod
    def worker(cls, args: "TestRunner.WorkerArgs"):
        asyncio.run(
            cls(
                shared_tests_state=args.shared_tests_state,
                include_paths=args.include_paths,
                disable_hint_validation_in_user_contracts=args.disable_hint_validation_in_user_contracts,
            ).run_test_suite(
                args.test_suite,
            )
        )

    async def run_test_suite(
        self,
        test_suite: TestSuite,
    ):
        try:
            compiled_test = self.tests_compiler.compile_contract(
                test_suite.test_path,
                add_debug_info=True,
            )

            await self._run_test_suite(
                test_contract=compiled_test,
                test_suite=test_suite,
            )
        except ProtostarException as ex:
            self.shared_tests_state.put_result(
                BrokenTestSuite(
                    file_path=test_suite.test_path,
                    test_case_names=test_suite.test_case_names,
                    exception=ex,
                )
            )

        except ReportedException as ex:
            self.shared_tests_state.put_result(
                BrokenTestSuite(
                    file_path=test_suite.test_path,
                    test_case_names=test_suite.test_case_names,
                    exception=ex,
                )
            )

        # An unexpected exception in a worker should crash nor freeze the whole application
        except BaseException as ex:  # pylint: disable=broad-except
            self.shared_tests_state.put_result(
                UnexpectedExceptionTestSuiteResult(
                    file_path=test_suite.test_path,
                    test_case_names=test_suite.test_case_names,
                    exception=ex,
                    traceback=traceback.format_exc(),
                )
            )

    async def _run_test_suite(
        self,
        test_contract: ContractClass,
        test_suite: TestSuite,
    ):
        assert self.shared_tests_state, "Uninitialized reporter!"

        setup_stdout: OutputName = "setup"

        try:
            execution_state = await TestExecutionState.from_test_suite_definition(
                self.user_contracts_compiler,
                test_contract,
            )

            if test_suite.setup_fn_name:
                await invoke_setup(
                    test_suite.setup_fn_name, execution_state, setup_stdout
                )

        except StarkException as ex:
            if self.is_constructor_args_exception(ex):
                ex = ProtostarException(
                    (
                        "Protostar doesn't support the unit testing approach for"
                        "files with a constructor expecting arguments."
                        "Restructure your code or use `deploy_contract` cheatcode."
                    )
                )

            self.shared_tests_state.put_result(
                BrokenTestSuite(
                    file_path=test_suite.test_path,
                    exception=ex,
                    test_case_names=test_suite.test_case_names,
                )
            )
            return

        setup_stdout_value = ""
        if test_suite.setup_fn_name:
            setup_stdout_value = execution_state.get_output(setup_stdout)

        for test_case_name in test_suite.test_case_names:
            new_execution_state = execution_state.fork()
            test_stdout: OutputName = "test"
            try:
                execution_resources = await invoke_test_case(
                    test_case_name,
                    new_execution_state,
                    test_stdout,
                )
                self.shared_tests_state.put_result(
                    PassedTestCase(
                        file_path=test_suite.test_path,
                        test_case_name=test_case_name,
                        execution_resources=execution_resources,
                        captured_stdout=[
                            (
                                setup_stdout,
                                new_execution_state.get_output(setup_stdout),
                            ),
                            (test_stdout, setup_stdout_value),
                        ],
                    )
                )
            except ReportedException as ex:
                self.shared_tests_state.put_result(
                    FailedTestCase(
                        file_path=test_suite.test_path,
                        test_case_name=test_case_name,
                        exception=ex,
                        captured_stdout=[
                            (
                                setup_stdout,
                                new_execution_state.get_output(setup_stdout),
                            ),
                            (test_stdout, setup_stdout_value),
                        ],
                    )
                )

    @staticmethod
    def is_constructor_args_exception(ex: StarkException) -> bool:
        if not ex.message:
            return False
        return "constructor" in ex.message and "__calldata_actual_size" in ex.message
