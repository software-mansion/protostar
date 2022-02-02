import re
from typing import Optional


def extract_slug_from_url(url: str) -> Optional[str]:
    result = re.search(r"(?<=https:\/\/github.com\/)[^\/]*\/[^\/]*", url)

    if result is None:
        return None

    return result.group()
