import multiprocessing
import signal
from typing import TYPE_CHECKING, Callable, List, Tuple

from src.commands.test.test_runner import TestRunner
from src.commands.test.testing_live_logger import TestingLiveLogger
from src.commands.test.test_subject_queue import TestSubjectQueue

if TYPE_CHECKING:
    from src.commands.test.test_collector import TestCollector


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
        self, test_collector_result: "TestCollector.Result", include_paths: List[str]
    ):
        with multiprocessing.Manager() as manager:
            testing_queue = TestSubjectQueue(manager.Queue())
            setups: List[Tuple[TestRunner.WorkerArgs]] = [
                (
                    TestRunner.WorkerArgs(
                        subject,
                        testing_queue,
                        include_paths,
                    ),
                )
                for subject in test_collector_result.test_subjects
            ]

            try:
                with multiprocessing.Pool(
                    multiprocessing.cpu_count(),
                    lambda: signal.signal(
                        signal.SIGINT, signal.SIG_IGN
                    ),  # prevents showing a stacktrace on cmd/ctrl + c
                ) as pool:
                    pool.starmap_async(self._worker, setups)
                    self._live_logger.log(testing_queue, test_collector_result)
            except KeyboardInterrupt:
                return
