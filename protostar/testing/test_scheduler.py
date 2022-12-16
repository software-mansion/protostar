import multiprocessing
import signal
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional
import dataclasses

from protostar.testing import (
    TestingSummary,
)
from protostar.testing import (
    BrokenTestSuiteResult,
    TestResult,
)

from .test_collector import TestCollector
from .test_runner import TestRunner
from .test_shared_tests_state import SharedTestsState
from .testing_seed import Seed


if TYPE_CHECKING:
    from protostar.commands.test.testing_live_logger import TestingLiveLogger


def make_path_relative_if_possible(test_result: TestResult, path: Path) -> TestResult:
    try:
        test_result = dataclasses.replace(
            test_result,
            file_path=test_result.file_path.resolve().relative_to(path.resolve()),
        )
    except ValueError:
        # We do this to preserve the functionality of running tests that are outside of the project
        pass
    return test_result


def _update_summary(
    shared_tests_state: SharedTestsState,
    test_collector_result: "TestCollector.Result",
    testing_summary: TestingSummary,
    project_root_path: Path,
    exit_first: bool,
):
    tests_left_n = test_collector_result.test_cases_count
    while tests_left_n > 0:
        test_result: TestResult = shared_tests_state.get_result()
        testing_summary.extend([test_result])
        test_result = make_path_relative_if_possible(test_result, project_root_path)
        if exit_first and shared_tests_state.any_failed_or_broken():
            tests_left_n = 0
            return
        if isinstance(test_result, BrokenTestSuiteResult):
            tests_in_case_count = len(test_result.test_case_names)
            tests_left_n -= tests_in_case_count
        else:
            tests_left_n -= 1


class TestScheduler:
    def __init__(
        self,
        live_logger: "TestingLiveLogger",
        worker: Callable[
            [TestRunner.WorkerArgs],
            None,
        ],
    ):
        self._live_logger = live_logger
        self._worker = worker

    def run(
        self,
        test_collector_result: "TestCollector.Result",
        include_paths: List[str],
        disable_hint_validation: bool,
        profiling: bool,
        exit_first: bool,
        testing_seed: Seed,
        max_steps: Optional[int],
        project_root_path: Path,
        cwd: Path,
        active_profile_name: Optional[str],
        gas_estimation_enabled: bool,
        structured_format: bool = False,
    ):
        with multiprocessing.Manager() as manager:
            shared_tests_state = SharedTestsState(
                test_collector_result=test_collector_result, manager=manager
            )
            setups: List[TestRunner.WorkerArgs] = [
                TestRunner.WorkerArgs(
                    test_suite,
                    shared_tests_state=shared_tests_state,
                    include_paths=include_paths,
                    disable_hint_validation_in_user_contracts=disable_hint_validation,
                    profiling=profiling,
                    testing_seed=testing_seed,
                    max_steps=max_steps,
                    project_root_path=project_root_path,
                    active_profile_name=active_profile_name,
                    cwd=cwd,
                    gas_estimation_enabled=gas_estimation_enabled,
                )
                for test_suite in test_collector_result.test_suites
            ]

            # A test case was broken
            if exit_first and shared_tests_state.any_failed_or_broken():
                self._live_logger.log_testing_summary(test_collector_result)
                return

            try:
                with multiprocessing.Pool(
                    processes=multiprocessing.cpu_count(),
                    initializer=_init_worker,
                ) as pool:
                    results = pool.map_async(self._worker, setups)

                    self._live_logger.log(
                        shared_tests_state, test_collector_result, structured_format
                    )

                    if exit_first and shared_tests_state.any_failed_or_broken():
                        pool.terminate()
                        return

                    results.get()
            except KeyboardInterrupt:
                return


# Note: This function has to be top-level function, because it is being pickled by multiprocessing.
def _init_worker():
    # Prevent showing a stacktrace on CMD/CTRL+C.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
