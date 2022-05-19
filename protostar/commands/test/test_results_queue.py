from typing import TYPE_CHECKING

from protostar.commands.test.test_cases import TestCaseResult

if TYPE_CHECKING:
    import queue


class TestResultsQueue:
    def __init__(self, shared_queue: "queue.Queue[TestCaseResult]") -> None:
        self._shared_queue = shared_queue

    def get(self) -> TestCaseResult:
        return self._shared_queue.get(block=True, timeout=1000)

    def put(self, item: TestCaseResult) -> None:
        self._shared_queue.put(item)
