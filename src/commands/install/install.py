from os import path

from git import InvalidGitRepositoryError, NoSuchPathError
from git.objects import Submodule
from git.repo import Repo

from . import installation_exceptions
from .utils import map_url_or_ssh_to_package_name


def install(
    url_or_ssh: str,
    path_to_repo_root: str,
    destination="./lib",
):
    try:
        repo = Repo(path_to_repo_root)
    except InvalidGitRepositoryError as _err:
        raise installation_exceptions.InvalidLocalRepository()
    except NoSuchPathError as _err:
        raise installation_exceptions.InvalidLocalRepository()

    package_name = map_url_or_ssh_to_package_name(url_or_ssh)

    Submodule.add(
        repo,
        package_name,
        path.join(destination, package_name),
        url_or_ssh,
    )
