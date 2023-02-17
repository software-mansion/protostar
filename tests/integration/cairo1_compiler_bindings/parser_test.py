from pathlib import Path
import pytest
from pytest_mock import MockerFixture

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.utils import RunResources

from protostar.cairo.cairo1_test_suite_parser import parse_test_suite


@pytest.fixture(name="test_suite_json")
def test_suite_json_fixture(datadir: Path) -> str:
    # Cairo source code of the tested fixture - ../cairo_compiler/contracts/hint_locals_test.cairo
    with open(datadir / "compiled_test_suite.json", "r") as file:
        return file.read()


def test_parse(mocker: MockerFixture, test_suite_json: str):
    for mocked_error_code in [0, 1]:
        test_suite = parse_test_suite(Path("test_source.cairo"), test_suite_json)

        cheat_mock = mocker.MagicMock()
        cheat_mock.return_value = type(
            "return_value", (object,), {"err_code": mocked_error_code}
        )()

        declare_mock = mocker.MagicMock()
        ok = type("ok", (object,), {"class_hash": 0})()
        declare_mock.return_value = type(
            "return_value", (object,), {"err_code": mocked_error_code, "ok": ok}
        )()

        for case in test_suite.test_cases:
            runner = CairoFunctionRunner(program=test_suite.program, layout="all")
            runner.run_from_entrypoint(
                case.offset,
                *[],
                hint_locals={
                    "roll": cheat_mock,
                    "declare": declare_mock,
                    "start_prank": cheat_mock,
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
            assert mocked_error_code == runner.get_return_values(3)[0]
