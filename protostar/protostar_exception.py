from typing import Optional

UNEXPECTED_PROTOSTAR_ERROR_MSG = (
    "Unexpected Protostar error. Report it here:\n"
    "https://github.com/software-mansion/protostar/issues\n"
)


class ProtostarException(Exception):
    """This exception is nicely printed by protostar and results in non-zero exit code"""

    # Disabling pylint to narrow down types
    # pylint: disable=useless-super-delegation
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class ProtostarExceptionSilent(ProtostarException):
    """This exception isn't printed but results in non-zero exit code"""
