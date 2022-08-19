import multiprocessing
import signal
from typing import TYPE_CHECKING, Callable, List

from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzConfig,
)
from protostar.commands.test.test_runner import TestRunner
from protostar.commands.test.test_shared_tests_state import SharedTestsState
from protostar.commands.test.testing_live_logger import TestingLiveLogger

if TYPE_CHECKING:
    from protostar.commands.test.test_collector import TestCollector


class TestScheduler:
    def __init__(
        self,
        live_logger: TestingLiveLogger,
        worker: Callable[
            [TestRunner.WorkerArgs],
            None,
        ],
    ):
        self._live_logger = live_logger
        self._worker = worker

    # pylint: disable=too-many-arguments
    def run(
        self,
        test_collector_result: "TestCollector.Result",
        # TODO(mkaput): Remove this along with --fuzz-max-examples argument.
        fuzz_config: FuzzConfig,
        include_paths: List[str],
        disable_hint_validation: bool,
        exit_first: bool,
    ):
        with multiprocessing.Manager() as manager:
            shared_tests_state = SharedTestsState(
                test_collector_result=test_collector_result, manager=manager
            )
            setups: List[TestRunner.WorkerArgs] = [
                TestRunner.WorkerArgs(
                    test_suite,
                    shared_tests_state=shared_tests_state,
                    # TODO(mkaput): Remove this along with --fuzz-max-examples argument.
                    fuzz_config=fuzz_config,
                    include_paths=include_paths,
                    disable_hint_validation_in_user_contracts=disable_hint_validation,
                )
                for test_suite in test_collector_result.test_suites
            ]

            # A test case was broken
            if exit_first and shared_tests_state.any_failed_or_broken():
                self._live_logger.log_testing_summary(test_collector_result)
                return

            try:
                with multiprocessing.Pool(
                    multiprocessing.cpu_count(),
                    lambda: signal.signal(
                        signal.SIGINT, signal.SIG_IGN
                    ),  # prevents showing a stacktrace on cmd/ctrl + c
                ) as pool:
                    results = pool.map_async(self._worker, setups)

                    self._live_logger.log(shared_tests_state, test_collector_result)

                    if exit_first and shared_tests_state.any_failed_or_broken():
                        pool.terminate()
                        return

                    results.get()
            except KeyboardInterrupt:
                return
