from .. import installation_exceptions


def map_slug_to_package_name(slug: str) -> str:
    splitted_account_repo_name = slug.split("/")
    if len(splitted_account_repo_name) == 2:
        return splitted_account_repo_name[1].replace("-", "_")

    raise installation_exceptions.InvalidLocalRepository()
