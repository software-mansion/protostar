import pytest

from protostar.protostar_exception import ProtostarException
from protostar.protostar_toml.protostar_toml_version_checker import (
    ProtostarTOMLVersionChecker,
)
from protostar.utils import VersionManager


@pytest.mark.parametrize(
    "last_supported_protostar_toml_version, protostar_toml_version",
    (
        ("1.0", "0.9"),
        ("2.1", "0.3.2"),
        ("1.0.0", "0.9.9"),
    ),
)
def test_failing_checks(
    mocker, last_supported_protostar_toml_version, protostar_toml_version
):
    protostar_toml_reader = mocker.MagicMock()
    protostar_toml_reader.get_attribute.return_value = protostar_toml_version

    version_manager = mocker.MagicMock()
    type(version_manager).last_supported_protostar_toml_version = mocker.PropertyMock(
        return_value=VersionManager.parse(last_supported_protostar_toml_version)
    )

    with pytest.raises(ProtostarException) as exception:
        ProtostarTOMLVersionChecker(protostar_toml_reader, version_manager).run()
    assert "is not compatible with provided protostar.toml" in exception.value.message


@pytest.mark.parametrize(
    "last_supported_protostar_toml_version, protostar_toml_version",
    (
        ("1.0", "1.1"),
        ("2.1", "2.2"),
        ("1.0.0", "1.0.1"),
        ("1.0", "1.0"),
        ("2.0.1", "2.0.1"),
    ),
)
def test_successful_checks(
    mocker, last_supported_protostar_toml_version, protostar_toml_version
):
    protostar_toml_reader = mocker.MagicMock()
    protostar_toml_reader.get_attribute.return_value = protostar_toml_version

    version_manager = mocker.MagicMock()
    type(version_manager).last_supported_protostar_toml_version = mocker.PropertyMock(
        return_value=VersionManager.parse(last_supported_protostar_toml_version)
    )

    ProtostarTOMLVersionChecker(protostar_toml_reader, version_manager).run()
