from src.protostar_exception import ProtostarException


class UpdatingException(ProtostarException):
    pass


class PackageAlreadyUpToDateException(UpdatingException):
    def __init__(self):
        super().__init__("Package already up to date.")
