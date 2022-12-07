from subprocess import CalledProcessError
from typing import Optional, Callable, Any
from functools import wraps
from protostar.protostar_exception import ProtostarException


class ProtostarGitException(ProtostarException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__("Error while executing Git command:\n" + message, details)


class InvalidGitRepositoryException(ProtostarGitException):
    pass


class GitNotFoundException(ProtostarGitException):
    pass


def wrap_git_exception(func: Callable):
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except CalledProcessError as ex:
            raise ProtostarGitException(str(ex)) from ex

    return wrapper
