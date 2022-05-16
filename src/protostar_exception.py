class ProtostarException(Exception):
    "This exception is nicely printed by protostar and results in non-zero exit code"
    # Disabling pylint to narrow down types
    # pylint: disable=useless-super-delegation
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProtostarExceptionSilent(ProtostarException):
    "This exception isn't printed but results in non-zero exit code"
    ...
