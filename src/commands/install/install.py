from enum import Enum
from os import path
from typing import Optional
from git import InvalidGitRepositoryError, NoSuchPathError
from git.repo import Repo
from git.objects import Submodule
from typing_extensions import TypedDict
from .utils import map_slug_to_package_name, extract_slug_from_url


class InstallationErrorEnum(Enum):
    INCORRECT_URL = "INCORRECT_URL"
    INVALID_LOCAL_REPOSITORY = "INVALID_LOCAL_REPOSITORY"
    INVALID_PACKAGE_NAME = "INVALID_PACKAGE_NAME"


InstallationResultType = TypedDict(
    "InstallationResult", {"error": Optional[InstallationErrorEnum]}
)


def install(
    url: str,
    path_to_repo_root: str,
    destination="./lib",
) -> InstallationResultType:
    slug = extract_slug_from_url(url)
    if slug is None:
        return {"error": InstallationErrorEnum.INCORRECT_URL}

    try:
        repo = Repo(path_to_repo_root)
    except InvalidGitRepositoryError as _err:
        return {"error": InstallationErrorEnum.INVALID_LOCAL_REPOSITORY}
    except NoSuchPathError as _err:
        return {"error": InstallationErrorEnum.INVALID_LOCAL_REPOSITORY}

    package_name = map_slug_to_package_name(slug)

    if package_name is None:
        return {"error": InstallationErrorEnum.INVALID_PACKAGE_NAME}

    Submodule.add(
        repo,
        package_name,
        path.join(destination, package_name),
        url,
    )

    return {"error": None}
