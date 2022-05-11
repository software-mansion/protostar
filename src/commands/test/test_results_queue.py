from typing import TYPE_CHECKING, Tuple

from src.commands.test.test_cases import TestCaseResult
from src.commands.test.test_subject import TestSubject

if TYPE_CHECKING:
    import queue


class TestResultsQueue:
    def __init__(
        self, shared_queue: "queue.Queue[Tuple[TestSubject, TestCaseResult]]"
    ) -> None:
        self._shared_queue = shared_queue

    def get(self) -> Tuple[TestSubject, TestCaseResult]:
        return self._shared_queue.get(block=True, timeout=1000)

    def put(self, item: Tuple[TestSubject, TestCaseResult]) -> None:
        self._shared_queue.put(item)
