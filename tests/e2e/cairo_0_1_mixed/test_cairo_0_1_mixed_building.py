from pathlib import Path

import os

from tests.e2e.conftest import ProtostarFixture, CopyFixture


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
        assert set(built_files) == {
            Path("build") / (contract + ".casm.json"),
            Path("build") / (contract + ".sierra.json"),
            Path("build") / (contract + ".class.hash"),
            Path("build") / (contract + ".compiled.class.hash"),
        }
        for file in built_files:
            file.unlink()


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
    actual_built_files = set(list(build_path.glob("*")))
    expected_built_files = set()
    for contract in contracts:
        expected_built_files.add(Path("build") / (contract + ".casm.json"))
        expected_built_files.add(Path("build") / (contract + ".sierra.json"))
        expected_built_files.add(Path("build") / (contract + ".class.hash"))
        expected_built_files.add(Path("build") / (contract + ".compiled.class.hash"))
    assert actual_built_files == expected_built_files


def test_cairo0_build_with_contract_names_separate_builds(
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


def test_cairo0_cairo1_build_mixed(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo_0_1_mixed", "./cairo_project")
    os.chdir("./cairo_project")
    protostar(["build"], expect_exit_code=1)
    protostar(["build-cairo1"], expect_exit_code=1)
    cairo0_contracts = ["basic_cairo0", "basic2_cairo0"]
    cairo1_contracts = ["calculate_cairo1", "do_nothing_cairo1"]
    for contract in cairo0_contracts:
        output = protostar(["build", "--contract-name", contract])
        assert f'Class hash for contract "{ contract }": ' in output
    for contract in cairo1_contracts:
        output = protostar(["build-cairo1", "--contract-name", contract])
        assert "Contracts built successfully" in output
