from protostar.protostar_exception import ProtostarException


class InvalidLocalRepository(ProtostarException):
    pass


class PackageNotFound(ProtostarException):
    pass
