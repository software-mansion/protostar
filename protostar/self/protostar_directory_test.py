from pathlib import Path

import pytest

from protostar.self.protostar_directory import ProtostarDirectory


@pytest.fixture(name="script_root")
def script_root_fixture(tmpdir: str) -> Path:
    return Path(tmpdir)


def test_protostar_binary_dir_path(script_root: Path):
    protostar_directory = ProtostarDirectory(script_root)

    assert protostar_directory.protostar_binary_dir_path == script_root


def test_directory_root_path(script_root: Path):
    protostar_directory = ProtostarDirectory(script_root)

    assert protostar_directory.directory_root_path == script_root.parent.parent
