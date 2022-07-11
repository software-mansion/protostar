import multiprocessing
import signal
from typing import TYPE_CHECKING, Callable, List
import ctypes

from protostar.commands.test.test_results_queue import TestResultsQueue
from protostar.commands.test.test_runner import TestRunner
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

    def run(
        self,
        test_collector_result: "TestCollector.Result",
        include_paths: List[str],
        is_account_contract: bool,
        disable_hint_validation: bool,
        exit_first: bool,
    ):
        with multiprocessing.Manager() as manager:
            test_results_queue = TestResultsQueue(
                manager.Queue(),
                manager.Value(
                    ctypes.c_bool,
                    (len(test_collector_result.broken_test_suites) > 0) and exit_first,
                ),
            )
            setups: List[TestRunner.WorkerArgs] = [
                TestRunner.WorkerArgs(
                    test_suite,
                    test_results_queue=test_results_queue,
                    include_paths=include_paths,
                    is_account_contract=is_account_contract,
                    disable_hint_validation_in_external_contracts=disable_hint_validation,
                )
                for test_suite in test_collector_result.test_suites
            ]

            # A test case was broken
            if exit_first and test_results_queue.failed():
                self._live_logger.exit_before_log(test_collector_result)
                return

            try:
                with multiprocessing.Pool(
                    multiprocessing.cpu_count(),
                    lambda: signal.signal(
                        signal.SIGINT, signal.SIG_IGN
                    ),  # prevents showing a stacktrace on cmd/ctrl + c
                ) as pool:
                    results = pool.map_async(self._worker, setups)

                    self._live_logger.log(test_results_queue, test_collector_result)

                    if exit_first and test_results_queue.failed():
                        pool.terminate()
                        return

                    results.get()
            except KeyboardInterrupt:
                return
