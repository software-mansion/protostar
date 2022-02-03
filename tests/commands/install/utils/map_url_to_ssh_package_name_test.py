import pytest
from src.commands.install import installation_exceptions
from src.commands.install.utils import map_url_or_ssh_to_package_name


def test_github():
    result = map_url_or_ssh_to_package_name(
        "https://github.com/software-mansion/protostar"
    )

    assert result == "protostar"


def test_dashes():
    result = map_url_or_ssh_to_package_name(
        "https://github.com/software-mansion/protostar-test"
    )

    assert result == "protostar_test"


def test_bitbucket():
    result = map_url_or_ssh_to_package_name(
        "https://bitbucket.org/atlassian/python-bitbucket/src/master"
    )

    assert result == "python_bitbucket"


def test_ssh_and_dot():
    result = map_url_or_ssh_to_package_name(
        "git@github.com:software-mansion/starknet.py.git"
    )

    assert result == "starknet_py"


def test_slash_at_the_end():
    result = map_url_or_ssh_to_package_name(
        "https://github.com/software-mansion/protostar/"
    )

    assert result == "protostar"


def test_incorrect_url():
    with pytest.raises(installation_exceptions.IncorrectURL):
        map_url_or_ssh_to_package_name("https://github.com/software-mansion")
