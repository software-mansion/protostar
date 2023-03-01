from protostar.protostar_exception import ProtostarException


class RemovalException(ProtostarException):
    pass


class InvalidLocalRepository(RemovalException):
    pass


class PackageNotFound(RemovalException):
    pass
