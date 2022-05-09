from typing import TYPE_CHECKING, Tuple

from src.commands.test.cases import CaseResult
from src.commands.test.utils import TestSubject

if TYPE_CHECKING:
    import queue


class TestSubjectQueue:
    def __init__(
        self, shared_queue: "queue.Queue[Tuple[TestSubject, CaseResult]]"
    ) -> None:
        self._shared_queue = shared_queue

    def dequeue(self) -> Tuple[TestSubject, CaseResult]:
        return self._shared_queue.get(block=True, timeout=1000)

    def enqueue(self, item: Tuple[TestSubject, CaseResult]) -> None:
        self._shared_queue.put(item)
