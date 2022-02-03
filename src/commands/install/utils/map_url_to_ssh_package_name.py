import re

from .. import installation_exceptions


def map_url_or_ssh_to_package_name(url_or_ssh: str) -> str:
    slug = ""

    if url_or_ssh.startswith("git@"):
        slug = _extract_slug_from_ssh(url_or_ssh)
    else:
        slug = _extract_slug_from_url(url_or_ssh)

    splitted_account_repo_name = slug.split("/")
    if len(splitted_account_repo_name) == 2:
        return splitted_account_repo_name[1].replace("-", "_").replace(".", "_")

    raise installation_exceptions.InvalidPackageName()


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
