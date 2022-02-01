from enum import Enum
from typing import Optional
from typing_extensions import TypedDict
from .utils import verify_repo_url


class InstallErrorEnum(Enum):
    INCORRECT_URL = "INCORRECT_URL"


InstallResultType = TypedDict(
    "InstallResult", {"ok": bool, "error": Optional[InstallErrorEnum]}
)


def install(url: str) -> InstallResultType:
    if not verify_repo_url(url):
        return {"ok": False, "error": InstallErrorEnum.INCORRECT_URL}
    return {"ok": True, "error": None}
