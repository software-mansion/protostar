import asyncio
import time
import traceback
from dataclasses import dataclass
from logging import getLogger
from typing import List, Optional

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.environments.factory import invoke_setup, invoke_test_case
from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzConfig,
    FuzzTestExecutionResult,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_cases import (
    BrokenTestSuite,
    FailedTestCase,
    PassedTestCase,
    UnexpectedExceptionTestSuiteResult,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_shared_tests_state import SharedTestsState
from protostar.commands.test.test_suite import TestSuite
from protostar.protostar_exception import ProtostarException
from protostar.utils.compiler.pass_managers import (
    ProtostarPassMangerFactory,
    TestSuitePassMangerFactory,
)
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler

logger = getLogger()


class TestRunner:
    def __init__(
        self,
        shared_tests_state: SharedTestsState,
        fuzz_config: FuzzConfig,
        include_paths: Optional[List[str]] = None,
        disable_hint_validation_in_user_contracts=False,
    ):
        self.shared_tests_state = shared_tests_state
        include_paths = include_paths or []
        self._fuzz_config = fuzz_config

        self.tests_compiler = StarknetCompiler(
            config=CompilerConfig(
                include_paths=include_paths, disable_hint_validation=True
            ),
            pass_manager_factory=TestSuitePassMangerFactory,
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
        fuzz_config: FuzzConfig

    @classmethod
    def worker(cls, args: "TestRunner.WorkerArgs"):
        asyncio.run(
            cls(
                shared_tests_state=args.shared_tests_state,
                fuzz_config=args.fuzz_config,
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

        try:
            execution_state = await TestExecutionState.from_test_suite_definition(
                self.user_contracts_compiler, test_contract
            )

            if test_suite.setup_fn_name:
                await invoke_setup(test_suite.setup_fn_name, execution_state)

        except StarkException as ex:
            self.shared_tests_state.put_result(
                BrokenTestSuite(
                    file_path=test_suite.test_path,
                    exception=ex,
                    test_case_names=test_suite.test_case_names,
                )
            )
            return

        for test_case_name in test_suite.test_case_names:
            new_execution_state = execution_state.fork()
            start_time = time.perf_counter()
            try:
                execution_result = await invoke_test_case(
                    test_case_name, new_execution_state, fuzz_config=self._fuzz_config
                )
                fuzz_runs_count = (
                    execution_result.fuzz_runs_count
                    if isinstance(execution_result, FuzzTestExecutionResult)
                    else None
                )

                self.shared_tests_state.put_result(
                    PassedTestCase(
                        file_path=test_suite.test_path,
                        test_case_name=test_case_name,
                        execution_resources=execution_result.execution_resources,
                        execution_time=time.perf_counter() - start_time,
                        captured_stdout=new_execution_state.output_recorder.get_captures(),
                        fuzz_runs_count=fuzz_runs_count
                        if isinstance(execution_result, FuzzTestExecutionResult)
                        else None,
                    )
                )
            except ReportedException as ex:
                self.shared_tests_state.put_result(
                    FailedTestCase(
                        file_path=test_suite.test_path,
                        test_case_name=test_case_name,
                        exception=ex,
                        execution_time=time.perf_counter() - start_time,
                        captured_stdout=new_execution_state.output_recorder.get_captures(),
                    )
                )
