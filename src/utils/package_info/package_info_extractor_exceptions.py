class PackageInfoExtractorException(Exception):
    pass


class IncorrectURL(PackageInfoExtractorException):
    pass


class InvalidPackageName(PackageInfoExtractorException):
    pass
