import asyncio
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import List, Optional

from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starkware_utils.error_handling import StarkException

from src.commands.test.starkware_patch import CheatableSysCallHandler
from src.commands.test.test_cases import BrokenTestFile, FailedTestCase, PassedTestCase
from src.commands.test.test_environment_exceptions import ReportedException
from src.commands.test.test_execution_environment import TestExecutionEnvironment
from src.commands.test.test_subject_queue import TestSubject, TestSubjectQueue
from src.utils.modules import replace_class
from src.utils.starknet_compilation import StarknetCompiler

current_directory = Path(__file__).parent

logger = getLogger()


class TestRunner:
    include_paths: Optional[List[str]] = None
    _collected_count: Optional[int] = None

    def __init__(
        self,
        queue: TestSubjectQueue,
        include_paths: Optional[List[str]] = None,
    ):
        self.queue = queue
        self.include_paths = []

        if include_paths:
            self.include_paths.extend(include_paths)

    @dataclass
    class WorkerArgs:
        subject: TestSubject
        test_subject_queue: TestSubjectQueue
        include_paths: List[str]

    @classmethod
    def worker(cls, args: "TestRunner.WorkerArgs"):
        asyncio.run(
            cls(
                queue=args.test_subject_queue, include_paths=args.include_paths
            ).run_test_subject(args.subject)
        )

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
        assert self.queue, "Uninitialized reporter!"

        try:
            env_base = await TestExecutionEnvironment.empty(
                test_contract, self.include_paths
            )
        except StarkException as err:
            self.queue.enqueue(
                (
                    test_subject,
                    BrokenTestFile(file_path=test_subject.test_path, exception=err),
                )
            )
            return

        for function in functions:
            env = env_base.fork()
            try:
                call_result = await env.invoke_test_function(function["name"])
                self.queue.enqueue(
                    (
                        test_subject,
                        PassedTestCase(
                            file_path=test_subject.test_path,
                            function_name=function["name"],
                            tx_info=call_result,
                        ),
                    )
                )
            except ReportedException as err:
                self.queue.enqueue(
                    (
                        test_subject,
                        FailedTestCase(
                            file_path=test_subject.test_path,
                            function_name=function["name"],
                            exception=err,
                        ),
                    )
                )
