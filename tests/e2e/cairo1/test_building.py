from pathlib import Path

import os

from tests.e2e.conftest import ProtostarFixture, CopyFixture


def test_cairo1_build(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_build", "./cairo1_build")
    os.chdir("./cairo1_build")
    protostar(["build-cairo1"])
    compiled_path = Path("build/main.json")
    assert compiled_path.exists()
    assert compiled_path.read_text()
