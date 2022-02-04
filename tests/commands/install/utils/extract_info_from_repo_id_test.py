import pytest
from src.commands.install import installation_exceptions
from src.commands.install.utils import extract_info_from_repo_id


def test_github():
    (package_name, tag, url) = extract_info_from_repo_id(
        "https://github.com/software-mansion/protostar"
    )

    assert package_name == "protostar"
    assert tag is None
    assert url == "https://github.com/software-mansion/protostar"


def test_dashes():
    (package_name, tag, url) = extract_info_from_repo_id(
        "https://github.com/software-mansion/protostar-test"
    )

    assert package_name == "protostar_test"
    assert tag is None
    assert url == "https://github.com/software-mansion/protostar-test"


def test_bitbucket():
    (package_name, tag, url) = extract_info_from_repo_id(
        "https://bitbucket.org/atlassian/python-bitbucket"
    )

    assert package_name == "python_bitbucket"
    assert tag is None
    assert url == "https://bitbucket.org/atlassian/python-bitbucket"


def test_ssh_and_dot():
    (package_name, tag, url) = extract_info_from_repo_id(
        "git@github.com:software-mansion/starknet.py.git"
    )

    assert package_name == "starknet_py"
    assert tag is None
    assert url == "https://github.com/software-mansion/starknet.py"


def test_account_repo_name():
    (package_name, tag, url) = extract_info_from_repo_id("software-mansion/protostar")

    assert package_name == "protostar"
    assert tag is None
    assert url == "https://github.com/software-mansion/protostar"


def test_tags():
    (package_name, tag, url) = extract_info_from_repo_id(
        "software-mansion/protostar@0.0.0-alpha"
    )

    assert package_name == "protostar"
    assert tag == "0.0.0-alpha"
    assert url == "https://github.com/software-mansion/protostar"


def test_slash_at_the_end():
    result = extract_info_from_repo_id("https://github.com/software-mansion/protostar/")

    assert result[0] == "protostar"


def test_incorrect_url():
    with pytest.raises(installation_exceptions.IncorrectURL):
        extract_info_from_repo_id("https://github.com/software-mansion")
