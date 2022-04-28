from typing import List, Optional, Union


class ReportedException(BaseException):
    """
    The exception used for catching unexpected errors thrown from test cases and as a base class.
    """

    def __str__(self) -> str:
        return str(super().__repr__())


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
        self.error_message = error_message

    def __str__(self) -> str:
        result: List[str] = []
        if self.error_type is not None:
            result.append(f"[error_type] {self.error_type}")

        if self.error_message is not None:
            if isinstance(self.error_message, list):
                result.append("[error_messages]:")
                for e_msg in self.error_message:
                    result.append(f"— {e_msg}")
            else:
                result.append(f"[error_message] {self.error_message}")
        return "\n".join(result)

    def match(self, other: "RevertableException") -> bool:
        error_type_match = (
            self.error_type is None or self.error_type == other.error_type
        )

        if error_type_match:
            if self.error_message is None:
                return True
        else:
            return False

        self_error_messages = (
            [self.error_message]
            if isinstance(self.error_message, str)
            else self.error_message
        )

        other_error_messages = (
            [other.error_message]
            if isinstance(other.error_message, str)
            else other.error_message
        ) or []

        for self_e_msg in self_error_messages:
            if self_e_msg not in other_error_messages:
                return False

        return True


class StarknetRevertableException(RevertableException):
    """
    The exception is an abstraction over errors raised by StarkNet.
    """

    @staticmethod
    def extract_error_messages_from_stark_ex_message(
        msg: Optional[str],
    ) -> List[str]:
        results: List[str] = []

        if msg is None:
            return []

        prefix = "Error message: "
        remaining_msg = msg
        start_index = remaining_msg.find(prefix)
        while not start_index == -1:
            end_index = remaining_msg.find("\n", start_index)
            results.append(remaining_msg[start_index + len(prefix) : end_index])
            remaining_msg = remaining_msg[end_index:]
            start_index = remaining_msg.find(prefix)

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

        if self.error_message:
            result.append(f"[message] {self.error_message}")

        if self.code:
            result.append(f"[code] {str(self.code)}")

        if self.details:
            result.append("[details]:\n")
            result.append(self.details)

        return "\n".join(result)


class ExpectedRevertException(ReportedException):
    def __init__(self, expected_error: RevertableException) -> None:
        self._expected_error = expected_error
        super().__init__()

    def __str__(self) -> str:
        result: List[str] = ["Expected an exception matching the following error:"]
        result.append(str(self._expected_error))

        return "\n".join(result)


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
