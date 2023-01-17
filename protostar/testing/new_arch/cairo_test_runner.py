import asyncio
import traceback
from logging import getLogger
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

from starkware.cairo.lang.compiler.program import Program

from protostar.compiler import (
    ProjectCompiler,
    ProjectCompilerConfig,
)
from protostar.compiler.project_cairo_path_builder import ProjectCairoPathBuilder
from protostar.starknet import ReportedException
from protostar.starknet.compiler.cairo_compilation import CairoCompiler
from protostar.configuration_file.configuration_file_factory import (
    ConfigurationFileFactory,
)
from protostar.protostar_exception import ProtostarException
from protostar.starknet.compiler.starknet_compilation import (
    CompilerConfig,
)
from protostar.testing import (
    UnexpectedBrokenTestSuiteResult,
    BrokenTestSuiteResult,
    SharedTestsState,
    TestResult,
)
from protostar.testing.new_arch.cairo_test_execution_environment import (
    CairoTestExecutionEnvironment,
)
from protostar.testing.new_arch.cairo_test_execution_state import (
    CairoTestExecutionState,
)
from protostar.testing.test_case_runners.standard_test_case_runner import (
    StandardTestCaseRunner,
)
from protostar.testing.test_config import TestConfig
from protostar.testing.test_suite import TestSuite, TestCase
from protostar.testing.testing_seed import Seed

if TYPE_CHECKING:
    from protostar.testing.test_runner import TestRunner

logger = getLogger()


# pylint: disable=too-many-instance-attributes
class CairoTestRunner:
    def __init__(
        self,
        project_root_path: Path,
        cwd: Path,
        shared_tests_state: SharedTestsState,
        active_profile_name: Optional[str],
        include_paths: Optional[List[str]] = None,
        profiling: bool = False,
        gas_estimation_enabled: bool = False,
    ):
        self._gas_estimation_enabled = gas_estimation_enabled
        self.shared_tests_state = shared_tests_state
        self.profiling = profiling
        include_paths = include_paths or []

        configuration_file = ConfigurationFileFactory(
            cwd=cwd, active_profile_name=active_profile_name
        ).create()

        relative_cairo_path = [Path(s_pth).resolve() for s_pth in include_paths]
        project_compiler_config = ProjectCompilerConfig(
            relative_cairo_path=relative_cairo_path,
            debugging_info_attached=profiling,
        )
        self.project_cairo_path_builder = ProjectCairoPathBuilder(project_root_path)
        self.project_compiler = ProjectCompiler(
            project_root_path=project_root_path,
            configuration_file=configuration_file,
            default_config=project_compiler_config,
            project_cairo_path_builder=self.project_cairo_path_builder,
        )

        project_cairo_path = (
            self.project_cairo_path_builder.build_project_cairo_path_list(
                relative_cairo_path
            )
        )

        compiler_config = CompilerConfig(
            include_paths=[str(path) for path in project_cairo_path],
            disable_hint_validation=project_compiler_config.hint_validation_disabled,
        )
        self.cairo_compiler = CairoCompiler(config=compiler_config)

    @classmethod
    def worker(cls, args: "TestRunner.WorkerArgs"):
        asyncio.run(
            cls(
                include_paths=args.include_paths,
                project_root_path=args.project_root_path,
                profiling=args.profiling,
                cwd=args.cwd,
                shared_tests_state=args.shared_tests_state,
                active_profile_name=args.active_profile_name,
                gas_estimation_enabled=args.gas_estimation_enabled,
            ).run_test_suite(
                test_suite=args.test_suite,
                testing_seed=args.testing_seed,
                max_steps=args.max_steps,
            )
        )

    async def _build_execution_state(self, test_config: TestConfig):
        state = await CairoTestExecutionState.from_test_config(
            test_config=test_config,
            project_compiler=self.project_compiler,
        )
        # TODO #1281: Execute __setup__ using test_execution_state & cairo_setup_execution_environment
        return state

    async def run_test_suite(
        self,
        test_suite: TestSuite,
        testing_seed: Seed,
        max_steps: Optional[int],
    ):
        test_config = TestConfig(  # pylint: disable=unused-variable
            seed=testing_seed,
            profiling=self.profiling,
            max_steps=max_steps,
            gas_estimation_enabled=self._gas_estimation_enabled,
        )
        test_execution_state = await self._build_execution_state(test_config)

        try:
            preprocessed = self.cairo_compiler.preprocess(test_suite.test_path)
            compiled_program = self.cairo_compiler.compile_preprocessed(preprocessed)

            await self._invoke_test_cases(
                test_suite=test_suite,
                program=compiled_program,
                test_execution_state=test_execution_state,
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

    async def _invoke_test_cases(
        self,
        test_suite: TestSuite,
        program: Program,
        test_execution_state: CairoTestExecutionState,
    ) -> None:
        for test_case in test_suite.test_cases:
            test_result = await self._invoke_test_case(
                test_case=test_case,
                program=program,
                initial_state=test_execution_state,
            )
            self.shared_tests_state.put_result(test_result)

    async def _invoke_test_case(
        self,
        initial_state: CairoTestExecutionState,
        test_case: TestCase,
        program: Program,
    ) -> TestResult:
        state: CairoTestExecutionState = initial_state.fork()

        # TODO #1281: Invoke setup case
        # if test_case.setup_fn_name:
        #     setup_case_result = await run_setup_case(test_case, state)
        #     if isinstance(setup_case_result, BrokenSetupCaseResult):
        #         return setup_case_result.into_broken_test_case_result()
        #     if isinstance(setup_case_result, SkippedSetupCaseResult):
        #         return setup_case_result.into_skipped_test_case_result()

        # TODO #1283, #1282: Plug in other test modes (fuzzing, parametrized)
        # state.determine_test_mode(test_case)

        test_execution_environment = CairoTestExecutionEnvironment(
            program=program,
            state=state,
        )
        return await StandardTestCaseRunner(
            test_execution_environment=test_execution_environment,
            test_case=test_case,
            output_recorder=state.output_recorder,
            stopwatch=state.stopwatch,
        ).run()
