import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from starkware.starknet.business_logic.execution.objects import Event
from starkware.starknet.public.abi import get_selector_from_name
from typing_extensions import NotRequired, TypedDict


def collect_immediate_subdirectories(root_dir: Path) -> List[str]:
    assert root_dir.is_dir(), f"{root_dir} is supposed to be a directory!"
    (root, dirs, _) = next(os.walk(str(root_dir.resolve())))
    return [str(Path(root, directory).resolve()) for directory in dirs]


class ExpectedEvent:
    RawEventType = TypedDict(
        "ExpectedEvent",
        {"name": str, "data": NotRequired[List[int]], "from_address": NotRequired[int]},
    )
    CheatcodeInputType = Union[RawEventType, str]

    def __init__(
        self,
        raw_expected_event: CheatcodeInputType,
    ):
        self.data = None
        self.from_address = None
        if isinstance(raw_expected_event, str):
            self.name = raw_expected_event
        else:
            self.name = raw_expected_event["name"]
            if "data" in raw_expected_event:
                self.data = raw_expected_event["data"]
            if "from_address" in raw_expected_event:
                self.from_address = raw_expected_event["from_address"]

    def __str__(self) -> str:
        result: List[str] = []

        result.append(f'"name": "{self.name}"')
        if self.data:
            result.append(f'"data": "{str(self.data)}"')
        if self.from_address:
            result.append(f'"from_address": "{str(self.from_address)}"')

        return f"{{{', '.join(result)}}}"

    @staticmethod
    def find_first_expected_event_not_included_in_state_events(
        expected_events: List["ExpectedEvent"], state_events: List[Event]
    ) -> Optional["ExpectedEvent"]:
        """Returns the expect event that has not been found."""
        assert len(expected_events) > 0

        for expected_event in expected_events:
            new_state_events = ExpectedEvent._get_next_state_events_if_event_found(
                expected_event, state_events
            )
            if new_state_events is None:
                return expected_event
            state_events = new_state_events
        return None

    @staticmethod
    def _get_next_state_events_if_event_found(
        expected_event: "ExpectedEvent", state_events: List[Event]
    ) -> Optional[List[Event]]:
        for (se_index, state_event) in enumerate(state_events):
            if expected_event.match(state_event):
                return state_events[se_index + 1 :]
        return None

    def match(self, state_event: Event) -> bool:
        return (
            get_selector_from_name(self.name) == state_event.keys[0]
            and (self.data is None or self.data == state_event.data)
            and (
                self.from_address is None
                or self.from_address == state_event.from_address
            )
        )


@dataclass
class TestSubject:
    """
    Deprecated. Use `TestSuite`.
    """

    test_path: Path
    test_functions: List[dict]
