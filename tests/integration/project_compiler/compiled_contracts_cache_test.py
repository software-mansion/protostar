import pytest

from tests.integration.conftest import CreateProtostarProjectFixture, ProtostarFixture
from protostar.compiler import CompiledContractsCache


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_create_cache_from_directory(protostar: ProtostarFixture):
    await protostar.build()
    compiled_contracts_cache = CompiledContractsCache.from_compiled_contracts_dir(
        protostar.project_root_path / "build"
    )

    assert compiled_contracts_cache.get("main") is not None
    assert compiled_contracts_cache.get("_") is None
