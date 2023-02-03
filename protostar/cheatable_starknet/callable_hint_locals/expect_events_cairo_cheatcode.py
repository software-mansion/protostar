from typing import Callable

from typing_extensions import NotRequired, TypedDict

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers.expect_events_controller import (
    ExpectEventsController,
    Event,
)
from protostar.starknet import CairoData, Address
from protostar.starknet.selector import Selector


class RawExpectedEvent(TypedDict):
    from_address: int
    name: str
    data: NotRequired[CairoData]


class ExpectEventsHintLocal(CallableHintLocal):
    def __init__(self, controller: ExpectEventsController):
        self._controller = controller

    @property
    def name(self) -> str:
        return "expect_events"

    def _build(self) -> Callable:
        def expect_events(
            *raw_expected_events: RawExpectedEvent,
        ):
            self._controller.add_expected_events(
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
