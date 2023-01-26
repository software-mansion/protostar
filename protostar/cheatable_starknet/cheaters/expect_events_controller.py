from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from protostar.starknet import Address, CairoOrPythonData, Selector
from protostar.testing import Hook

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatables.cheatable_starknet_facade import (
        CheatableStarknetFacade,
    )
    from protostar.cairo_testing import CairoTestExecutionState


@dataclass
class Event:
    from_address: Address
    key: Selector
    data: Optional[CairoOrPythonData]


EventsExpectation = list[Event]


@dataclass
class EventMatching:
    pass


@dataclass
class SkippedEventMatching(EventMatching):
    emitted_event: Event


@dataclass
class AcceptedEventMatching(EventMatching):
    emitted_event: Event
    expected_event: Event


@dataclass
class MatchingResult:
    event_matchings: list[EventMatching]
    unmatched_expected_events: list[Event]

    @property
    def are_all_matches_accepted(self) -> bool:
        for event_matching in self.event_matchings:
            if not isinstance(event_matching, AcceptedEventMatching):
                return False
        return True


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
        self._test_execution_state.event_expectations.append(expected_events)

    def compare_expected_and_actual_results(self):
        for expected_events in self._test_execution_state.event_expectations:
            matching_result = self.match_events(
                expected_events=expected_events,
                emitted_events=self._cheatable_starknet_facade.get_emitted_events(),
            )
            if not matching_result.are_all_matches_accepted:
                raise ExpectEventsMismatchException(matching_result)

    def match_events(
        self, expected_events: list[Event], emitted_events: list[Event]
    ) -> MatchingResult:
        assert len(expected_events) > 0
        expected_events_queue = deque(expected_events)
        event_matchings: list[EventMatching] = []
        for emitted_event in emitted_events:
            try:
                expected_event = expected_events_queue[0]
                if self.should_accept_event_matching(
                    expected_event=expected_event, emitted_event=emitted_event
                ):
                    event_matchings.append(
                        AcceptedEventMatching(
                            emitted_event=emitted_event,
                            expected_event=expected_event,
                        )
                    )
                    expected_events_queue.popleft()
                else:
                    event_matchings.append(
                        SkippedEventMatching(emitted_event=emitted_event)
                    )
            except IndexError:
                event_matchings.append(
                    SkippedEventMatching(emitted_event=emitted_event)
                )

        return MatchingResult(
            event_matchings=event_matchings,
            unmatched_expected_events=list(expected_events_queue),
        )

    def should_accept_event_matching(
        self, expected_event: Event, emitted_event: Event
    ) -> bool:
        return (
            expected_event.key == emitted_event.key
            and expected_event.data is None
            or expected_event.data == emitted_event.data
            and expected_event.from_address == emitted_event.from_address
        )


@dataclass
class ExpectEventsMismatchException(Exception):
    matching_result: MatchingResult
