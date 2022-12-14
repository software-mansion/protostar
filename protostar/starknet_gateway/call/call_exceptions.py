from protostar.protostar_exception import ProtostarException


class AbiNotFoundException(ProtostarException):
    def __init__(self, message: str):
        super().__init__(message=message)
