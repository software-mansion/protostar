from os import listdir

import pytest

from tests.integration.conftest import CreateProtostarProjectFixture, ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.set_cached_configuration_file(
            contract_name_to_path_strs={
                "A": ["src/main.cairo"],
                "B": ["src/main.cairo"],
            }
        )
        yield protostar


async def test_building_whole_project_when_no_contract_is_specified(
    protostar: ProtostarFixture,
):
    await protostar.build([])

    build_dir_content = listdir(protostar.project_root_path / "build")
    assert "A.json" in build_dir_content
    assert "B.json" in build_dir_content


async def test_building_specific_contract_from_name(protostar: ProtostarFixture):
    await protostar.build(["A"])

    build_dir_content = listdir(protostar.project_root_path / "build")
    assert "A.json" in build_dir_content
    assert "B.json" not in build_dir_content


async def test_building_many_specific_contracts_from_name(protostar: ProtostarFixture):
    await protostar.build(["A", "B"])

    build_dir_content = listdir(protostar.project_root_path / "build")
    assert "A.json" in build_dir_content
    assert "B.json" in build_dir_content


async def test_building_specific_contract_from_path(protostar: ProtostarFixture):
    await protostar.build(["src/main.cairo"])

    build_dir_content = listdir(protostar.project_root_path / "build")
    assert "main.json" in build_dir_content
