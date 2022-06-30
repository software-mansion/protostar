from typing import TYPE_CHECKING, Callable

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
        *raw_expected_events: ExpectedEvent.CheatcodeInputType,
    ) -> None:
        def compare_expected_and_emitted_events():

            expected_events = list(map(ExpectedEvent, raw_expected_events))

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
