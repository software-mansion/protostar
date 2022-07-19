import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

from starkware.starknet.business_logic.execution.objects import Event
from typing_extensions import Literal

from protostar.commands.test.expected_event import ExpectedEvent
from protostar.utils.log_color_provider import SupportedColorName, log_color_provider


class ExceptionMetadata(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def display(self) -> str:
        ...


class ReportedException(BaseException):
    """
    The exception used for catching unexpected errors thrown from test cases and as a base class.
    """

    def __init__(self, *args: object) -> None:
        self.metadata: List[ExceptionMetadata] = []
        super().__init__(*args)

    def __str__(self) -> str:
        return str(super().__repr__())


class SimpleReportedException(ReportedException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return str(self.message)


class CheatcodeException(ReportedException):
    def __init__(self, cheatcode_name: str, message: str):
        self.cheatcode_name = cheatcode_name
        self.message = message
        super().__init__(message)

    def __str__(self):
        lines: List[str] = []
        lines.append(f"Incorrect usage of `{self.cheatcode_name}` cheatcode")
        lines.append(self.message)
        return "\n".join(lines)

    def __reduce__(self):
        return type(self), (self.cheatcode_name, self.message)


class RevertableException(ReportedException):
    """
    This exception is used by `except_revert` logic.
    """

    def __init__(
        self,
        error_message: Optional[Union[str, List[str]]] = None,
        error_type: Optional[str] = None,
    ) -> None:
        super().__init__(error_message)
        self.error_type = error_type
        self.error_messages = (
            [error_message] if isinstance(error_message, str) else error_message
        ) or []

    def __str__(self) -> str:
        result: List[str] = []
        if self.error_type is not None:
            result.append(f"[error_type] {self.error_type}")

        if len(self.error_messages) > 0:
            result.append("[error_messages]:")
            for e_msg in self.error_messages:
                result.append(f"— {e_msg}")

        return "\n".join(result)

    def match(self, other: "RevertableException") -> bool:
        error_type_match = (
            self.error_type is None or self.error_type == other.error_type
        )

        if not error_type_match:
            return False

        if error_type_match and len(self.error_messages) == 0:
            return True

        for self_e_msg in self.error_messages:
            if not RevertableException.can_pattern_be_found(
                self_e_msg, other.error_messages
            ):
                return False
        return True

    @staticmethod
    def can_pattern_be_found(pattern: str, strings: List[str]) -> bool:
        return any(pattern in string for string in strings)

    def __reduce__(self):
        return type(self), (self.error_messages, self.error_type)


class StarknetRevertableException(RevertableException):
    """
    The exception is an abstraction over errors raised by StarkNet.
    """

    @staticmethod
    def extract_error_messages_from_stark_ex_message(
        msg: Optional[str],
    ) -> List[str]:
        if msg is None:
            return []

        results = re.findall("Error message: (.*)", msg)
        results.reverse()
        return results

    def __init__(
        self,
        error_message: Optional[Union[str, List[str]]] = None,
        error_type: Optional[str] = None,
        code: Optional[int] = None,
        details: Optional[str] = None,
    ) -> None:
        super().__init__(error_message, error_type)
        self.code = code
        self.details = details

    def __str__(self) -> str:
        result: List[str] = []

        result.append(f"[type] {self.error_type}")

        if self.code:
            result.append(f"[code] {str(self.code)}")

        if len(self.error_messages) > 0:
            result.append("[messages]:")
            for e_msg in self.error_messages:
                result.append(f"— {e_msg}")

        if self.details:
            result.append("[details]:")
            result.append(log_color_provider.colorize("GRAY", self.details))

        return "\n".join(result)

    def __reduce__(self):
        return type(self), (
            self.error_messages,
            self.error_type,
            self.code,
            self.details,
        )


class ExpectedRevertException(ReportedException):
    def __init__(self, expected_error: RevertableException) -> None:
        self._expected_error = expected_error
        super().__init__()

    def __str__(self) -> str:
        result: List[str] = ["Expected an exception matching the following error:"]
        result.append(str(self._expected_error))

        return "\n".join(result)

    def __reduce__(self):
        return type(self), (self._expected_error,)


class ExpectedRevertMismatchException(ReportedException):
    def __init__(
        self,
        expected: RevertableException,
        received: RevertableException,
    ):
        self._expected = expected
        self._received = received
        super().__init__()

    def __str__(self) -> str:
        result: List[str] = []

        if self._expected:
            result.append("EXPECTED:")
            result.append(
                str(self._expected),
            )
        else:
            result.append("Expected any error")

        if self._received:
            result.append("INSTEAD GOT:")
            result.append(
                str(self._received),
            )
        else:
            result.append("instead got nothing")

        return "\n".join(result)

    def __reduce__(self):
        return type(self), (self._expected, self._received)


class ExpectedEventMissingException(ReportedException):
    ResultType = Literal["skip", "pass", "miss"]

    def __init__(
        self,
        matches: ExpectedEvent.MatchesList,
        missing: List[ExpectedEvent],
        event_selector_to_name_map: Dict[int, str],
        line_prefix="  ",
    ) -> None:
        self.matches = matches
        self.missing = missing
        self._event_selector_to_name_map = event_selector_to_name_map
        self.line_prefix = line_prefix
        super().__init__()

    def map_match_result_to_lines(
        self,
        result: ResultType,
        expected_ev: Optional[ExpectedEvent],
        state_ev: Optional[Event],
    ) -> List[str]:
        lines: List[str] = []

        result_to_color: Dict[
            ExpectedEventMissingException.ResultType, SupportedColorName
        ] = {
            "skip": "GRAY",
            "pass": "GREEN",
            "miss": "RED",
        }

        colored_state_ev = (
            log_color_provider.colorize(
                "GRAY",
                self._state_event_to_string(state_ev),
            )
            if state_ev
            else None
        )

        result_message = (
            f"[{log_color_provider.colorize(result_to_color[result], result)}]"
        )
        lines.append(
            self.line_prefix
            + result_message
            + f" {str(expected_ev) if expected_ev else colored_state_ev}"
        )
        if expected_ev and state_ev:
            lines.append(
                log_color_provider.colorize(
                    "GRAY",
                    self.line_prefix
                    + "       "
                    + self._state_event_to_string(state_ev),
                )
            )
        return lines

    def __str__(self) -> str:
        result: List[str] = []
        for match in self.matches:
            if match[0] == ExpectedEvent.MatchResult.MATCH:
                (_, expected_ev, state_ev) = match
                result = result + self.map_match_result_to_lines(
                    "pass", expected_ev, state_ev
                )

            elif match[0] == ExpectedEvent.MatchResult.SKIPPED:
                (_, state_ev) = match
                result = result + self.map_match_result_to_lines("skip", None, state_ev)

        for missed_event in self.missing:
            result = result + self.map_match_result_to_lines("miss", missed_event, None)
        return "\n".join(result)

    def _state_event_to_string(self, state_event: Event):
        result: List[str] = []

        selector = state_event.keys[0]
        if selector in self._event_selector_to_name_map:
            result.append(f'"name": "{self._event_selector_to_name_map[selector]}"')
        else:
            result.append(f'"selector (hashed name)": "{selector}"')

        result.append(f'"data": {str(state_event.data)}')
        result.append(f'"from_address": {state_event.from_address}')
        return f"{{{', '.join(result)}}}"

    def __reduce__(self):
        return type(self), (
            self.matches,
            self.missing,
            self._event_selector_to_name_map,
        )
