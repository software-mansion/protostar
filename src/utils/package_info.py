import re
from dataclasses import dataclass, replace
from os import listdir
from typing import Dict, Optional

from git.repo import Repo

from src.protostar_exception import ProtostarException


@dataclass
class PackageInfo:
    name: str
    version: Optional[str]
    url: str


class PackageNameRetrievalException(ProtostarException):
    pass


class IncorrectURL(ProtostarException):
    pass


class InvalidPackageName(ProtostarException):
    pass


def retrieve_real_package_name(
    package_id: str, root_repo_dir: str, packages_dir: str
) -> str:
    normalized_package_name = ""
    if "/" in package_id:
        normalized_package_name = extract_info_from_repo_id(package_id).name
    else:
        normalized_package_name = normalize_package_name(package_id)

    mapping = load_normalized_to_real_name_map(root_repo_dir, packages_dir)

    if normalized_package_name in mapping:
        return mapping[normalized_package_name]

    # custom name
    package_names = listdir(packages_dir)
    if normalized_package_name in package_names:
        return normalized_package_name

    raise PackageNameRetrievalException(
        f'Protostar couldn\'t find package "{package_id}".'
    )


def load_normalized_to_real_name_map(repo_root_dir: str, packages_dir: str):
    repo = Repo.init(repo_root_dir)

    mapping: Dict["str", "str"] = {}

    package_names = listdir(packages_dir)
    for submodule in repo.submodules:
        if submodule.name in package_names:
            normalized_package_name = extract_info_from_repo_id(submodule.url).name
            mapping[normalized_package_name] = submodule.name

    return mapping


def normalize_package_name(package_name: str) -> str:
    return package_name.replace("-", "_").replace(".", "_")


def extract_info_from_repo_id(repo_id: str) -> PackageInfo:
    """
    A function which installs a package as git submodule.
    :param repo_id: Repo identifier which can be accepted in the following three forms:
        - name — e.g. `software-mansion/starknet.py@0.1.0-alpha`
        - url — e.g. `https://github.com/software-mansion/protostar`
        - ssh — e.g. `git@github.com:software-mansion/protostar.git`
    """
    result: Optional[PackageInfo] = None

    if repo_id.startswith("git@"):
        slug = _extract_slug_from_ssh(repo_id)
        splitted_account_repo_name = slug.split("/")
        if len(splitted_account_repo_name) == 2:
            result = PackageInfo(
                name=splitted_account_repo_name[1],
                version=None,
                url=_map_ssh_to_url(repo_id),
            )
    elif ".org" in repo_id or ".com" in repo_id:
        slug = _extract_slug_from_url(repo_id)
        splitted_account_repo_name = slug.split("/")
        if len(splitted_account_repo_name) == 2:
            result = PackageInfo(
                name=splitted_account_repo_name[1], version=None, url=repo_id
            )
    else:
        splitted_account_repo_name = repo_id.split("/")

        if len(splitted_account_repo_name) == 2:
            repo_name_with_tag = splitted_account_repo_name[1]
            splitted_repo_name_tag = repo_name_with_tag.split("@")
            tag: Optional[str] = None
            if len(splitted_repo_name_tag) == 2:
                tag = splitted_repo_name_tag[1]

            result = PackageInfo(
                name=splitted_repo_name_tag[0],
                version=tag,
                url=_map_name_to_url(
                    splitted_account_repo_name[0] + "/" + splitted_repo_name_tag[0]
                ),
            )

    if result is None:
        raise InvalidPackageName(
            f"""Protostar couldn\'t extract necessary information about the package from "{repo_id}".
Try providing package reference in one of the following formats:
- software-mansion/protostar (GitHub only)
- https://github.com/software-mansion/protostar
- git@github.com:software-mansion/protostar.git
"""
        )

    return replace(result, name=normalize_package_name(result.name))


def _map_name_to_url(name: str) -> str:
    return f"https://github.com/{name}"


def _map_ssh_to_url(ssh: str) -> str:
    slug = _extract_slug_from_ssh(ssh)
    domain_match = re.search(r"(?<=git@).*(?=:)", ssh)

    if domain_match is None:
        raise InvalidPackageName(
            f"""Protostar couldn't map SSH URI to URL.
Are you sure the following URI is correct?
{ssh}"""
        )

    return f"https://{domain_match.group()}/{slug}"


# https://github.com/software-mansion/protostar
def _extract_slug_from_url(url: str) -> str:
    result = re.search(r"(?<=.org\/|.com\/)[^\/]*\/[^\/]*", url)

    if result is None:
        raise IncorrectURL(
            f"""Protostar couldn't extract slug from the url.
Are you sure your the following url is correct?
{url}"""
        )

    return result.group()


# git@github.com:software-mansion/starknet.py.git
def _extract_slug_from_ssh(ssh: str) -> str:
    result = re.search(r"(?<=:)[^\/]*\/[^\/]*(?=\.git)", ssh)

    if result is None:
        raise IncorrectURL(
            f"""Protostar couldn't extract slug from the SSH URI.
Are you sure your the following SSH URI is correct?
{ssh}"""
        )

    return result.group()
