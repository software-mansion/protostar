import pytest

from src.commands.install import installation_exceptions
from src.commands.install.extract_info_from_repo_id import (
    _map_ssh_to_url,
    extract_info_from_repo_id,
)


def test_github():
    package_info = extract_info_from_repo_id(
        "https://github.com/software-mansion/protostar"
    )

    assert package_info.name == "protostar"
    assert package_info.version is None
    assert package_info.url == "https://github.com/software-mansion/protostar"


def test_dashes():
    package_info = extract_info_from_repo_id(
        "https://github.com/software-mansion/protostar-test"
    )

    assert package_info.name == "protostar_test"
    assert package_info.version is None
    assert package_info.url == "https://github.com/software-mansion/protostar-test"


def test_bitbucket():
    package_info = extract_info_from_repo_id(
        "https://bitbucket.org/atlassian/python-bitbucket"
    )

    assert package_info.name == "python_bitbucket"
    assert package_info.version is None
    assert package_info.url == "https://bitbucket.org/atlassian/python-bitbucket"


def test_ssh_and_dot():
    package_info = extract_info_from_repo_id(
        "git@github.com:software-mansion/starknet.py.git"
    )

    assert package_info.name == "starknet_py"
    assert package_info.version is None
    assert package_info.url == "https://github.com/software-mansion/starknet.py"


def test_account_repo_name():
    package_info = extract_info_from_repo_id("software-mansion/protostar")

    assert package_info.name == "protostar"
    assert package_info.version is None
    assert package_info.url == "https://github.com/software-mansion/protostar"


def test_tags():
    package_info = extract_info_from_repo_id("software-mansion/protostar@0.0.0-alpha")

    assert package_info.name == "protostar"
    assert package_info.version == "0.0.0-alpha"
    assert package_info.url == "https://github.com/software-mansion/protostar"


def test_slash_at_the_end():
    package_info = extract_info_from_repo_id(
        "https://github.com/software-mansion/protostar/"
    )

    assert package_info.name == "protostar"
    assert package_info.version is None
    assert package_info.url == "https://github.com/software-mansion/protostar/"


def test_incorrect_url():
    with pytest.raises(installation_exceptions.IncorrectURL):
        extract_info_from_repo_id("https://github.com/software-mansion")


def test_failure_at_extracting_slug_from_ssh():
    with pytest.raises(installation_exceptions.IncorrectURL):
        extract_info_from_repo_id("git@github.com:software-mansion/starknet.py")


def test_failure_at_unknown_repo_id_format():
    with pytest.raises(installation_exceptions.InvalidPackageName):
        extract_info_from_repo_id("http://github.pl/foobar.git")


def test_failure_at_mapping_ssh_to_url():
    with pytest.raises(installation_exceptions.InvalidPackageName):
        _map_ssh_to_url("abc@github.com:software-mansion/starknet.py.git")
