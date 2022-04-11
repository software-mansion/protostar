from typing import Union
from starkware.starkware_utils.error_handling import StarkException


class ReportedException(BaseException):
    def __str__(self) -> str:
        return str(super().__repr__())


class MissingExceptException(ReportedException):
    pass


class ExceptMismatchException(ReportedException):
    def __init__(
        self,
        expected_name: Union[str, None],
        expected_message: Union[str, None],
        received: StarkException,
    ):
        self.expected_name = expected_name
        self.expected_message = expected_message
        self.received = received
        super().__init__()

    def __str__(self) -> str:
        message = [
            "Expected:",
            f"name: {self.expected_name}, message: "
            self.expected_message,
            "Instead got:",
            f"name: {self.received.code.name}, message: ",
            self.received.message,
        ]
        return "\n".join(message)


class StarkReportedException(ReportedException):
    def __init__(self, stark_exception: StarkException):
        self.stark_exception = stark_exception
        super().__init__()

    def __str__(self) -> str:
        message = [
            f"Error type: {self.stark_exception.code.name}",
            "Error message:",
            f"  {self.stark_exception.message}",
            "Error code:",
            f"  {self.stark_exception.code.value}",
        ]
        return "\n".join(message)
