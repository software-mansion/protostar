from typing import TYPE_CHECKING, Callable, Optional, Union

from typing_extensions import NotRequired, TypedDict

from protostar.starknet import Cheatcode
from protostar.testing.expected_event import ExpectedEvent
from protostar.testing.test_environment_exceptions import ExpectedEventMissingException
from protostar.utils.data_transformer import (
    CairoOrPythonData,
    from_python_events_transformer,
)
from protostar.utils.hook import Hook

if TYPE_CHECKING:
    from protostar.starknet.forkable_starknet import ForkableStarknet


class RawExpectedEventData(TypedDict):
    name: str
    data: NotRequired[CairoOrPythonData]
    from_address: NotRequired[int]


RawExpectedEventName = str

RawExpectedEvent = Union[RawExpectedEventData, RawExpectedEventName]


class ExpectEventsCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        starknet: "ForkableStarknet",
        finish_hook: Hook,
    ):
        super().__init__(syscall_dependencies)
        self.starknet = starknet
        self.finish_hook = finish_hook

    @property
    def name(self) -> str:
        return "expect_events"

    def build(self) -> Callable:
        return self.expect_events

    def expect_events(
        self,
        *raw_expected_events: RawExpectedEvent,
    ) -> None:
        def compare_expected_and_emitted_events():
            expected_events = list(
                map(
                    self._convert_raw_expected_event_to_expected_event,
                    raw_expected_events,
                )
            )

            (
                matches,
                missing,
            ) = ExpectedEvent.match_state_events_to_expected_to_events(
                expected_events,
                self.starknet.state.events,
            )

            if len(missing) > 0:
                raise ExpectedEventMissingException(
                    matches=matches,
                    missing=missing,
                    # pylint: disable=line-too-long
                    event_selector_to_name_map=self.cheatable_state.event_selector_to_name_map,
                )

        self.finish_hook.on(compare_expected_and_emitted_events)

    def _convert_raw_expected_event_to_expected_event(
        self,
        raw_expected_event: RawExpectedEvent,
    ):

        name: str
        data: Optional[CairoOrPythonData] = None
        from_address: Optional[int] = None
        if isinstance(raw_expected_event, str):
            name = raw_expected_event
        else:
            name = raw_expected_event["name"]
            if "data" in raw_expected_event:
                raw_data = raw_expected_event["data"]
                if isinstance(raw_data, dict):
                    assert (
                        name in self.cheatable_state.event_name_to_contract_abi_map
                    ), "Couldn't map event name to the contract path with that event"

                    contract_abi = self.cheatable_state.event_name_to_contract_abi_map[
                        name
                    ]
                    transformer = from_python_events_transformer(contract_abi, name)
                    data = transformer(raw_data)
                else:
                    data = raw_data
            if "from_address" in raw_expected_event:
                from_address = raw_expected_event["from_address"]

        return ExpectedEvent(name=name, data=data, from_address=from_address)
