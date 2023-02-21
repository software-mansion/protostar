from pathlib import Path
import pytest
from pytest_mock import MockerFixture

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.utils import RunResources

from protostar.cairo.cairo1_test_suite_parser import (
    program_from_casm,
    get_test_name_to_offset_map_from_casm,
)


@pytest.fixture(name="test_suite_json")
def test_suite_json_fixture(datadir: Path) -> str:
    # Cairo source code of the tested fixture - ../cairo_compiler/contracts/roll_test.cairo
    with open(datadir / "compiled_test_suite.json", "r") as file:
        return file.read()


def test_parse(mocker: MockerFixture, test_suite_json: str):
    program = program_from_casm(test_suite_json)
    test_name_to_offset_map = get_test_name_to_offset_map_from_casm(test_suite_json)

    cheat_mock = mocker.MagicMock()
    cheat_mock.return_value = 0

    for case_offset in test_name_to_offset_map.values():
        runner = CairoFunctionRunner(program, layout="all")
        runner.run_from_entrypoint(
            case_offset,
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
