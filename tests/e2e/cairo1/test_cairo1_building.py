from pathlib import Path
from typing import Optional, Callable

import os

import pytest

from tests.e2e.conftest import ProtostarFixture, CopyFixture


def run_build_with_custom_action(
    protostar: ProtostarFixture,
    copy_fixture: CopyFixture,
    action: Optional[Callable] = None,
):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")
    if action:
        action()
    protostar(["build-cairo1"])


def test_cairo1_build(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    run_build_with_custom_action(protostar, copy_fixture)
    compiled_path = Path("build/main.json")
    assert compiled_path.exists()
    assert compiled_path.read_text()


def test_cairo1_build_invalid_contract_path_to_cairo_file(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    def _action():
        protostar_toml = Path("protostar.toml")
        protostar_toml.write_text(
            protostar_toml.read_text().replace(
                'main = ["src"]', 'main = ["src/lib.cairo"]'
            )
        )

    with pytest.raises(Exception) as ex:
        run_build_with_custom_action(
            protostar=protostar, copy_fixture=copy_fixture, action=_action
        )
    assert "invalid input path: a directory path is expected, a file was received" is ex


def test_cairo1_build_invalid_contract_non_existent_path(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    def _action():
        protostar_toml = Path("protostar.toml")
        protostar_toml.write_text(
            protostar_toml.read_text().replace('main = ["src"]', 'main = ["srcc"]')
        )

    with pytest.raises(Exception) as ex:
        run_build_with_custom_action(
            protostar=protostar, copy_fixture=copy_fixture, action=_action
        )
    assert "invalid input path: a directory path is expected" is ex


def test_cairo1_build_invalid_contract_no_contract(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    def _action():
        lib_cairo = Path("src/lib.cairo")
        lib_cairo.write_text(lib_cairo.read_text().replace("#[contract]", ""))

    with pytest.raises(Exception) as ex:
        run_build_with_custom_action(
            protostar=protostar, copy_fixture=copy_fixture, action=_action
        )
    assert "Contract not found" is ex
