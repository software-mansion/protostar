import re


def verify_repo_url(url: str) -> bool:
    return bool(re.match(r"^https:\/\/github.com\/[^\/]*\/[^\/]*$", url))
