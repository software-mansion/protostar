from pathlib import Path

import os

from tests.e2e.conftest import ProtostarFixture, CopyFixture


def test_cairo1_build(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")
    protostar(["build-cairo1"])
    compiled_path = Path("build/main.json")
    assert compiled_path.exists()
    assert compiled_path.read_text()


def test_cairo1_build_with_contract_names_separate_builds(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo_0_1_mixed", "./cairo_project")
    os.chdir("./cairo_project")
    contracts = ["calculate_cairo1", "do_nothing_cairo1"]
    for contract in contracts:
        protostar(["build-cairo1", "--contract-name", contract])
        build_path = Path("build")
        assert build_path.exists()
        built_files = list(build_path.glob("*"))
        assert built_files == [Path("build") / (contract + ".json")]
        built_files[0].unlink()


def test_cairo1_build_with_contract_names_build_together(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo_0_1_mixed", "./cairo_project")
    os.chdir("./cairo_project")
    contracts = ["calculate_cairo1", "do_nothing_cairo1"]
    toml_file = Path("protostar.toml")
    toml_file.write_text(
        toml_file.read_text()
        .replace('basic_cairo0 = ["src/basic_cairo0.cairo"]', "")
        .replace('basic2_cairo0 = ["src/basic2_cairo0.cairo"]', "")
    )
    protostar(["build-cairo1"])
    build_path = Path("build")
    assert build_path.exists()
    built_files = list(build_path.glob("*"))
    assert set(built_files) == set(
        Path("build") / (contract + ".json") for contract in contracts
    )
