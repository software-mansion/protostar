from pathlib import Path

import pytest
from protostar.cairo import CairoVersion
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project(CairoVersion.cairo1) as protostar_project:
        yield protostar_project.protostar


def test_cairo1_build(protostar: ProtostarFixture):
    protostar.build_sync()

    expected_paths = [
        Path("build/hello_starknet.sierra.json"),
        Path("build/hello_starknet.casm.json"),
        Path("build/hello_starknet.class.hash"),
        Path("build/hello_starknet.compiled.class.hash"),
    ]
    for path in expected_paths:
        assert path.exists()
        assert path.read_text()
