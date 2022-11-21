from pathlib import Path

from protostar.configuration_file import FakeConfigurationFile

from .contract_source_identifier import ContractSourceIdentifier


def test_creating_contract_source_identifier_from_contract_name():
    main_contract_source_path = Path("src/main.cairo")
    create_contract_source = create_contract_source_identifier_factory(
        configuration_file=FakeConfigurationFile(
            contract_name_to_source_paths={"main": [main_contract_source_path]}
        )
    )

    contract_source_identifier = create_contract_source_identifier("main")

    assert contract_source_identifier.name == "main"
    assert main_contract_source_path in contract_source_identifier.paths
    assert len(contract_source_identifier.paths) == 1
