import os
from collections import deque
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from starkware.starknet.business_logic.execution.objects import Event
from starkware.starknet.public.abi import get_selector_from_name
from typing_extensions import Literal, NotRequired, TypedDict

from protostar.commands.test.test_suite import TestSuite
from protostar.utils.data_transformer_facade import DataTransformerFacade


def collect_immediate_subdirectories(root_dir: Path) -> List[str]:
    assert root_dir.is_dir(), f"{root_dir} is supposed to be a directory!"
    (root, dirs, _) = next(os.walk(str(root_dir.resolve())))
    return [str(Path(root, directory).resolve()) for directory in dirs]


class ExpectedEvent:
    RawEventType = TypedDict(
        "ExpectedEvent",
        {
            "name": str,
            "data": NotRequired[
                Union[
                    List[int],
                    Dict[
                        DataTransformerFacade.ArgumentName,
                        DataTransformerFacade.SupportedType,
                    ],
                ]
            ],
            "from_address": NotRequired[int],
        },
    )
    RawEventTypeWithTransformedData = TypedDict(
        "ExpectedEvent",
        {"name": str, "data": NotRequired[List[int]], "from_address": NotRequired[int]},
    )
    CheatcodeInputType = Union[RawEventType, str]

    @classmethod
    def from_cheatcode_input_type(
        cls, raw_expected_event: CheatcodeInputType
    ) -> "ExpectedEvent":

        data = None
        from_address = None
        if isinstance(raw_expected_event, str):
            name = raw_expected_event
        else:
            name = raw_expected_event["name"]
            if "data" in raw_expected_event:
                data = raw_expected_event["data"]

            if "from_address" in raw_expected_event:
                from_address = raw_expected_event["from_address"]

        # if isinstance(data, Mapping):
        #     fn_name = "constructor"
        #     constructor_calldata = DataTransformerFacade.from_contract_path(
        #         Path(contract_path), self._starknet_compiler
        #     ).build_from_python_transformer(fn_name, "inputs")(constructor_calldata)

        return cls(name=name, data=data, from_address=from_address)

    def __init__(
        self,
        name: str,
        data: Optional[List[int]] = None,
        from_address: Optional[int] = None,
    ):
        self.name = name
        self.data = data
        self.from_address = from_address

    def __str__(self) -> str:
        result: List[str] = []
        result.append(f'"name": "{self.name}"')

        if self.data:
            result.append(f'"data": {str(self.data)}')
        if self.from_address:
            result.append(f'"from_address": {str(self.from_address)}')

        return f"{{{', '.join(result)}}}"

    class MatchResult(Enum):
        MATCH = 1
        SKIPPED = 2

    MatchesList = List[
        Union[
            Tuple[Literal[MatchResult.SKIPPED], Event],
            Tuple[Literal[MatchResult.MATCH], "ExpectedEvent", Event],
        ]
    ]

    @staticmethod
    def match_state_events_to_expected_to_events(
        expected_events: List["ExpectedEvent"], state_events: List[Event]
    ) -> Tuple[MatchesList, List["ExpectedEvent"]]:
        assert len(expected_events) > 0
        expected = deque(expected_events)
        results: ExpectedEvent.MatchesList = []
        for state_event in state_events:
            try:
                if expected[0].match(state_event):
                    results.append(
                        (ExpectedEvent.MatchResult.MATCH, expected[0], state_event)
                    )
                    expected.popleft()
                else:
                    results.append((ExpectedEvent.MatchResult.SKIPPED, state_event))
            except IndexError:
                results.append((ExpectedEvent.MatchResult.SKIPPED, state_event))

        return results, list(expected)

    def match(self, state_event: Event) -> bool:
        return (
            get_selector_from_name(self.name) == state_event.keys[0]
            and (self.data is None or self.data == state_event.data)
            and (
                self.from_address is None
                or self.from_address == state_event.from_address
            )
        )


TestSubject = TestSuite
