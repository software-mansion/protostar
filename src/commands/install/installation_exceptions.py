class InstallationException(Exception):
    pass


class IncorrectURL(InstallationException):
    pass


class InvalidLocalRepository(InstallationException):
    pass


class InvalidPackageName(InstallationException):
    pass
