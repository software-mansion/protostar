from os import listdir

import pytest

from tests.integration.conftest import CreateProtostarProjectFixture, ProtostarFixture


@pytest.fixture(scope="module", name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_building_whole_project(protostar: ProtostarFixture):
    protostar.set_cached_configuration_file(
        contract_name_to_path_strs={
            "main": ["src/main.cairo"],
            "second_contract": ["src/main.cairo"],
        }
    )

    await protostar.build(["second_contract"])

    build_dir_content = listdir(protostar.project_root_path / "build")
    assert "main.json" not in build_dir_content
    assert "second_contract.json" in build_dir_content
