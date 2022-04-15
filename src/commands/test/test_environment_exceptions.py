from typing import Optional

from starkware.starkware_utils.error_handling import StarkException

from src.commands.test.utils import extract_core_info_from_stark_ex_message


class ReportedException(BaseException):
    def __str__(self) -> str:
        return str(super().__repr__())


class MissingExceptException(ReportedException):
    pass


class ExceptMismatchException(ReportedException):
    def __init__(
        self,
        expected_name: Optional[str],
        expected_message: Optional[str],
        received: StarkException,
    ):
        self.expected_name = expected_name
        self.expected_message = expected_message
        self.received = received
        super().__init__()

    def __str__(self) -> str:
        message = [
            "Expected:",
            f"name: {self.expected_name}, message: ",
            str(self.expected_message),
            "Instead got:",
            f"name: {self.received.code.name}, message: ",
            str(self.received.message),
        ]
        return "\n".join(message)


class StarkReportedException(ReportedException):
    def __init__(self, stark_exception: StarkException):
        self.stark_exception = stark_exception
        super().__init__()

    def __str__(self) -> str:
        message = [
            "[ERROR TYPE]",
            self.stark_exception.code.name,
            "",
            "[ERROR CODE]",
            str(self.stark_exception.code.value),
            "",
            "[ERROR MESSAGE]",
            extract_core_info_from_stark_ex_message(self.stark_exception.message) or "",
            "",
            "[ERROR DESCRIPTION]",
            self.stark_exception.message,
            "",
        ]
        return "\n".join(message)
