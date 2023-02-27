from typing import Optional

from starkware.cairo.lang.compiler.program import Program

from protostar.cairo.cairo1_test_suite_parser import ProtostarCasm
import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo_testing import CairoTestExecutionState
from protostar.cairo_testing.cairo_test_runner import CairoTestRunner
from protostar.cairo_testing.execution_environments.cairo_test_execution_environment import (
    CairoTestExecutionEnvironment,
)
from protostar.testing import TestResult
from protostar.testing.test_case_runners.cairo1_test_case_runner import (
    Cairo1TestCaseRunner,
)

from protostar.testing.test_config import TestConfig
from protostar.testing.test_suite import (
    Cairo1TestSuite,
    TestSuite,
    TestCase,
    TestCaseWithOffsets,
)
from protostar.testing.testing_seed import Seed


class Cairo1TestRunnerAdapter(CairoTestRunner):
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
