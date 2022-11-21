from pathlib import Path

import pytest

from protostar.configuration_file import FakeConfigurationFile

from .contract_source_identifier import create_contract_source_identifier_factory


@pytest.fixture(name="fake_contract_path")
def fake_contract_path_fixture(tmp_path: Path) -> Path:
    contract_path = tmp_path / "main.cairo"
    contract_path.touch()
    return contract_path


def test_creating_contract_source_identifier_from_contract_name(
    fake_contract_path: Path,
):
    create_contract_source_identifier = create_contract_source_identifier_factory(
        configuration_file=FakeConfigurationFile(
            contract_name_to_source_paths={"main": [fake_contract_path]}
        )
    )

    contract_source_identifier = create_contract_source_identifier("main")

    assert contract_source_identifier.name == "main"
    assert fake_contract_path in contract_source_identifier.paths
    assert len(contract_source_identifier.paths) == 1
