from os import listdir, mkdir
from pathlib import Path

import pytest


# pylint: disable=unused-argument
@pytest.fixture(name="my_private_libs_setup")
def my_private_libs_setup_fixture(init, tmpdir, copy_fixture):
    my_private_libs_dir = Path(tmpdir) / "my_private_libs"
    mkdir(my_private_libs_dir)

    my_lib_dir = my_private_libs_dir / "my_lib"
    mkdir(my_lib_dir)

    copy_fixture("simple_function.cairo", my_lib_dir / "utils.cairo")

    with open("./src/main.cairo", mode="w", encoding="utf-8") as my_contract:
        my_contract.write(
            """%lang starknet
from my_lib.utils import get_my_number

@view
func my_func() -> (res: felt):
    let (res) = get_my_number()
    return (res)
end
"""
        )
    return (my_private_libs_dir,)


@pytest.mark.usefixtures("init")
def test_default_build(protostar):
    protostar(["build"])
    dirs = listdir()
    assert "build" in dirs


@pytest.mark.usefixtures("init")
def test_output_dir(protostar):
    protostar(["build", "--output", "out"])
    dirs = listdir()
    assert "build" not in dirs
    assert "out" in dirs


def test_cairo_path_argument(protostar, my_private_libs_setup):
    (my_private_libs_dir,) = my_private_libs_setup

    protostar(["build", "--cairo-path", my_private_libs_dir])

    dirs = listdir()
    assert "build" in dirs


@pytest.mark.usefixtures("init")
def test_disable_hint_validation(protostar):

    with open("./src/main.cairo", mode="w", encoding="utf-8") as my_contract:
        my_contract.write(
            """%lang starknet

@view
func use_hint():
    tempvar x
    %{
        from foo import bar
        ids.x = 42
    %}
    assert x = 42

    return ()
end
"""
        )

    result = protostar(["build"])
    assert "Hint is not whitelisted." in result

    result = protostar(["build", "--disable-hint-validation"])
    assert result == ""
