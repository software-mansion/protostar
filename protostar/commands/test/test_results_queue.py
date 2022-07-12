from multiprocessing.managers import ValueProxy
from typing import TYPE_CHECKING

from protostar.commands.test.test_cases import TestCaseResult, PassedTestCase

if TYPE_CHECKING:
    import queue


class TestResultsQueue:
    def __init__(
        self,
        shared_queue: "queue.Queue[TestCaseResult]",
        any_failed_or_broken_shared_value: ValueProxy,
    ) -> None:
        self._shared_queue = shared_queue
        self._any_failed_or_broken_shared_value = any_failed_or_broken_shared_value

    def get(self) -> TestCaseResult:
        return self._shared_queue.get(block=True, timeout=1000)

    def put(self, item: TestCaseResult) -> None:
        if not isinstance(item, PassedTestCase):
            self._any_failed_or_broken_shared_value.value = True
        self._shared_queue.put(item)

    def any_failed_or_broken(self) -> bool:
        return self._any_failed_or_broken_shared_value.value
