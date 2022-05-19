# pylint: disable=consider-using-with
import subprocess
import time
from distutils.file_util import copy_file
from pathlib import Path
from socket import socket as Socket

import pytest


def get_available_port() -> int:
    with Socket() as socket:
        socket.bind(("", 0))
        return socket.getsockname()[1]


@pytest.fixture(name="devnet_gateway_url")
def devnet_gateway_url_fixture():
    devnet_port = get_available_port()

    command = [
        "poetry",
        "run",
        "starknet-devnet",
        "--host",
        "localhost",
        "--port",
        str(devnet_port),
    ]
    # pylint: disable=consider-using-with
    proc = subprocess.Popen(command)
    time.sleep(5)
    yield f"http://localhost:{devnet_port}"
    proc.kill()


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
    file_handle = open(compiled_contract_filepath, "r", encoding="utf_8")
    yield file_handle
    file_handle.close()
