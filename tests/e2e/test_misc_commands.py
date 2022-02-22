# pylint: disable=redefined-outer-name
from os import listdir

import pytest

from tests.conftest import init_project, protostar


def test_help():
    result = protostar(["--help"])

    assert "usage:" in result


def test_init(project_name: str):
    with pytest.raises(FileNotFoundError):
        listdir(f"./{project_name}")

    init_project(project_name)

    assert "package.toml" in listdir(f"./{project_name}")
