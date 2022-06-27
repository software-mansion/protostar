from typing import TYPE_CHECKING, Callable, List, Optional, Union

from typing_extensions import NotRequired, TypedDict

from protostar.commands.test.expected_event import ExpectedEvent
from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.commands.test.test_environment_exceptions import (
    ExpectedEventMissingException,
)

if TYPE_CHECKING:
    from protostar.commands.test.starkware.forkable_starknet import ForkableStarknet
    from protostar.commands.test.test_execution_environment import (
        TestExecutionEnvironment,
    )


class ExpectEventsCheatcode(Cheatcode):
    RawExpectedEventDictType = TypedDict(
        "ExpectedEvent",
        {"name": str, "data": NotRequired[List[int]], "from_address": NotRequired[int]},
    )
    RawExpectedEventType = Union[RawExpectedEventDictType, str]

    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        starknet: "ForkableStarknet",
        test_execution_environment: "TestExecutionEnvironment",
    ):
        super().__init__(syscall_dependencies)
        self.starknet = starknet
        self.test_execution_environment = test_execution_environment

    @property
    def name(self) -> str:
        return "expect_events"

    def build(self) -> Callable:
        return self.expect_events

    def expect_events(
        self,
        *raw_expected_events: RawExpectedEventType,
    ) -> None:
        def compare_expected_and_emitted_events():

            expected_events: List[ExpectedEvent] = []

            for raw_expected_event in raw_expected_events:
                expected_events.append(
                    self._convert_raw_expected_event_to_expected_event(
                        raw_expected_event
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
                    event_selector_to_name_map=self.starknet.cheatable_state.cheatable_carried_state.event_selector_to_name_map,
                )

        self.test_execution_environment.add_test_finish_hook(
            compare_expected_and_emitted_events
        )

    @staticmethod
    def _convert_raw_expected_event_to_expected_event(
        raw_expected_event: RawExpectedEventType,
    ):
        name: str
        data: Optional[List[int]] = None
        from_address: Optional[int] = None
        if isinstance(raw_expected_event, str):
            name = raw_expected_event
        else:
            name = raw_expected_event["name"]
            if "data" in raw_expected_event:
                data = raw_expected_event["data"]
            if "from_address" in raw_expected_event:
                from_address = raw_expected_event["from_address"]

        return ExpectedEvent(name=name, data=data, from_address=from_address)
