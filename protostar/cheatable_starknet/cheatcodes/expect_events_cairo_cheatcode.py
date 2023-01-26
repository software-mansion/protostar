from typing import Callable

from typing_extensions import NotRequired, TypedDict

from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.cheatable_starknet.cheaters import CairoCheaters
from protostar.cheatable_starknet.cheaters.expect_events_controller import (
    ExpectEventsController,
    Event,
)
from protostar.starknet import CairoData, Address
from protostar.starknet.selector import Selector


class RawExpectedEvent(TypedDict):
    from_address: int
    name: str
    data: NotRequired[CairoData]


class ExpectEventsCheatcode(CairoCheatcode):
    def __init__(self, controller: ExpectEventsController, cheaters: "CairoCheaters"):
        super().__init__(cheaters)
        self._controller = controller

    @property
    def name(self) -> str:
        return "expect_events"

    def _build(self) -> Callable:
        def expect_events(
            *raw_expected_events: RawExpectedEvent,
        ):
            self._controller.add_expectation(
                self._create_expected_events_from(list(raw_expected_events))
            )

        return expect_events

    def _create_expected_events_from(
        self, raw_expected_events: list[RawExpectedEvent]
    ) -> list[Event]:
        return [
            Event(
                from_address=Address.from_user_input(
                    raw_expected_event["from_address"]
                ),
                key=Selector(raw_expected_event["name"]),
                data=raw_expected_event["data"]
                if "data" in raw_expected_event
                else None,
            )
            for raw_expected_event in raw_expected_events
        ]
