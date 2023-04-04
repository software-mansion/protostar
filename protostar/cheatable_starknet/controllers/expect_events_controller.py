from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from protostar.starknet import Address, CairoData, Selector, ReportedException

if TYPE_CHECKING:
    from protostar.cairo_testing import CairoTestExecutionState
    from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
        CheatableCachedState,
    )


@dataclass
class Event:
    from_address: Address
    key: Selector
    data: Optional[CairoData] = None


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
class FailedEventMatching(EventMatching):
    expected_event: Event


@dataclass
class EventMatchingResult:
    event_matchings: list[EventMatching]

    @property
    def failed_event_matchings(self):
        return [
            matching
            for matching in self.event_matchings
            if isinstance(matching, FailedEventMatching)
        ]

    @property
    def should_be_accepted(self) -> bool:
        return not self.failed_event_matchings


class ExpectEventsController:
    def __init__(
        self,
        test_execution_state: "CairoTestExecutionState",
        cheatable_state: "CheatableCachedState",
    ) -> None:
        self._test_execution_state = test_execution_state
        self._cheatable_state = cheatable_state

    def add_expected_events(self, expected_events: list[Event]):
        self._test_execution_state.expected_events_list.append(expected_events)

    def compare_expected_and_actual_results(self):
        for expected_events in self._test_execution_state.expected_events_list:
            matching_result = match_events(
                expected_events=expected_events,
                emitted_events=self._cheatable_state.emitted_events,
            )
            if not matching_result.should_be_accepted:
                raise ExpectEventsMismatchReportedException(matching_result)


def match_events(
    expected_events: list[Event], emitted_events: list[Event]
) -> EventMatchingResult:
    event_matchings: list[EventMatching] = []
    for emitted_event in emitted_events:
        if expected_events and should_accept_event_matching(
            expected_event=expected_events[0], emitted_event=emitted_event
        ):
            event_matchings.append(
                AcceptedEventMatching(
                    emitted_event=emitted_event,
                    expected_event=expected_events[0],
                )
            )
            expected_events.pop(0)
        else:
            event_matchings.append(SkippedEventMatching(emitted_event=emitted_event))
    failed_event_matchings = [
        FailedEventMatching(expected_event) for expected_event in expected_events
    ]
    return EventMatchingResult(
        event_matchings=[*event_matchings, *failed_event_matchings],
    )


def should_accept_event_matching(expected_event: Event, emitted_event: Event) -> bool:
    return (
        expected_event.key == emitted_event.key
        and (expected_event.data is None or (expected_event.data == emitted_event.data))
        and expected_event.from_address == emitted_event.from_address
    )


class ExpectEventsMismatchReportedException(ReportedException):
    def __init__(
        self, event_matching_result: EventMatchingResult, *args: object
    ) -> None:
        super().__init__(*args)
        self.event_matching_result = event_matching_result

    def __reduce__(self):
        return (
            type(self),
            (self.event_matching_result,),
            self.__getstate__(),
        )

    def __str__(self) -> str:
        formatted_event_matches_lines = self._get_event_matches_formatted_lines()
        return "Expect Events mismatch\n  " + (
            "\n  ".join(formatted_event_matches_lines)
        )

    def _get_event_matches_formatted_lines(self):
        lines: list[str] = []
        for event_matching in self.event_matching_result.event_matchings:
            if isinstance(event_matching, AcceptedEventMatching):
                lines.append(
                    self._format_event(
                        event=event_matching.emitted_event, prefix="[pass]"
                    )
                )
            elif isinstance(event_matching, SkippedEventMatching):
                lines.append(
                    self._format_event(
                        event=event_matching.emitted_event, prefix="[skip]"
                    )
                )
            elif isinstance(event_matching, FailedEventMatching):
                lines.append(
                    self._format_event(
                        event=event_matching.expected_event, prefix="[fail]"
                    )
                )
            else:
                assert False, f"Unexpected event_matching: {event_matching}"
        return lines

    def _format_event(self, event: Event, prefix: str):
        segments: list[str] = []
        segments.append(f"name: {event.key}")
        segments.append(f"from_address: {event.from_address}")
        if event.data is not None:
            segments.append(f"data: {event.data}")
        details = ", ".join(segments)
        return f"{prefix} {details}"
