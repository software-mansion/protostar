import os
import pytest
from tests.e2e.conftest import CopyFixture, ProtostarFixture



def test_complex(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    os.chdir("./cairo1_project")
    breakpoint()
    result = protostar(["--cairo1", "test", "tests"])

    assert "Collected 2 suites, and 4 test cases" in result
    assert "4 passed" in result