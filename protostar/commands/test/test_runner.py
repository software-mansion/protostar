import asyncio
import traceback
from dataclasses import dataclass
from logging import getLogger
from typing import List, Optional

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.test_cases import (
    BrokenTestSuite,
    FailedTestCase,
    PassedTestCase,
    UnexpectedExceptionTestSuiteResult,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_execution_environment import TestExecutionEnvironment
from protostar.commands.test.test_results_queue import TestResultsQueue
from protostar.commands.test.test_suite import TestSuite
from protostar.protostar_exception import ProtostarException
from protostar.utils.starknet_compilation import StarknetCompiler

logger = getLogger()


class TestRunner:
    def __init__(
        self,
        queue: TestResultsQueue,
        include_paths: Optional[List[str]] = None,
    ):
        self.queue = queue
        self.include_paths: List[str] = []

        if include_paths:
            self.include_paths.extend(include_paths)

        self.starknet_compiler = StarknetCompiler(
            include_paths=self.include_paths,
            disable_hint_validation=True,
        )

    @dataclass
    class WorkerArgs:
        test_suite: TestSuite
        test_results_queue: TestResultsQueue
        include_paths: List[str]
        is_account_contract: bool

    @classmethod
    def worker(cls, args: "TestRunner.WorkerArgs"):
        asyncio.run(
            cls(
                queue=args.test_results_queue, include_paths=args.include_paths
            ).run_test_suite(args.test_suite)
        )

    async def run_test_suite(self, test_suite: TestSuite):
        try:
            assert (
                self.include_paths is not None
            ), "Uninitialized paths list in test runner"

            compiled_test = self.starknet_compiler.compile_preprocessed_contract(
                test_suite.preprocessed_contract,
                add_debug_info=True,
                is_account_contract=False,
            )

            await self._run_test_suite(
                test_contract=compiled_test,
                test_suite=test_suite,
            )

        except ReportedException as ex:
            self.queue.put(
                BrokenTestSuite(
                    file_path=test_suite.test_path,
                    test_case_names=test_suite.test_case_names,
                    exception=ex,
                )
            )
        # An unexpected exception in a worker should crash nor freeze the whole application
        except BaseException as ex:  # pylint: disable=broad-except
            self.queue.put(
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
        assert self.queue, "Uninitialized reporter!"

        try:
            env_base = await TestExecutionEnvironment.from_test_suite_definition(
                self.starknet_compiler, test_contract, self.include_paths
            )

            if test_suite.setup_fn_name:
                await env_base.invoke_setup_hook(test_suite.setup_fn_name)

        except StarkException as ex:
            if self.is_constructor_args_exception(ex):
                ex = ProtostarException(
                    (
                        "Protostar doesn't support the unit testing approach for"
                        "files with a constructor expecting arguments."
                        "Restructure your code or use `deploy_contract` cheatcode."
                    )
                )

            self.queue.put(
                BrokenTestSuite(
                    file_path=test_suite.test_path,
                    exception=ex,
                    test_case_names=test_suite.test_case_names,
                )
            )
            return

        for test_case_name in test_suite.test_case_names:
            env = env_base.fork()
            try:
                call_result = await env.invoke_test_case(test_case_name)
                self.queue.put(
                    PassedTestCase(
                        file_path=test_suite.test_path,
                        test_case_name=test_case_name,
                        tx_info=call_result,
                    )
                )
            except ReportedException as ex:
                self.queue.put(
                    FailedTestCase(
                        file_path=test_suite.test_path,
                        test_case_name=test_case_name,
                        exception=ex,
                    )
                )

    @staticmethod
    def is_constructor_args_exception(ex: StarkException) -> bool:
        if not ex.message:
            return False
        return "constructor" in ex.message and "__calldata_actual_size" in ex.message
