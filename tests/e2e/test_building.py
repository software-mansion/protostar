import json
import os
from os import listdir
from pathlib import Path
from textwrap import dedent

import pytest

from tests.e2e.conftest import MyPrivateLibsSetupFixture, ProtostarFixture, CopyFixture


@pytest.mark.usefixtures("init")
def test_default_build(protostar: ProtostarFixture):
    protostar(["build"])
    dirs = listdir()
    assert "build" in dirs


@pytest.mark.usefixtures("init")
def test_class_hash_output(protostar: ProtostarFixture):
    output = protostar(["build"])
    assert 'Class hash for contract "main": ' in output
    assert output.split('Class hash for contract "main": ')[1].strip().startswith("0x")
    numeric_value = int(
        output.split('Class hash for contract "main": ')[1].strip()[2:], 16
    )

    output_json = protostar(["build", "--json"])
    output_json_parsed = json.loads(output_json.split("\n")[0])
    assert output_json_parsed["main"].startswith("0x")
    assert numeric_value == int(output_json_parsed["main"][2:], 16)


@pytest.mark.usefixtures("init")
def test_non_zero_exit_code_if_fails(protostar: ProtostarFixture):
    Path("./src/main.cairo").write_text(
        dedent(
            """
            %lang starknet
            @view
            func broken() {
            """
        ),
        encoding="utf-8",
    )

    protostar(["build"], expect_exit_code=1)


@pytest.mark.usefixtures("init")
def test_output_dir(protostar: ProtostarFixture):
    protostar(["build", "--compiled-contracts-dir", "out"])
    dirs = listdir()
    assert "build" not in dirs
    assert "out" in dirs


def test_cairo_path_argument(
    protostar: ProtostarFixture, my_private_libs_setup: MyPrivateLibsSetupFixture
):
    (my_private_libs_dir,) = my_private_libs_setup

    protostar(["build", "--cairo-path", str(my_private_libs_dir)])

    dirs = listdir()
    assert "build" in dirs


def test_cairo_path_loaded_from_command_config_section_in_config_file(
    protostar: ProtostarFixture, my_private_libs_setup: MyPrivateLibsSetupFixture
):
    (my_private_libs_dir,) = my_private_libs_setup

    with open("./protostar.toml", "a", encoding="utf-8") as protostar_toml:
        protostar_toml.write(
            "\n".join(["[build]", f'cairo-path = ["{str(my_private_libs_dir)}"]'])
        )

    protostar(["build"])

    dirs = listdir()
    assert "build" in dirs


@pytest.mark.usefixtures("init")
def test_cairo_path_loaded_from_command_shared_section_in_config_file(
    protostar: ProtostarFixture,
    my_private_libs_setup: MyPrivateLibsSetupFixture,
):
    (my_private_libs_dir,) = my_private_libs_setup

    Path("protostar.toml").write_text(
        dedent(
            f"""
            [project]
            protostar-version="0.0.0"
            cairo-path=["{str(my_private_libs_dir)}"]

            [contracts]
            main=["src/main.cairo"]
            """
        ),
        encoding="utf-8",
    )

    protostar(["build"])

    dirs = listdir()
    assert "build" in dirs


def test_cairo_path_loaded_from_profile_section(
    protostar: ProtostarFixture, my_private_libs_setup: MyPrivateLibsSetupFixture
):
    (my_private_libs_dir,) = my_private_libs_setup

    protostar(["build"], expect_exit_code=1)

    Path("protostar.toml").write_text(
        dedent(
            f"""
            [project]
            protostar-version="0.0.0"

            [contracts]
            main=["src/main.cairo"]

            [profile.my_profile.build]
            cairo-path=["{str(my_private_libs_dir)}"]
            """
        ),
        encoding="utf-8",
    )

    protostar(["-p", "my_profile", "build"])

    dirs = listdir()
    assert "build" in dirs


@pytest.mark.usefixtures("init")
def test_disable_hint_validation(protostar: ProtostarFixture):
    Path("./src/main.cairo").write_text(
        dedent(
            """
            %lang starknet

            @view
            func use_hint() {
                tempvar x;
                %{
                    from foo import bar
                    ids.x = 42
                %}
                assert x = 42;

                return ();
            }
            """
        ),
        encoding="utf-8",
    )

    result = protostar(["build"], ignore_exit_code=True)
    assert "Hint is not whitelisted." in result

    result = protostar(["build", "--disable-hint-validation"], ignore_exit_code=True)
    assert "Hint is not whitelisted." not in result


@pytest.mark.usefixtures("init")
def test_building_account_contract(protostar: ProtostarFixture):
    Path("./src/main.cairo").write_text(
        dedent(
            """
            %lang starknet

            @external
            func __validate__() {
                return ();
            }

            @external
            func __validate_declare__(class_hash: felt) {
                return ();
            }

            @external
            func __execute__() {
                return ();
            }
            """
        ),
        encoding="utf-8",
    )

    protostar(["build"])

    dirs = listdir()
    assert "build" in dirs


@pytest.mark.usefixtures("init")
@pytest.mark.parametrize("protostar_version", ["0.0.0"])
def test_building_project_with_modified_protostar_toml(protostar: ProtostarFixture):
    with open("./protostar.toml", mode="w", encoding="utf-8") as protostar_toml:
        protostar_toml.write(
            dedent(
                """
            [project]
            protostar-version = "0.0.0"
            lib-path = "lib"

            [contracts]
            foo = [
                "./src/main.cairo",
            ]
            bar = [
                "./src/main.cairo",
            ]
            """
            ),
        )

    protostar(["build"])

    build_dir = listdir("./build")
    assert "foo.json" in build_dir
    assert "bar.json" in build_dir


def test_build_with_contract_names(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo_0_1_mixed", "./cairo_project")
    os.chdir("./cairo_project")
    contracts = ["basic_cairo0", "basic2_cairo0"]
    for contract in contracts:
        protostar(["build", "--contract-name", contract])
        build_path = Path("build")
        assert build_path.exists()
        built_files = set(build_path.glob("*"))
        assert built_files == {
            Path("build") / (contract + ".json"),
            Path("build") / (contract + "_abi.json"),
        }
        for built_file in built_files:
            built_file.unlink()

    toml_file = Path("protostar.toml")
    toml_file.write_text(
        toml_file.read_text()
        .replace('calculate_cairo1 = ["src/calculate_cairo1.cairo"]', "")
        .replace('do_nothing_cairo1 = ["src/do_nothing_cairo1.cairo"]', "")
    )
    protostar(["build"])
    build_path = Path("build")
    assert build_path.exists()
    built_files = set(build_path.glob("*"))
    assert built_files == set(
        [Path("build") / (contract + ".json") for contract in contracts]
        + [Path("build") / (contract + "_abi.json") for contract in contracts]
    )


def test_build_cairo0_cairo1_mixed(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo_0_1_mixed", "./cairo_project")
    os.chdir("./cairo_project")
    protostar(["build"], expect_exit_code=1)
    protostar(["build-cairo1"], expect_exit_code=1)
    cairo0_contracts = ["basic_cairo0", "basic2_cairo0"]
    cairo1_contracts = ["calculate_cairo1", "do_nothing_cairo1"]
    for contract in cairo0_contracts:
        protostar(["build", "--contract-name", contract])
    for contract in cairo1_contracts:
        protostar(["build-cairo1", "--contract-name", contract])
