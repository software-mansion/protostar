import asyncio
import traceback
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import List, Optional

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.protostar_exception import ProtostarException
from protostar.test_runner.environments.setup_execution_environment import (
    SetupExecutionEnvironment,
)
from protostar.utils.compiler.pass_managers import (
    ProtostarPassMangerFactory,
    TestSuitePassMangerFactory,
)
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler

from .test_case_runners.setup_case_runner import run_setup_case
from .test_case_runners.test_case_runner_factory import TestCaseRunnerFactory
from .test_config import TestConfig
from .test_results import (
    BrokenSetupCaseResult,
    BrokenTestSuiteResult,
    SkippedSetupCaseResult,
    TestResult,
    UnexpectedBrokenTestSuiteResult,
)
from .test_shared_tests_state import SharedTestsState
from .test_suite import TestCase, TestSuite
from .testing_seed import Seed

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
        testing_seed: Seed

    @classmethod
    def worker(cls, args: "TestRunner.WorkerArgs"):
        asyncio.run(
            cls(
                shared_tests_state=args.shared_tests_state,
                include_paths=args.include_paths,
                disable_hint_validation_in_user_contracts=args.disable_hint_validation_in_user_contracts,
            ).run_test_suite(
                test_suite=args.test_suite,
                testing_seed=args.testing_seed,
            )
        )

    async def run_test_suite(
        self,
        test_suite: TestSuite,
        testing_seed: Seed,
    ):
        test_config = TestConfig(seed=testing_seed)

        try:
            compiled_test = self.tests_compiler.compile_contract(
                test_suite.test_path,
                add_debug_info=True,
            )

            execution_state = await self._build_execution_state(
                test_contract=compiled_test,
                test_suite=test_suite,
                test_config=test_config,
                contract_path=test_suite.test_path,
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
        contract_path: Path,
    ) -> Optional[TestExecutionState]:
        assert self.shared_tests_state, "Uninitialized reporter!"

        try:
            execution_state = await TestExecutionState.from_test_suite_definition(
                starknet_compiler=self.user_contracts_compiler,
                test_suite_definition=test_contract,
                test_config=test_config,
                contract_path=contract_path,
            )

            if test_suite.setup_fn_name:
                env = SetupExecutionEnvironment(execution_state)
                await env.execute(test_suite.setup_fn_name)

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

        if test_case.setup_fn_name:
            setup_case_result = await run_setup_case(test_case, state)
            if isinstance(setup_case_result, BrokenSetupCaseResult):
                return setup_case_result.into_broken_test_case_result()
            if isinstance(setup_case_result, SkippedSetupCaseResult):
                return setup_case_result.into_skipped_test_case_result()

        state.determine_test_mode(test_case)

        test_case_runner_factory = TestCaseRunnerFactory(state)
        test_case_runner = test_case_runner_factory.make(test_case)
        return await test_case_runner.run()
