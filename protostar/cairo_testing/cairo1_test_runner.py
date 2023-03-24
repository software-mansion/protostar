import asyncio
import traceback
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import Optional, TYPE_CHECKING, List

from starkware.cairo.lang.compiler.program import Program

from protostar.cairo import CairoCompiler, CairoCompilerConfig
from protostar.cairo.cairo1_test_suite_parser import ProtostarCasm
from protostar.cairo_testing.execution_environments.cairo_setup_execution_environment import (
    CairoSetupExecutionEnvironment,
)

from protostar.cairo_testing.execution_environments.cairo_setup_case_execution_environment import (
    CairoSetupCaseExecutionEnvironment,
)
from protostar.compiler import (
    Cairo0ProjectCompiler,
    ProjectCairoPathBuilder,
    ProjectCompilerConfig,
)
from protostar.configuration_file import ConfigurationFileFactory
from protostar.starknet import ReportedException
from protostar.protostar_exception import ProtostarException
from protostar.testing import (
    UnexpectedBrokenTestSuiteResult,
    BrokenTestSuiteResult,
    SharedTestsState,
    TestResult,
    BrokenSetupCaseResult,
    PassedSetupCaseResult,
    SetupCaseResult,
)
from protostar.cairo_testing.execution_environments.cairo_test_execution_environment import (
    CairoTestExecutionEnvironment,
)
from protostar.cairo_testing.cairo_test_execution_state import CairoTestExecutionState
from protostar.testing.test_case_runners.cairo1_test_case_runner import (
    Cairo1TestCaseRunner,
)
from protostar.testing.test_config import TestConfig
from protostar.testing.test_environment_exceptions import RevertableException
from protostar.testing.test_suite import (
    TestSuite,
    TestCase,
    Cairo1TestSuite,
    TestCaseWithOffsets,
)
from protostar.testing.testing_seed import Seed
import protostar.cairo.cairo_bindings as cairo1


if TYPE_CHECKING:
    from protostar.testing.test_runner import TestRunner

logger = getLogger()


class Cairo1TestRunner:
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
        self.project_compiler = Cairo0ProjectCompiler(
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

        compiler_config = CairoCompilerConfig(
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
        return await CairoTestExecutionState.from_test_config(
            test_config=test_config,
            project_compiler=self.project_compiler,
        )

    async def _run_suite_setup(
        self,
        test_suite: TestSuite,
        test_execution_state: CairoTestExecutionState,
        program: Program,
    ):
        if test_suite.setup_fn_name:
            env = CairoSetupExecutionEnvironment(
                program=program, state=test_execution_state
            )
            await env.execute(test_suite.setup_fn_name)

    async def _run_setup_case(
        self,
        test_case: TestCase,
        state: CairoTestExecutionState,
        program: Program,
    ) -> SetupCaseResult:
        assert test_case.setup_fn_name
        try:
            execution_environment = CairoSetupCaseExecutionEnvironment(
                state=state, program=program
            )

            with state.stopwatch.lap(test_case.setup_fn_name):
                await execution_environment.execute(test_case.setup_fn_name)

            return PassedSetupCaseResult(
                file_path=test_case.test_path,
                test_case_name=test_case.test_fn_name,
                setup_case_name=test_case.setup_fn_name,
                execution_time=state.stopwatch.total_elapsed,
            )

        except (ReportedException, RevertableException) as ex:
            return BrokenSetupCaseResult(
                file_path=test_case.test_path,
                test_case_name=test_case.test_fn_name,
                setup_case_name=test_case.setup_fn_name,
                exception=ex,
                execution_time=state.stopwatch.total_elapsed,
                captured_stdout=state.output_recorder.get_captures(),
            )

    async def run_test_suite(
        self,
        test_suite: TestSuite,
        testing_seed: Seed,
        max_steps: Optional[int],
    ):
        assert isinstance(
            test_suite, Cairo1TestSuite
        ), "Cairo1 test runner cannot run non-cairo1 suites!"

        with self.suite_exception_handling(test_suite):
            test_config = TestConfig(
                seed=testing_seed,
                profiling=self.profiling,
                max_steps=max_steps,
                gas_estimation_enabled=self._gas_estimation_enabled,
            )
            test_execution_state = await self._build_execution_state(test_config)

            casm_json = cairo1.compile_protostar_sierra_to_casm(
                named_tests=[
                    test_case.test_fn_name for test_case in test_suite.test_cases
                ],
                input_data=test_suite.sierra_output,
            )

            assert casm_json, f"No CASM was emitted for {test_suite.test_path}"

            protostar_casm = ProtostarCasm.from_json(casm_json)

            test_suite.add_offsets_to_cases(offset_map=protostar_casm.offset_map)

            await self._invoke_test_cases(
                test_suite=test_suite,
                program=protostar_casm.program,
                test_execution_state=test_execution_state,
            )

    @contextmanager
    def suite_exception_handling(self, test_suite: TestSuite):
        try:
            yield
        except (ProtostarException, ReportedException, RevertableException) as ex:
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
        assert isinstance(
            test_case, TestCaseWithOffsets
        ), "Cairo 1 runner only supports test cases with offsets!"
        # TODO #1537: Plug in setups
        # if test_case.setup_fn_name:
        #     setup_case_result = await self._run_setup_case(
        #         test_case=test_case, state=state, program=program
        #     )
        #     if isinstance(setup_case_result, BrokenSetupCaseResult):
        #         return setup_case_result.into_broken_test_case_result()

        # TODO #1283, #1282: Plug in other test modes (fuzzing, parametrized)
        # state.determine_test_mode(test_case)

        test_execution_environment = CairoTestExecutionEnvironment(
            state=state,
            program=program,
        )
        return await Cairo1TestCaseRunner(
            function_executor=test_execution_environment,
            test_case=test_case,
            output_recorder=state.output_recorder,
            stopwatch=state.stopwatch,
        ).run()
