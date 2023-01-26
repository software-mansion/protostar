from dataclasses import dataclass

from protostar.testing.test_environment_exceptions import ReportedException
from protostar.cheatable_starknet.cheaters.expect_events_controller import (
    EventMatchingResult,
    AcceptedEventMatching,
    SkippedEventMatching,
    FailedEventMatching,
    Event,
)


@dataclass
class ExpectEventsMismatchReportedException(ReportedException):
    event_matching_result: EventMatchingResult

    def __str__(self) -> str:
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
        return "\n".join(lines)

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
