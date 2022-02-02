import pytest
from src.commands.install import installation_exceptions
from src.commands.install.utils import extract_slug_from_url


def test_base_case():
    result = extract_slug_from_url("https://github.com/software-mansion/protostar")

    assert result == "software-mansion/protostar"


def test_url_with_slash_at_the_end():
    result = extract_slug_from_url("https://github.com/software-mansion/protostar/")

    assert result == "software-mansion/protostar"


def test_partial_url():
    with pytest.raises(installation_exceptions.IncorrectURL):
        extract_slug_from_url("https://github.com/software-mansion")
