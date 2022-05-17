from typing import TYPE_CHECKING, Tuple

from protostar.commands.test.test_cases import TestCaseResult
from protostar.commands.test.test_suite import TestSuite

if TYPE_CHECKING:
    import queue


class TestResultsQueue:
    def __init__(
        self, shared_queue: "queue.Queue[Tuple[TestSuite, TestCaseResult]]"
    ) -> None:
        self._shared_queue = shared_queue

    def get(self) -> Tuple[TestSuite, TestCaseResult]:
        return self._shared_queue.get(block=True, timeout=1000)

    def put(self, item: Tuple[TestSuite, TestCaseResult]) -> None:
        self._shared_queue.put(item)
