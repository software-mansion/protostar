from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from protostar.cheatable_starknet.cheatable_cached_state import CheatableCachedState
from protostar.starknet import Address, CairoOrPythonData, Selector
from protostar.testing import Hook

if TYPE_CHECKING:
    from protostar.testing.starkware.test_execution_state import TestExecutionState


@dataclass
class ExpectedEvent:
    address: Address
    selector: Selector
    data: Optional[CairoOrPythonData]


class ExpectEventsController:
    def __init__(
        self,
        test_finish_hook: Hook,
        test_execution_state: "TestExecutionState",
        cheatable_state: "CheatableCachedState",
    ) -> None:
        self._test_execution_state = test_execution_state
        self._cheatable_state = cheatable_state
        self._test_finish_hook = test_finish_hook
        self._test_finish_hook.on(self.compare_expected_and_actual_results)

    async def execute(self, expected_events: list[ExpectedEvent]):
        self._test_execution_state.add_events_expectation(expected_events)

    def compare_expected_and_actual_results(self):
        expected_events = self._test_execution_state.get_events_expectations()
        actual_events = self._cheatable_state.get_emitted_events()
        assert False, "Not implemented"
