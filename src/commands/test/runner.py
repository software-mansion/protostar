from pathlib import Path
from typing import List, Optional, Pattern

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from src.commands.test.cases import BrokenTest, FailedCase, PassedCase
from src.commands.test.cheatcodes.inject_protostar_hint_locals import (
    inject_protostar_hint_locals,
)
from src.commands.test.cheatcodes.syscall_handler import CheatableSysCallHandler
from src.commands.test.collector import TestCollector
from src.commands.test.reporter import TestReporter
from src.commands.test.utils import TestSubject
from src.utils.config.project import Project
from src.utils.modules import replace_class
from src.utils.starknet_compilation import StarknetCompiler

current_directory = Path(__file__).parent

# fake comment to be able to resolve conflict


class TestRunner:
    reporter: Optional[TestReporter] = None
    include_paths: Optional[List[str]] = None
    _collected_count: Optional[int] = None

    def __init__(
        self,
        project: Optional[Project] = None,
        include_paths: Optional[List[str]] = None,
    ):
        self._is_test_error_expected = False
        self.include_paths = include_paths or []

        if project:
            config = project.load_config()
            self.include_paths.append(str(project.project_root))
            self.include_paths.append(str(Path(project.project_root, config.libs_path)))

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
        original_run_from_entrypoint = CairoFunctionRunner.run_from_entrypoint
        CairoFunctionRunner.run_from_entrypoint = inject_protostar_hint_locals(
            CairoFunctionRunner.run_from_entrypoint, self
        )

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
        CairoFunctionRunner.run_from_entrypoint = original_run_from_entrypoint

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
                if self._is_test_error_expected:
                    self.reporter.report(
                        subject=test_subject,
                        case_result=FailedCase(
                            file_path=test_subject.test_path,
                            function_name=function["name"],
                            exception=BaseException("Expected revert"),
                        ),
                    )
                else:
                    self.reporter.report(
                        subject=test_subject,
                        case_result=PassedCase(tx_info=call_result),
                    )
            except StarkException as ex:
                if self._is_test_error_expected:
                    self._is_test_error_expected = False
                    self.reporter.report(
                        subject=test_subject,
                        case_result=PassedCase(tx_info=None),
                    )
                else:
                    self.reporter.report(
                        subject=test_subject,
                        case_result=FailedCase(
                            file_path=test_subject.test_path,
                            function_name=function["name"],
                            exception=ex,
                        ),
                    )
            self._is_test_error_expected = False

    def expect_revert(self):
        self._is_test_error_expected = True
