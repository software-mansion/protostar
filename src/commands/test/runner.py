from pathlib import Path
from typing import List, Optional, Pattern

from starkware.starknet.business_logic.internal_transaction import InternalTransaction
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from src.commands.test.cases import BrokenTest, FailedCase, PassedCase
from src.commands.test.cheatcodes.internal_transaction import (
    CheatableInternalDeploy,
    CheatableInternalInvokeFunction,
)
from src.commands.test.cheatcodes.starknet import CheatableStarknet
from src.commands.test.cheatcodes.state import CheatableStarknetState
from src.commands.test.cheatcodes.syscall_handler import CheatableSysCallHandler
from src.commands.test.collector import TestCollector
from src.commands.test.reporter import TestReporter
from src.commands.test.utils import TestSubject
from src.utils.config.project import Project
from src.utils.modules import replace_class
from src.utils.starknet_compilation import StarknetCompiler

current_directory = Path(__file__).parent


class TestRunner:
    reporter: Optional[TestReporter] = None
    include_paths: Optional[List[str]] = None
    _collected_count: Optional[int] = None

    def __init__(
        self,
        project: Optional[Project] = None,
        include_paths: Optional[List[str]] = None,
    ):
        self.include_paths = include_paths or []
        self.include_paths.append(
            str(Path(current_directory, "cheatcodes", "cheat_sources"))
        )
        if project:
            config = project.load_config()
            self.include_paths.append(str(project.project_root))
            self.include_paths.append(str(Path(project.project_root, config.libs_path)))

    @replace_class(
        "starkware.starknet.testing.state.StarknetState",
        CheatableStarknetState,
    )
    @replace_class(
        "starkware.starknet.business_logic.internal_transaction.InternalDeploy",
        CheatableInternalDeploy,
    )
    @replace_class(
        "starkware.starknet.business_logic.internal_transaction.InternalInvokeFunction",
        CheatableInternalInvokeFunction,
    )
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
        InternalTransaction.external_to_internal_cls[
            CheatableInternalInvokeFunction.related_external_cls
        ] = CheatableInternalInvokeFunction

        self.reporter = TestReporter(src)
        assert self.include_paths is not None, "Uninitialized paths list in test runner"
        test_subjects = TestCollector(
            sources_directory=src,
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
        try:
            starknet = await Starknet.empty()
            contract = await starknet.deploy(contract_def=test_contract)
        except StarkException as err:
            self.reporter.report(
                subject=test_subject,
                case_result=BrokenTest(file_path=test_subject.test_path, exception=err),
            )
            return

        for function in functions:
            try:
                func = getattr(contract, function["name"])

                # TODO: Improve stacktrace
                call_result = await func(contract.contract_address).call()
                self.reporter.report(
                    subject=test_subject, case_result=PassedCase(tx_info=call_result)
                )
            except StarkException as ex:
                self.reporter.report(
                    subject=test_subject,
                    case_result=FailedCase(
                        file_path=test_subject.test_path,
                        function_name=function["name"],
                        exception=ex,
                    ),
                )
