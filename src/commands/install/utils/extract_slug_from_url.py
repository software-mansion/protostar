import re
from .. import installation_exceptions


def extract_slug_from_url(url: str) -> str:
    result = re.search(r"(?<=.org\/|.com\/)[^\/]*\/[^\/]*", url)

    if result is None:
        raise installation_exceptions.IncorrectURL()

    return result.group()
