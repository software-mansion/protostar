# pyright: reportGeneralTypeIssues=false

from enum import Enum
from typing import Optional
from typing_extensions import TypedDict
from git import Repo, Submodule, InvalidGitRepositoryError
from .utils import verify_repo_url


class InstallationErrorEnum(Enum):
    INCORRECT_URL = "INCORRECT_URL"
    INVALID_LOCAL_REPOSITORY = "INVALID_LOCAL_REPOSITORY"


InstallationResultType = TypedDict(
    "InstallResult", {"error": Optional[InstallationErrorEnum]}
)


def install(repo_root_location: str, url: str) -> InstallationResultType:
    if not verify_repo_url(url):
        return {"error": InstallationErrorEnum.INCORRECT_URL}

    try:
        repo = Repo(repo_root_location)
    except InvalidGitRepositoryError as _err:
        return {"error": InstallationErrorEnum.INVALID_LOCAL_REPOSITORY}

    Submodule.add(
        repo,
        "submodule_test",
        "./libs",
        url,
    )

    return {"error": None}
