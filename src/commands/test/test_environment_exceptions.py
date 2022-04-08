from starkware.starkware_utils.error_handling import StarkException


class ReportedException(BaseException):
    def __str__(self) -> str:
        return str(super().__repr__())


class MissingExceptException(ReportedException):
    pass

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
