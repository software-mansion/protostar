from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

from protostar.starknet import Address, CairoData, Selector, ReportedException

if TYPE_CHECKING:
    from protostar.testing import Hook
    from protostar.cheatable_starknet.cheatables.cheatable_starknet_facade import (
        CheatableStarknetFacade,
    )
    from protostar.cairo_testing import CairoTestExecutionState


@dataclass
class Event:
    from_address: Address
    key: Selector
    data: Optional[CairoData] = None


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
        return len(self.failed_event_matchings) == 0


class ExpectEventsController:
    def __init__(
        self,
        test_finish_hook: "Hook",
        test_execution_state: "CairoTestExecutionState",
        cheatable_starknet_facade: "CheatableStarknetFacade",
    ) -> None:
        self._test_execution_state = test_execution_state
        self._cheatable_starknet_facade = cheatable_starknet_facade
        self._test_finish_hook = test_finish_hook
        self._test_finish_hook.on(self.compare_expected_and_actual_results)

    def add_expectation(self, expected_events: list[Event]):
        self._test_execution_state.event_expectations.append(expected_events)

    def compare_expected_and_actual_results(self):
        for expected_events in self._test_execution_state.event_expectations:
            matching_result = match_events(
                expected_events=expected_events,
                emitted_events=self._cheatable_starknet_facade.get_emitted_events(),
            )
            if not matching_result.should_be_accepted:
                raise ExpectEventsMismatchReportedException(matching_result)


def match_events(
    expected_events: list[Event], emitted_events: list[Event]
) -> EventMatchingResult:
    assert len(expected_events) > 0
    expected_events_queue = deque(expected_events)
    event_matchings: list[EventMatching] = []
    for emitted_event in emitted_events:
        try:
            event_matchings.append(
                match_expected_and_emitted_event(
                    emitted_event=emitted_event,
                    expected_event=expected_events_queue[0],
                    on_accepted=expected_events_queue.popleft,
                )
            )
        except IndexError:
            event_matchings.append(SkippedEventMatching(emitted_event=emitted_event))
    failed_event_matchings = [
        FailedEventMatching(expected_event)
        for expected_event in list(expected_events_queue)
    ]
    return EventMatchingResult(
        event_matchings=[*event_matchings, *failed_event_matchings],
    )


def match_expected_and_emitted_event(
    emitted_event: Event,
    expected_event: Event,
    on_accepted: Callable,
):
    if should_accept_event_matching(
        expected_event=expected_event, emitted_event=emitted_event
    ):
        on_accepted()
        return AcceptedEventMatching(
            emitted_event=emitted_event,
            expected_event=expected_event,
        )
    return SkippedEventMatching(emitted_event=emitted_event)


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
                lines.append(self._format_accepted_event_matching(event_matching))
            elif isinstance(event_matching, SkippedEventMatching):
                lines.append(self._format_skipped_event_matching(event_matching))
            elif isinstance(event_matching, FailedEventMatching):
                lines.append(self._format_failed_event_matching(event_matching))
            else:
                assert False, f"Unexpected event_matching: {event_matching}"
        return lines

    def _format_accepted_event_matching(self, event_matching: AcceptedEventMatching):
        return self._format_event(event=event_matching.emitted_event, prefix="[pass]")

    def _format_failed_event_matching(self, event_matching: FailedEventMatching):
        return self._format_event(event=event_matching.expected_event, prefix="[fail]")

    def _format_skipped_event_matching(self, event_matching: SkippedEventMatching):
        return self._format_event(event=event_matching.emitted_event, prefix="[skip]")

    def _format_event(self, event: Event, prefix: str):
        segments: list[str] = []
        segments.append(f"name: {event.key}")
        segments.append(f"from_address: {event.from_address}")
        if event.data is not None:
            segments.append(f"data: {event.data}")
        details = ", ".join(segments)
        return f"{prefix} {details}"
