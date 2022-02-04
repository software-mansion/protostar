import re
from typing import NamedTuple, Optional

from .. import installation_exceptions


class ExtractInfoFromRepoIdResult(NamedTuple):
    package_name: str
    tag: Optional[str]
    url: Optional[str]


def extract_info_from_repo_id(repo_id: str) -> ExtractInfoFromRepoIdResult:
    result: Optional[ExtractInfoFromRepoIdResult] = None

    if repo_id.startswith("git@"):
        slug = _extract_slug_from_ssh(repo_id)
        splitted_account_repo_name = slug.split("/")
        if len(splitted_account_repo_name) == 2:
            result = ExtractInfoFromRepoIdResult(
                package_name=splitted_account_repo_name[1],
                tag=None,
                url=_map_ssh_to_url(repo_id),
            )
    elif ".org" in repo_id or ".com" in repo_id:
        slug = _extract_slug_from_url(repo_id)
        splitted_account_repo_name = slug.split("/")
        if len(splitted_account_repo_name) == 2:
            result = ExtractInfoFromRepoIdResult(
                package_name=splitted_account_repo_name[1], tag=None, url=repo_id
            )
    else:
        splitted_account_repo_name = repo_id.split("/")

        if len(splitted_account_repo_name) == 2:
            repo_name_with_tag = splitted_account_repo_name[1]
            splitted_repo_name_tag = repo_name_with_tag.split("@")
            tag: Optional[str] = None
            if len(splitted_repo_name_tag) == 2:
                tag = splitted_repo_name_tag[1]

            result = ExtractInfoFromRepoIdResult(
                package_name=splitted_repo_name_tag[0],
                tag=tag,
                url=_map_name_to_url(
                    splitted_account_repo_name[0] + "/" + splitted_repo_name_tag[0]
                ),
            )

    if result is None:
        raise installation_exceptions.InvalidPackageName()

    (package_name, tag, url) = result
    return ExtractInfoFromRepoIdResult(
        package_name=package_name.replace("-", "_").replace(".", "_"), tag=tag, url=url
    )


def _map_name_to_url(name: str) -> Optional[str]:
    return f"https://github.com/{name}"


def _map_ssh_to_url(ssh: str) -> Optional[str]:
    slug = _extract_slug_from_ssh(ssh)
    domain_match = re.search(r"(?<=git@).*(?=:)", ssh)

    if domain_match is None:
        return None

    return f"https://{domain_match.group()}/{slug}"


# https://github.com/software-mansion/protostar
def _extract_slug_from_url(url: str) -> str:
    result = re.search(r"(?<=.org\/|.com\/)[^\/]*\/[^\/]*", url)

    if result is None:
        raise installation_exceptions.IncorrectURL()

    return result.group()


# git@github.com:software-mansion/starknet.py.git
def _extract_slug_from_ssh(ssh: str) -> str:
    result = re.search(r"(?<=:)[^\/]*\/[^\/]*(?=\.git)", ssh)

    if result is None:
        raise installation_exceptions.IncorrectURL()

    return result.group()
