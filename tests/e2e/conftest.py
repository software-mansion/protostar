# pylint: disable=redefined-outer-name
import shutil
from os import chdir, mkdir, path
from pathlib import Path
from subprocess import PIPE, STDOUT, run
from typing import Callable, List, Optional

import pexpect
import pytest
import tomli
import tomli_w
from typing_extensions import Protocol

from tests.conftest import run_devnet


@pytest.fixture
def actual_cwd() -> Path:
    file_path = Path(__file__)
    assert file_path.match(
        "tests/e2e/conftest.py"
    ), f"{file_path.name} was moved without adjusting path logic"
    return file_path.parent.parent.parent


@pytest.fixture
def protostar_bin_path(actual_cwd: Path) -> Path:
    return actual_cwd / "dist" / "protostar" / "protostar"


@pytest.fixture(autouse=True)
def change_cwd(tmpdir, actual_cwd: Path):
    protostar_project_dir = Path(tmpdir) / "protostar_project"
    mkdir(protostar_project_dir)
    yield chdir(protostar_project_dir)
    chdir(actual_cwd)


@pytest.fixture
def cairo_fixtures_dir(actual_cwd: Path):
    return actual_cwd / "tests" / "e2e" / "fixtures"


@pytest.fixture
def copy_fixture(cairo_fixtures_dir) -> Callable[[Path, Path], None]:
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
    protostar_bin_path: Path, project_name: str, libs_path: str
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

        child = pexpect.spawn(f"{protostar_bin_path} init")
        child.expect(
            "project directory name:", timeout=30
        )  # the very first run is a bit slow
        child.sendline(real_project_name)
        child.expect("libraries directory *", timeout=1)
        child.sendline(real_libs_path)
        child.expect(pexpect.EOF)

    return _init_project


class ProtostarFixture(Protocol):
    def __call__(self, args: List[str], ignore_exit_code=False) -> str:
        ...


@pytest.fixture
def protostar_version() -> Optional[str]:
    return None


@pytest.fixture
def last_supported_protostar_toml_version() -> Optional[str]:
    return None


@pytest.fixture
def protostar(
    actual_cwd: Path,
    tmp_path: Path,
    protostar_version: Optional[str],
    last_supported_protostar_toml_version: Optional[str],
) -> ProtostarFixture:
    shutil.copytree(actual_cwd / "dist", tmp_path / "dist")

    if protostar_version and not last_supported_protostar_toml_version:
        last_supported_protostar_toml_version = protostar_version

    with open(
        tmp_path / "dist" / "protostar" / "info" / "pyproject.toml",
        "r+",
        encoding="UTF-8",
    ) as file:
        raw_pyproject = file.read()
        pyproject = tomli.loads(raw_pyproject)

        pyproject["tool"]["poetry"]["version"] = (
            protostar_version
            if protostar_version
            else pyproject["tool"]["poetry"]["version"]
        )

        pyproject["tool"]["protostar"]["last_supported_protostar_toml_version"] = (
            last_supported_protostar_toml_version
            if last_supported_protostar_toml_version
            else pyproject["tool"]["protostar"]["last_supported_protostar_toml_version"]
        )

        file.seek(0)
        file.truncate()
        file.write(tomli_w.dumps(pyproject))

    def _protostar(args: List[str], ignore_exit_code=False) -> str:
        return (
            run(
                [path.join(tmp_path, "dist", "protostar", "protostar")] + args,
                stdout=PIPE,
                stderr=STDOUT,
                check=(not ignore_exit_code),
            )
            .stdout.decode("utf-8")
            .strip()
        )

    return _protostar


@pytest.fixture(name="devnet_gateway_url", scope="module")
def devnet_gateway_url_fixture(devnet_port: int):
    proc = run_devnet(["poetry", "run", "starknet-devnet"], devnet_port)
    yield f"http://localhost:{devnet_port}"
    proc.kill()


@pytest.fixture
def init(
    actual_cwd: Path,
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
    chdir(actual_cwd)


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
