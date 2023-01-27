# pylint: disable=line-too-long

from protostar.cheatable_starknet.cheaters.expect_events_controller import (
    EventMatchingResult,
    AcceptedEventMatching,
    SkippedEventMatching,
    FailedEventMatching,
    Event,
)
from protostar.starknet import Address, Selector

from .cairo_execution_environment_exceptions import (
    ExpectEventsMismatchReportedException,
)


def test_expect_events_mismatch_exception():
    ex = ExpectEventsMismatchReportedException(
        message="expect_events failed",
        event_matching_result=EventMatchingResult(
            event_matchings=[
                AcceptedEventMatching(
                    emitted_event=Event(
                        from_address=Address(1),
                        key=Selector("foo"),
                        data=[1],
                    ),
                    expected_event=Event(from_address=Address(1), key=Selector("foo")),
                ),
                SkippedEventMatching(
                    emitted_event=Event(
                        from_address=Address(2), key=Selector("bar"), data=[1]
                    )
                ),
                FailedEventMatching(
                    expected_event=Event(from_address=Address(3), key=Selector("baz"))
                ),
            ],
        ),
    )

    result = str(ex)

    assert result == "\n".join(
        [
            "expect_events failed",
            "  [pass] name: foo, from_address: 0x0000000000000000000000000000000000000000000000000000000000000001, data: [1]",
            "  [skip] name: bar, from_address: 0x0000000000000000000000000000000000000000000000000000000000000002, data: [1]",
            "  [fail] name: baz, from_address: 0x0000000000000000000000000000000000000000000000000000000000000003",
        ]
    )
