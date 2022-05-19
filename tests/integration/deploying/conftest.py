from distutils.file_util import copy_file
from pathlib import Path

import pytest


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(tmpdir) -> Path:
    return Path(tmpdir)


@pytest.fixture(name="output_dir")
def output_dir_fixture(project_root_path: Path) -> Path:
    (project_root_path / "build").mkdir(exist_ok=True)
    return Path("build")


@pytest.fixture(name="contract_name")
def contract_name_fixture() -> str:
    return "main"


@pytest.fixture(name="compiled_contract_filename")
def compiled_contract_filename_fixture(contract_name: str) -> str:
    return f"{contract_name}.json"


@pytest.fixture(name="compiled_contract_filepath")
def compiled_contract_filepath_fixture(
    project_root_path: Path,
    output_dir: Path,
    compiled_contract_filename: str,
    shared_datadir: Path,
) -> Path:
    filepath = project_root_path / output_dir / compiled_contract_filename
    copy_file(
        str(shared_datadir / compiled_contract_filename),
        str(project_root_path / output_dir / compiled_contract_filename),
    )
    return filepath


@pytest.fixture(name="compiled_contract_file_handle")
def compiled_contract_file_handle_fixture(compiled_contract_filepath):
    # pylint: disable=consider-using-with
    file_handle = open(compiled_contract_filepath, "r", encoding="utf_8")
    yield file_handle
    file_handle.close()
