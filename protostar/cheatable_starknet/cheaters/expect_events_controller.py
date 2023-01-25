from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from protostar.cheatable_starknet.cheatables.cheatable_starknet_facade import (
    CheatableStarknetFacade,
)
from protostar.starknet import Address, CairoOrPythonData, Selector
from protostar.testing import Hook

if TYPE_CHECKING:
    from protostar.cairo_testing import CairoTestExecutionState


@dataclass
class Event:
    from_address: Address
    key: Selector
    data: Optional[CairoOrPythonData]


EventsExpectation = list[Event]


class ExpectEventsController:
    def __init__(
        self,
        test_finish_hook: Hook,
        test_execution_state: "CairoTestExecutionState",
        cheatable_starknet_facade: "CheatableStarknetFacade",
    ) -> None:
        self._test_execution_state = test_execution_state
        self._cheatable_starknet_facade = cheatable_starknet_facade
        self._test_finish_hook = test_finish_hook
        self._test_finish_hook.on(self.compare_expected_and_actual_results)

    async def execute(self, expected_events: list[Event]):
        self._test_execution_state.add_events_expectation(expected_events)

    def compare_expected_and_actual_results(self):
        expected_events = self._test_execution_state.get_events_expectations()
        actual_events = self._cheatable_starknet_facade.get_emitted_events()
        assert False, "Not implemented"
