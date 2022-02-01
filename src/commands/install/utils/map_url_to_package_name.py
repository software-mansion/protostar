import re
from typing import Optional


def map_url_to_package_name(url: str) -> Optional[str]:
    result = re.search(r"(?<=https:\/\/github.com\/).*", url)

    if result is None:
        return None

    account_repo_name = result.group()
    splitted_account_repo_name = account_repo_name.split("/")
    if len(splitted_account_repo_name) == 2:
        return splitted_account_repo_name[1].replace("-", "_")

    return None
