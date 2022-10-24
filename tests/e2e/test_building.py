from os import listdir
from pathlib import Path
from textwrap import dedent

import pytest

from tests.e2e.conftest import MyPrivateLibsSetupFixture, ProtostarFixture


@pytest.mark.usefixtures("init")
def test_default_build(protostar: ProtostarFixture):
    protostar(["build"])
    dirs = listdir()
    assert "build" in dirs


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
            "\n".join(
                ['["protostar.build"]', f'cairo_path = ["{str(my_private_libs_dir)}"]']
            )
        )

    protostar(["build"])

    dirs = listdir()
    assert "build" in dirs


def test_cairo_path_loaded_from_command_shared_section_in_config_file(
    protostar: ProtostarFixture, my_private_libs_setup: MyPrivateLibsSetupFixture
):
    (my_private_libs_dir,) = my_private_libs_setup

    with open("./protostar.toml", "a", encoding="utf-8") as protostar_toml:
        protostar_toml.write(
            "\n".join(
                [
                    '["protostar.shared_command_configs"]',
                    f'cairo_path = ["{str(my_private_libs_dir)}"]',
                ]
            )
        )

    protostar(["build"])

    dirs = listdir()
    assert "build" in dirs


def test_cairo_path_loaded_from_profile_section(
    protostar: ProtostarFixture, my_private_libs_setup: MyPrivateLibsSetupFixture
):
    (my_private_libs_dir,) = my_private_libs_setup

    protostar(["build"], expect_exit_code=1)

    with open("./protostar.toml", "a", encoding="utf-8") as protostar_toml:
        protostar_toml.write(
            "\n".join(
                [
                    "[profile.my_profile.project]",
                    f'cairo_path = ["{str(my_private_libs_dir)}"]',
                ]
            )
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
            ["protostar.config"]
            protostar_version = "0.0.0"

            ["protostar.project"]
            libs_path = "lib"

            ["protostar.contracts"]
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
