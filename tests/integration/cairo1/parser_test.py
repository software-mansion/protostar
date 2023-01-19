
from pathlib import Path
from protostar.starknet.cairo1_parser import parse_test_suite
from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.utils import RunResources
from pytest_mock import MockerFixture

def test_parse(mocker: MockerFixture):
    with open("tests/integration/cairo1/out.json", "r") as file:
        test_suite = parse_test_suite(Path("test_source.cairo"), file.read())
    cheat_mock = mocker.MagicMock()
    for case in test_suite.test_cases:
        runner = CairoFunctionRunner(program=test_suite.program, layout="all")
        runner.run_from_entrypoint(
            case.offset,
            *[],
            hint_locals={
                "roll": cheat_mock 
            },
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