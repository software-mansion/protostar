import asyncio
from dataclasses import dataclass
from logging import getLogger
from typing import List, Optional

from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.test_cases import (
    BrokenTestSuite,
    FailedTestCase,
    PassedTestCase,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_execution_environment import TestExecutionEnvironment
from protostar.commands.test.test_results_queue import TestResultsQueue
from protostar.commands.test.test_suite import TestSuite
from protostar.utils.starknet_compilation import StarknetCompiler

logger = getLogger()


class TestRunner:
    include_paths: Optional[List[str]] = None
    _collected_count: Optional[int] = None

    def __init__(
        self,
        queue: TestResultsQueue,
        include_paths: Optional[List[str]] = None,
    ):
        self.queue = queue
        self.include_paths = []

        if include_paths:
            self.include_paths.extend(include_paths)

    @dataclass
    class WorkerArgs:
        test_suite: TestSuite
        test_results_queue: TestResultsQueue
        include_paths: List[str]

    @classmethod
    def worker(cls, args: "TestRunner.WorkerArgs"):
        asyncio.run(
            cls(
                queue=args.test_results_queue, include_paths=args.include_paths
            ).run_test_suite(args.test_suite)
        )

    async def run_test_suite(self, test_suite: TestSuite):
        assert self.include_paths is not None, "Uninitialized paths list in test runner"

        compiled_test = StarknetCompiler(
            include_paths=self.include_paths,
            disable_hint_validation=True,
        ).compile_preprocessed_contract(
            test_suite.preprocessed_contract, add_debug_info=True
        )

        await self._run_test_suite(
            test_contract=compiled_test,
            test_suite=test_suite,
        )

    async def _run_test_suite(
        self,
        test_contract: ContractDefinition,
        test_suite: TestSuite,
    ):
        assert self.queue, "Uninitialized reporter!"

        try:
            env_base = await TestExecutionEnvironment.empty(
                test_contract, self.include_paths
            )

            if test_suite.setup_state_fn_name:
                raise NotImplementedError()

        except StarkException as err:
            self.queue.put(
                BrokenTestSuite(
                    file_path=test_suite.test_path,
                    exception=err,
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
            except ReportedException as err:
                self.queue.put(
                    FailedTestCase(
                        file_path=test_suite.test_path,
                        test_case_name=test_case_name,
                        exception=err,
                    )
                )
