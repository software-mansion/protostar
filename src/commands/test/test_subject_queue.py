from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple

from src.commands.test.test_cases import TestCaseResult

if TYPE_CHECKING:
    import queue


@dataclass
class TestSubject:
    """
    A dataclass consisting of identification of a single test bundle, and target functions
    """

    test_path: Path
    test_functions: List[dict]


class TestSubjectQueue:
    def __init__(
        self, shared_queue: "queue.Queue[Tuple[TestSubject, TestCaseResult]]"
    ) -> None:
        self._shared_queue = shared_queue

    def dequeue(self) -> Tuple[TestSubject, TestCaseResult]:
        return self._shared_queue.get(block=True, timeout=1000)

    def enqueue(self, item: Tuple[TestSubject, TestCaseResult]) -> None:
        self._shared_queue.put(item)
