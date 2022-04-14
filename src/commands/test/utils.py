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


def extract_core_info_from_stark_ex_message(msg: Optional[str]) -> Optional[str]:
    if not msg:
        return None

    prefix = "Error message: "
    start_index = msg.rfind(prefix)

    if start_index == -1:
        return None

    end_index = msg.find("\n", start_index)

    return msg[start_index + len(prefix) : end_index]


class ExpectedEvent:
    RawEventType = TypedDict(
        "ExpectedEvent", {"name": str, "data": NotRequired[List[int]]}
    )
    CheatcodeInputType = Union[RawEventType, str]

    name: str
    data: Optional[List[int]]

    def __init__(
        self,
        raw_expected_event: CheatcodeInputType,
    ):
        self.data = None
        if isinstance(raw_expected_event, str):
            self.name = raw_expected_event
        else:
            self.name = raw_expected_event["name"]
            if "data" in raw_expected_event:
                self.data = raw_expected_event["data"]

    def __str__(self) -> str:
        return '{"name": ' + self.name + ', "data": ' + str(self.data) + "}"

    @classmethod
    def compare_events(
        cls, expected_events: List["ExpectedEvent"], state_events: List[Event]
    ) -> bool:
        matches_count = 0
        recent_match_index = 0
        for expected_event in expected_events:
            for (index, state_event) in enumerate(state_events[recent_match_index:]):
                if expected_event.match(state_event):
                    matches_count += 1
                    recent_match_index = index
                    continue
            if matches_count == len(expected_events):
                return True

        return False

    def match(self, state_event: Event) -> bool:
        return get_selector_from_name(self.name) == state_event.keys[0] and (
            self.data is None or self.data == state_event.data
        )


@dataclass
class TestSubject:
    """
    A dataclass consisting of identification of a single test bundle, and target functions
    """

    test_path: Path
    test_functions: List[dict]
