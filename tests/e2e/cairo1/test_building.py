from pathlib import Path

import pytest

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.usefixtures("init_cairo1")
def test_default_build(protostar: ProtostarFixture):
    protostar(["build-cairo1"])
    compiled_path = Path("build/main.json")
    assert compiled_path.exists()
    assert compiled_path.read_text()
