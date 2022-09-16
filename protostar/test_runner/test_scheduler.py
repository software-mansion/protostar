import multiprocessing
import signal
from typing import TYPE_CHECKING, Callable, List

from protostar.commands.test.test_shared_tests_state import SharedTestsState
from protostar.commands.test.testing_live_logger import TestingLiveLogger
from protostar.commands.test.testing_seed import Seed
from protostar.test_runner import TestRunner

if TYPE_CHECKING:
    from protostar.test_runner import TestCollector


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

    def run(
        self,
        test_collector_result: "TestCollector.Result",
        include_paths: List[str],
        disable_hint_validation: bool,
        exit_first: bool,
        testing_seed: Seed,
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
                    testing_seed=testing_seed,
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

                    self._live_logger.log(shared_tests_state, test_collector_result)

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
