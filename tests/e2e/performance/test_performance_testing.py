import multiprocessing
import shutil
from time import time
from pathlib import Path
from string import Template
from contextlib import contextmanager
from typing import List

import pytest

from protostar.commands.test.test_collector import TestCollector
from protostar.commands.test.test_runner import TestRunner
from protostar.commands.test.test_shared_tests_state import SharedTestsState
from protostar.commands.test.test_suite import TestSuite
from protostar.utils.compiler.pass_managers import ProtostarPassMangerFactory
from protostar.utils.starknet_compilation import StarknetCompiler, CompilerConfig

SCRIPT_DIRECTORY = Path(__file__).parent


def _multiply_cases(test_body: str) -> (str, List[str]):
    source_code = ""
    cases_names = []
    for i in range(10):
        case_name = f"test_case_{i}"
        source_code += Template(
            """
            @external
            func $case_name{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
                $body
                return ()
            end
            """
        ).substitute(case_name=case_name, body=test_body)
    return source_code, cases_names


def make_test_file(test_body: str) -> (Path, List[str]):
    source, cases = _multiply_cases(test_body)
    return f"""
        %lang starknet
        from starkware.cairo.common.cairo_builtins import HashBuiltin
        {source}
    """, cases


@pytest.fixture(name="tmp_test_dir")
def make_test_dir() -> Path:
    test_dir_path = SCRIPT_DIRECTORY / "tmp_test_files"
    test_dir_path.mkdir()
    yield test_dir_path
    shutil.rmtree(test_dir_path)


@contextmanager
def timing(expected):
    start_timer = time()
    yield
    stop_timer = time()
    elapsed = stop_timer - start_timer
    assert elapsed <= expected


async def run_tests(tests_source: str, test_dir_path: Path, test_case_names: List[str]):
    compiler = StarknetCompiler(
        config=CompilerConfig(
            include_paths=[],
            disable_hint_validation=True
        ),
        pass_manager_factory=ProtostarPassMangerFactory,
    )
    test_file_path = test_dir_path / 'tempfile_test.cairo'
    with open(test_file_path, mode="x", encoding="utf-8") as file:
        file.write(tests_source)

    contract = compiler.compile_contract(test_file_path)
    this_test_suite = TestSuite(test_path=test_file_path, test_case_names=test_case_names)
    with multiprocessing.Manager() as manager:
        tests_state = SharedTestsState(
            test_collector_result=TestCollector.Result(test_suites=[this_test_suite]),
            manager=manager,
        )
        runner = TestRunner(
            shared_tests_state=tests_state,
            include_paths=[],
        )

        await runner._run_test_suite(
            test_contract=contract,
            test_suite=this_test_suite,
        )
        # print(tests_state.get_result().display())
        assert not tests_state.any_failed_or_broken(), tests_state.get_result().display()


@pytest.mark.asyncio
async def test_deploy_perf(tmp_test_dir, request):
    test_source, case_names = make_test_file(
        Template("%{ deploy_contract('$contractpath') %}").substitute(
            contractpath=(Path(request.node.fspath).parent / 'basic.cairo').absolute()
        )
    )
    with timing(expected=3):
        await run_tests(
            tests_source=test_source,
            test_dir_path=tmp_test_dir,
            test_case_names=case_names,
        )


@pytest.mark.asyncio
async def test_setup_perf(tmp_test_dir):
    test_cases, case_names = make_test_file(
        """
        let (value) = storage_variable.read(20)
        assert value = 1
        """
    )

    test_source = Template(
        """
        $cases
        @storage_var
        func storage_variable(a: felt) -> (res: felt):
        end

        func __setup__{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
            storage_variable.write(20, 1)
            return ()
        end
        """
    ).substitute(cases=test_cases)

    with timing(expected=3):
        await run_tests(
            tests_source=test_source,
            test_dir_path=tmp_test_dir,
            test_case_names=case_names,
        )


def test_expect_revert_perf():
    pass


def test_expect_events_perf():
    pass


def test_deploy_contract_perf():
    pass


def test_declare_perf():
    pass


def test_prepare_perf():
    pass


def test_start_prank_perf():
    pass


def test_roll_perf():
    pass


def test_warp_perf():
    pass


def test_assertions_perf():
    pass


def test_unit_testing_perf():
    pass


def test_integration_perf():
    pass
