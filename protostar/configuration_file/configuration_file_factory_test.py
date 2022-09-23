from pathlib import Path

from .configuration_file_factory import ConfigurationFileFactory


def test_not_finding_configuration_file():
    configuration_file_factory = ConfigurationFileFactory(cwd=Path())

    configuration_file = configuration_file_factory.create()

    assert configuration_file is None
