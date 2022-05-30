import re
from typing import List, Optional, Union
from starkware.starknet.business_logic.execution.objects import Event

from protostar.utils.log_color_provider import log_color_provider
from protostar.commands.test.expected_event import ExpectedEvent


class ReportedException(BaseException):
    """
    The exception used for catching unexpected errors thrown from test cases and as a base class.
    """

    def __str__(self) -> str:
        return str(super().__repr__())


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
    def __init__(
        self, matches: ExpectedEvent.MatchesList, missing: List[ExpectedEvent]
    ) -> None:
        self.matches = matches
        self.missing = missing
        super().__init__()

    def __str__(self) -> str:
        result: List[str] = ["Matches: "]
        for match in self.matches:
            if match[0] == ExpectedEvent.MatchResult.MATCH:
                (_, expected_ev, state_ev) = match
                result.append(
                    log_color_provider.colorize(
                        "GREEN", self.state_event_to_string(state_ev)
                    )
                )
                result.append(
                    log_color_provider.colorize("GREEN", f"Match: {str(expected_ev)}")
                )

            elif match[0] == ExpectedEvent.MatchResult.SKIPPED:
                (_, state_ev) = match
                result.append(
                    log_color_provider.colorize(
                        "GRAY", self.state_event_to_string(state_ev)
                    )
                )
            result.append("")

        result.append("Missing: ")
        for missed_event in self.missing:
            result.append(log_color_provider.colorize("RED", str(missed_event)))
        return "\n".join(result)

    @staticmethod
    def state_event_to_string(state_event: Event):
        result: List[str] = []
        result.append(f'"name": "{state_event.keys[0]}"')
        result.append(f'"data": "{str(state_event.data)}"')
        result.append(f'"from_address": "{state_event.from_address}"')
        return f"{{{', '.join(result)}}}"

    def __reduce__(self):
        return type(self), (self.matches, self.missing)
