import asyncio
import traceback
from dataclasses import dataclass
from logging import getLogger
from typing import List, Optional

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.environments.setup_execution_environment import (
    SetupExecutionEnvironment,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_case_runners.test_case_runner_factory import (
    TestCaseRunnerFactory,
)
from protostar.commands.test.test_config import TestConfig, TestMode
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_results import (
    BrokenTestSuiteResult,
    TestResult,
    UnexpectedBrokenTestSuiteResult,
)
from protostar.commands.test.test_shared_tests_state import SharedTestsState
from protostar.commands.test.test_suite import TestSuite, TestCase
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
        include_paths: Optional[List[str]] = None,
        disable_hint_validation_in_user_contracts=False,
    ):
        self.shared_tests_state = shared_tests_state
        include_paths = include_paths or []

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
        test_config = TestConfig()

        try:
            compiled_test = self.tests_compiler.compile_contract(
                test_suite.test_path,
                add_debug_info=True,
            )

            execution_state = await self._build_execution_state(
                test_contract=compiled_test,
                test_suite=test_suite,
                test_config=test_config,
            )
            if not execution_state:
                return
            await self._invoke_test_cases(
                test_suite=test_suite,
                execution_state=execution_state,
            )
        except ProtostarException as ex:
            self.shared_tests_state.put_result(
                BrokenTestSuiteResult(
                    file_path=test_suite.test_path,
                    test_case_names=test_suite.collect_test_case_names(),
                    exception=ex,
                )
            )

        except ReportedException as ex:
            self.shared_tests_state.put_result(
                BrokenTestSuiteResult(
                    file_path=test_suite.test_path,
                    test_case_names=test_suite.collect_test_case_names(),
                    exception=ex,
                )
            )

        # An unexpected exception in a worker should neither crash nor freeze the whole application
        except BaseException as ex:  # pylint: disable=broad-except
            self.shared_tests_state.put_result(
                UnexpectedBrokenTestSuiteResult(
                    file_path=test_suite.test_path,
                    test_case_names=test_suite.collect_test_case_names(),
                    exception=ex,
                    traceback=traceback.format_exc(),
                )
            )

    async def _build_execution_state(
        self,
        test_contract: ContractClass,
        test_suite: TestSuite,
        test_config: TestConfig,
    ) -> Optional[TestExecutionState]:
        assert self.shared_tests_state, "Uninitialized reporter!"

        try:
            execution_state = await TestExecutionState.from_test_suite_definition(
                starknet_compiler=self.user_contracts_compiler,
                test_suite_definition=test_contract,
                test_config=test_config,
            )

            if test_suite.setup_fn_name:
                env = SetupExecutionEnvironment(execution_state)
                await env.invoke(test_suite.setup_fn_name)

            return execution_state
        except StarkException as ex:
            self.shared_tests_state.put_result(
                BrokenTestSuiteResult(
                    file_path=test_suite.test_path,
                    test_case_names=test_suite.collect_test_case_names(),
                    exception=ex,
                )
            )

            return None

    async def _invoke_test_cases(
        self,
        test_suite: TestSuite,
        execution_state: TestExecutionState,
    ) -> None:
        for test_case in test_suite.test_cases:
            test_result = await self._invoke_test_case(test_case, execution_state)
            self.shared_tests_state.put_result(test_result)

    @staticmethod
    async def _invoke_test_case(
        test_case: TestCase, initial_state: TestExecutionState
    ) -> TestResult:
        state: TestExecutionState = initial_state.fork()

        # TODO(mkaput): Remove this in favor of setting mode explicitly by cheatcodes in setup hooks.
        state.config.mode = TestMode.infer_from_contract_function(
            test_case.test_fn_name, state.contract
        )

        test_case_runner_factory = TestCaseRunnerFactory(state)
        test_case_runner = test_case_runner_factory.make(test_case)
        return await test_case_runner.run()
