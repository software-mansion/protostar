# pylint: disable=redefined-outer-name
import json
import os
import shlex
import shutil
from os import chdir, getcwd, mkdir, path
from pathlib import Path
from subprocess import PIPE, STDOUT, run, DEVNULL
from typing import Callable, Generator, List, Optional, Tuple, Union

import pexpect
import pytest
from typing_extensions import Protocol

from protostar.self.protostar_directory import ProtostarDirectory
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
def change_cwd(tmp_path: Path, protostar_repo_root: Path):
    protostar_project_dir = tmp_path / "protostar_project"
    mkdir(protostar_project_dir)
    yield chdir(protostar_project_dir)
    chdir(protostar_repo_root)


@pytest.fixture
def cairo_fixtures_dir(protostar_repo_root: Path) -> Path:
    return protostar_repo_root / "tests" / "e2e" / "fixtures"


CopyFixture = Callable[[Union[Path, str], Union[Path, str]], None]


@pytest.fixture
def copy_fixture(
    cairo_fixtures_dir: Path,
) -> CopyFixture:
    def copy_content(file: Union[Path, str], dst: Union[Path, str]):
        if (cairo_fixtures_dir / file).is_dir():
            shutil.copytree(cairo_fixtures_dir / file, dst)
        else:
            shutil.copy(cairo_fixtures_dir / file, dst)
    return copy_content

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
    def __call__(self, override_project_name: Optional[str] = None) -> None:
        ...


@pytest.fixture
def init_project(
    protostar_bin: Path,
    project_name: str,
) -> ProjectInitializer:
    def _init_project(override_project_name: Optional[str] = None) -> None:
        if override_project_name is None:
            real_project_name = project_name
        else:
            real_project_name = override_project_name

        child = pexpect.spawn(f"{protostar_bin} init {real_project_name}")
        child.expect(pexpect.EOF, timeout=30)

    return _init_project


class ProtostarFixture(Protocol):
    def __call__(
        self,
        args: List[str],
        expect_exit_code: int = 0,
        ignore_exit_code: bool = False,
        ignore_stderr: bool = False,
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
        ignore_stderr: bool = False,
    ) -> str:
        # HACK(mkaput): When running E2E tests within PyCharm, this environment variable makes
        #   tested Protostar think that it's running within a TTY which is not expected by tests.
        #   As a workaround, we forcefully remove this environment variable from the subprocess.
        #   This problem does not occur in CI.
        env = dict(os.environ)
        if "PYCHARM_HOSTED" in env:
            del env["PYCHARM_HOSTED"]

        completed = run(
            [path.join(tmp_path, "dist", "protostar", "protostar")] + args,
            stdout=PIPE,
            stderr=DEVNULL if ignore_stderr else STDOUT,
            encoding="utf-8",
            env=env,
            check=False,
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


@pytest.fixture(name="devnet_gateway_url", scope="module")
def devnet_gateway_url_fixture(devnet_port: int, protostar_repo_root: Path):
    prev_cwd = getcwd()
    chdir(protostar_repo_root)
    proc = run_devnet(["poetry", "run", "starknet-devnet"], devnet_port)
    chdir(prev_cwd)
    yield f"http://localhost:{devnet_port}"
    proc.kill()


InitFixture = Generator[None, None, None]


@pytest.fixture
def init(
    protostar_repo_root: Path,
    project_name: str,
    protostar_toml_protostar_version: str,
    init_project: ProjectInitializer,
    libs_path: Optional[str],
) -> InitFixture:
    init_project()
    chdir(project_name)
    if protostar_toml_protostar_version or libs_path:
        protostar_toml_content = Path("protostar.toml").read_text(encoding="utf-8")
        protostar_toml_content_lines = protostar_toml_content.splitlines()
        new_protostar_toml_content_lines: list[str] = []
        for line in protostar_toml_content_lines:
            if protostar_toml_protostar_version and line.startswith(
                "protostar-version"
            ):
                new_protostar_toml_content_lines.append(
                    f'protostar-version="{protostar_toml_protostar_version}"'
                )
                continue
            if libs_path and line.startswith("lib-path"):
                new_protostar_toml_content_lines.append(f'lib-path="{libs_path}"')
                continue
            new_protostar_toml_content_lines.append(line)

        (Path() / "protostar.toml").write_text(
            "\n".join(new_protostar_toml_content_lines), encoding="utf-8"
        )
    yield
    chdir(protostar_repo_root)


MyPrivateLibsSetupFixture = Tuple[Path,]


# pylint: disable=unused-argument
@pytest.fixture(name="my_private_libs_setup")
def my_private_libs_setup_fixture(
    init: InitFixture, tmp_path: Path, copy_fixture: CopyFixture
) -> MyPrivateLibsSetupFixture:
    my_private_libs_dir = tmp_path / "my_private_libs"
    mkdir(my_private_libs_dir)

    my_lib_dir = my_private_libs_dir / "my_lib"
    mkdir(my_lib_dir)

    copy_fixture("simple_function.cairo", my_lib_dir / "utils.cairo")
    copy_fixture("main_using_simple_function.cairo", Path() / "src" / "main.cairo")
    copy_fixture(
        "test_main_using_simple_function.cairo", Path() / "tests" / "test_main.cairo"
    )
    return (my_private_libs_dir,)
