# pylint: disable=redefined-outer-name
import json
import shlex
import shutil
from os import chdir, mkdir, path, getcwd
from pathlib import Path
from subprocess import PIPE, STDOUT, run
from typing import Callable, List, Optional, Union

import pexpect
import pytest
import tomli
import tomli_w
from typing_extensions import Protocol

from protostar.io import ProtostarDirectory
from tests.conftest import run_devnet


@pytest.fixture(scope="session")
def protostar_repo_root() -> Path:
    file_path = Path(__file__)
    assert file_path.match(
        "tests/e2e/conftest.py"
    ), f"{file_path.name} was moved without adjusting path logic"
    return file_path.parent.parent.parent


@pytest.fixture
def protostar_bin(protostar_repo_root: Path) -> Path:
    return protostar_repo_root / "dist" / "protostar" / "protostar"


@pytest.fixture(autouse=True)
def change_cwd(tmpdir, protostar_repo_root: Path):
    protostar_project_dir = Path(tmpdir) / "protostar_project"
    mkdir(protostar_project_dir)
    yield chdir(protostar_project_dir)
    chdir(protostar_repo_root)


@pytest.fixture
def cairo_fixtures_dir(protostar_repo_root: Path):
    return protostar_repo_root / "tests" / "e2e" / "fixtures"


@pytest.fixture
def copy_fixture(
    cairo_fixtures_dir,
) -> Callable[[Union[Path, str], Union[Path, str]], None]:
    return lambda file, dst: shutil.copy(cairo_fixtures_dir / file, dst)


@pytest.fixture
def project_name() -> str:
    return "foobar"


@pytest.fixture
def libs_path() -> str:
    return ""


@pytest.fixture
def protostar_toml_protostar_version() -> Optional[str]:
    return None


class ProjectInitializer(Protocol):
    def __call__(
        self,
        override_project_name: Optional[str] = None,
        override_libs_path: Optional[str] = None,
    ) -> None:
        ...


@pytest.fixture
def init_project(
    protostar_bin: Path, project_name: str, libs_path: str
) -> ProjectInitializer:
    def _init_project(
        override_project_name: Optional[str] = None,
        override_libs_path: Optional[str] = None,
    ) -> None:
        if override_project_name is None:
            real_project_name = project_name
        else:
            real_project_name = override_project_name

        if override_libs_path is None:
            real_libs_path = libs_path
        else:
            real_libs_path = override_libs_path

        child = pexpect.spawn(f"{protostar_bin} init")
        child.expect(
            "project directory name:", timeout=30
        )  # the very first run is a bit slow
        child.sendline(real_project_name)
        child.expect("libraries directory *", timeout=1)
        child.sendline(real_libs_path)
        child.expect(pexpect.EOF)

    return _init_project


class ProtostarFixture(Protocol):
    def __call__(
        self,
        args: List[str],
        expect_exit_code: int = 0,
        ignore_exit_code: bool = False,
    ) -> str:
        ...


@pytest.fixture
def protostar_version() -> Optional[str]:
    return None


@pytest.fixture
def latest_supported_protostar_toml_version() -> Optional[str]:
    return None


@pytest.fixture(name="info_dir_path")
def info_dir_path_fixture(tmp_path: Path) -> Path:
    return tmp_path / "dist" / "protostar" / "info"


@pytest.fixture
def protostar(
    protostar_repo_root: Path,
    tmp_path: Path,
    protostar_version: Optional[str],
    info_dir_path: Path,
) -> ProtostarFixture:
    shutil.copytree(protostar_repo_root / "dist", tmp_path / "dist")

    runtime_constants_file_path = (
        info_dir_path / ProtostarDirectory.RUNTIME_CONSTANTS_FILE_NAME
    )
    if protostar_version:
        with open(
            runtime_constants_file_path, mode="r+", encoding="utf-8"
        ) as runtime_constants_file:
            constants_dict = json.load(runtime_constants_file)
            constants_dict["PROTOSTAR_VERSION"] = protostar_version

            runtime_constants_file.seek(0)
            runtime_constants_file.truncate()
            runtime_constants_file.write(json.dumps(constants_dict))

    def _protostar(
        args: List[str],
        expect_exit_code: int = 0,
        ignore_exit_code: bool = False,
    ) -> str:
        completed = run(
            [path.join(tmp_path, "dist", "protostar", "protostar")] + args,
            stdout=PIPE,
            stderr=STDOUT,
            encoding="utf-8",
        )

        if not ignore_exit_code:
            if completed.returncode != expect_exit_code:
                # TODO(mkaput): Report this in nicer Pytest assertion-understandable way.
                raise AssertionError(
                    f"""\
Proces exited with {completed.returncode} while expected {expect_exit_code}.",
Args: {shlex.join(completed.args)}
Output:
{completed.stdout}
"""
                )

        return completed.stdout

    return _protostar


@pytest.fixture(name="devnet_gateway_url", scope="session")
def devnet_gateway_url_fixture(devnet_port: int, protostar_repo_root):
    prev_cwd = getcwd()
    chdir(protostar_repo_root)
    proc = run_devnet(["poetry", "run", "starknet-devnet"], devnet_port)
    chdir(prev_cwd)
    yield f"http://localhost:{devnet_port}"
    proc.kill()


@pytest.fixture
def init(
    protostar_repo_root: Path,
    project_name: str,
    protostar_toml_protostar_version: str,
    init_project: ProjectInitializer,
):
    init_project()
    chdir(project_name)
    if protostar_toml_protostar_version:
        with open(Path() / "protostar.toml", "r+", encoding="UTF-8") as file:
            raw_protostar_toml = file.read()
            protostar_toml = tomli.loads(raw_protostar_toml)

            assert (
                protostar_toml["protostar.config"]["protostar_version"] is not None
            )  # Sanity check

            protostar_toml["protostar.config"][
                "protostar_version"
            ] = protostar_toml_protostar_version
            file.seek(0)
            file.truncate()
            file.write(tomli_w.dumps(protostar_toml))
    yield
    chdir(protostar_repo_root)


# pylint: disable=unused-argument
@pytest.fixture(name="my_private_libs_setup")
def my_private_libs_setup_fixture(init, tmpdir, copy_fixture):
    my_private_libs_dir = Path(tmpdir) / "my_private_libs"
    mkdir(my_private_libs_dir)

    my_lib_dir = my_private_libs_dir / "my_lib"
    mkdir(my_lib_dir)

    copy_fixture("simple_function.cairo", my_lib_dir / "utils.cairo")
    copy_fixture("main_using_simple_function.cairo", Path() / "src" / "main.cairo")
    copy_fixture(
        "test_main_using_simple_function.cairo", Path() / "tests" / "test_main.cairo"
    )
    return (my_private_libs_dir,)
