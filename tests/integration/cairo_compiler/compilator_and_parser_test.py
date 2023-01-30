from pathlib import Path
import pytest
from pytest_mock import MockerFixture

import cairo_python_bindings

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.utils import RunResources

from tests.data.cairo1_contracts import (
    CAIRO_ROLL_TEST,
)
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import ProtostarFixture
from protostar.cairo.cairo1_test_suite_parser import parse_test_suite


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="prepared_files")
def prepared_files_fixture(protostar: ProtostarFixture):
    cairo_tests_path = Path("./src/tests.cairo")
    sierra_path = Path("./src/example.sierra")
    casm_path = Path("./src/example.casm")

    paths = {
        "cairo_tests": cairo_tests_path,
        "sierra": sierra_path,
        "casm": casm_path,
    }

    for _, path in paths.items():
        protostar.create_files({str(path): ""})
        assert path.exists()

    with open(cairo_tests_path, "w") as file:
        file.write(CAIRO_ROLL_TEST)

    return paths


def test_compilator_and_parser(prepared_files: dict[str, Path], mocker: MockerFixture):
    sierra, named_tests = cairo_python_bindings.call_test_collector(  # pyright: ignore
        str(prepared_files["cairo_tests"]),
    )
    assert sierra and named_tests
    _, named_tests = cairo_python_bindings.call_test_collector(  # pyright: ignore
        str(prepared_files["cairo_tests"]),
        str(prepared_files["sierra"]),
    )
    assert named_tests
    assert Path(prepared_files["sierra"]).read_text()

    protostar_casm_json = (
        cairo_python_bindings.call_protostar_sierra_to_casm(  # pyright: ignore
            named_tests,
            str(prepared_files["sierra"]),
        )
    )
    assert protostar_casm_json
    test_suite = parse_test_suite(
        Path(str(prepared_files["casm"])), protostar_casm_json
    )
    cheat_mock = mocker.MagicMock()
    for case in test_suite.test_cases:
        runner = CairoFunctionRunner(program=test_suite.program, layout="all")
        runner.run_from_entrypoint(
            case.offset,
            *[],
            hint_locals={"roll": cheat_mock},
            static_locals={
                "__find_element_max_size": 2**20,
                "__squash_dict_max_size": 2**20,
                "__keccak_max_size": 2**20,
                "__usort_max_size": 2**20,
                "__chained_ec_op_max_len": 1000,
            },
            run_resources=RunResources(n_steps=100000000000000000),
            verify_secure=False,
        )
    assert cheat_mock.call_count == 6
