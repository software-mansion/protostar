class RemovalException(Exception):
    pass


class InvalidLocalRepository(RemovalException):
    pass


class PackageNotFound(Exception):
    pass
