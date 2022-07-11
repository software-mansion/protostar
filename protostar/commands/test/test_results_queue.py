from ast import Pass
from concurrent.futures import thread
import multiprocessing
from multiprocessing.managers import ValueProxy
import threading
from typing import TYPE_CHECKING

from protostar.commands.test.test_cases import TestCaseResult, PassedTestCase

if TYPE_CHECKING:
    import queue


class TestResultsQueue:
    def __init__(
        self, shared_queue: "queue.Queue[TestCaseResult]", failed: ValueProxy
    ) -> None:
        self._shared_queue = shared_queue
        self._failed = failed

    def get(self) -> TestCaseResult:
        return self._shared_queue.get(block=True, timeout=1000)

    def put(self, item: TestCaseResult) -> None:
        if not isinstance(item, PassedTestCase):
            self._failed.value = True
        self._shared_queue.put(item)

    def failed(self) -> bool:
        return self._failed.value
