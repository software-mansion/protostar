from typing import Optional


def map_slug_to_package_name(slug: str) -> Optional[str]:
    splitted_account_repo_name = slug.split("/")
    if len(splitted_account_repo_name) == 2:
        return splitted_account_repo_name[1].replace("-", "_")

    return None
