from os import path
from git import InvalidGitRepositoryError, NoSuchPathError
from git.objects import Submodule
from git.repo import Repo
from . import installation_exceptions
from .utils import extract_slug_from_url, map_slug_to_package_name


def install(
    url: str,
    path_to_repo_root: str,
    destination="./lib",
):
    slug = extract_slug_from_url(url)

    try:
        repo = Repo(path_to_repo_root)
    except InvalidGitRepositoryError as _err:
        raise installation_exceptions.InvalidLocalRepository()
    except NoSuchPathError as _err:
        raise installation_exceptions.InvalidLocalRepository()

    package_name = map_slug_to_package_name(slug)

    Submodule.add(
        repo,
        package_name,
        path.join(destination, package_name),
        url,
    )
