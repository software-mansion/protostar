import ctypes
from multiprocessing.managers import SyncManager

from .test_collector import TestCollector
from .test_results import NONNEGATIVE_RESULTS, TestResult


class SharedTestsState:
    def __init__(
        self,
        test_collector_result: "TestCollector.Result",
        manager: SyncManager,
    ) -> None:
        self._shared_queue = manager.Queue()
        self._any_failed_or_broken_shared_value = manager.Value(
            ctypes.c_bool,
            (len(test_collector_result.broken_test_suites) > 0),
        )

    def get_result(self) -> TestResult:
        return self._shared_queue.get(block=True, timeout=20000)

    def put_result(self, item: TestResult) -> None:
        if not isinstance(item, NONNEGATIVE_RESULTS):
            self._any_failed_or_broken_shared_value.value = True
        self._shared_queue.put(item)

    def any_failed_or_broken(self) -> bool:
        return self._any_failed_or_broken_shared_value.value
