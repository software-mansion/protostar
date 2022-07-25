import asyncio
import multiprocessing
import sys
from pathlib import Path
from string import Template
from typing import List, Optional, Tuple

import pytest
from starkware.starknet.services.api.contract_class import ContractClass

from protostar.commands.test.environments.factory import (
    InvokeCaseCallable,
    invoke_test_case,
)
from protostar.commands.test.test_cases import PassedTestCase
from protostar.commands.test.test_collector import TestCollector
from protostar.commands.test.test_runner import TestRunner
from protostar.commands.test.test_shared_tests_state import SharedTestsState
from protostar.commands.test.test_suite import TestSuite
from protostar.utils.compiler.pass_managers import ProtostarPassMangerFactory
from protostar.utils.starknet_compilation import StarknetCompiler, CompilerConfig

SCRIPT_DIRECTORY = Path(__file__).parent


def _multiply_cases(test_body: str) -> Tuple[str, List[str]]:
    source_code = ""
    cases_names = []
    for i in range(3):
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
        cases_names.append(case_name)
    return source_code, cases_names


def make_test_file(
    test_body: str, imports: Optional[str] = ""
) -> Tuple[str, List[str]]:
    source, cases = _multiply_cases(test_body)
    return (
        f"""
        %lang starknet
        from starkware.cairo.common.cairo_builtins import HashBuiltin
        {imports}
        {source}
    """,
        cases,
    )


@pytest.fixture(name="basic_contract_path")
def basic_contract_path_fixture(request) -> Path:
    return (Path(request.node.fspath).parent / "basic.cairo").absolute()


@pytest.fixture(name="protostar_cairo_path")
def protostar_cairo_path_fixture(request) -> Path:
    return (Path(request.node.fspath).parent.parent.parent / "cairo").absolute()


def get_test_starknet_compiler(
    include_paths: Optional[List[str]] = None,
) -> StarknetCompiler:
    return StarknetCompiler(
        config=CompilerConfig(
            include_paths=include_paths or [], disable_hint_validation=True
        ),
        pass_manager_factory=ProtostarPassMangerFactory,
    )


def build_test_suite(
    source_code: str,
    case_names: List[str],
    file_path: Path,
    setup_fn_name: Optional[str] = None,
    include_paths: Optional[List[str]] = None,
) -> Tuple[ContractClass, TestSuite]:
    compiler = get_test_starknet_compiler(include_paths)

    if not file_path.name.endswith(".cairo"):
        file_path = file_path / "tempfile_test.cairo"

    with open(file_path, mode="w", encoding="utf-8") as file:
        file.write(source_code)

    contract = compiler.compile_contract(file_path, add_debug_info=True)
    suite = TestSuite(
        test_path=file_path,
        test_case_names=case_names,
        setup_fn_name=setup_fn_name,
    )
    return contract, suite


async def run_tests(
    test_suite: TestSuite, contract: ContractClass, invoke_fn: InvokeCaseCallable
):
    with multiprocessing.Manager() as manager:
        tests_state = SharedTestsState(
            test_collector_result=TestCollector.Result(test_suites=[test_suite]),
            manager=manager,
        )
        runner = TestRunner(
            shared_tests_state=tests_state,
            include_paths=[],
        )

        # pylint: disable=protected-access
        await runner._run_test_suite(
            test_contract=contract,
            test_suite=test_suite,
            invoke_case=invoke_fn,
        )

        tests_left = len(test_suite.test_case_names)
        while tests_left:
            test_result = tests_state.get_result()
            if isinstance(test_result, PassedTestCase):
                out = sys.stdout
            else:
                out = sys.stderr

            print(test_result.display(), file=out)
            tests_left -= 1

        assert (
            not tests_state.any_failed_or_broken()
        ), "Tests failed! See logs above for more info"


@pytest.mark.asyncio
async def test_deploy_perf(benchmark, tmp_path, basic_contract_path):
    test_source, case_names = make_test_file(
        Template("%{ deploy_contract('$contractpath') %}").substitute(
            contractpath=basic_contract_path
        )
    )
    contract_class, test_suite = build_test_suite(
        source_code=test_source,
        file_path=tmp_path,
        case_names=case_names,
    )

    def benchmarked_invoke(*args, **kwargs):
        def schedule_task_and_run(*args, **kwargs):
            loop = asyncio.get_running_loop()
            task = loop.create_task(invoke_test_case(*args, **kwargs))
            while not task.done():
                pass
            return task.result()

        result = benchmark(schedule_task_and_run, *args, **kwargs)
        return result

    await run_tests(
        contract=contract_class,
        test_suite=test_suite,
        invoke_fn=benchmarked_invoke,
    )


# @pytest.mark.asyncio
# async def test_setup_perf(benchmark, tmp_path, basic_contract_path):
#     test_cases, case_names = make_test_file(
#         """
#         alloc_locals
#         local deployed_contract_address: felt
#         %{ ids.deployed_contract_address = context.deployed_contract_addr %}
#         """
#     )
#     definitions = Template(
#         """
#         @external
#         func __setup__{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
#             %{ context.deployed_contract_addr = deploy_contract("$basic_contract_path").contract_address %}
#             return ()
#         end
#         """
#     ).substitute(basic_contract_path=basic_contract_path)
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases + definitions,
#         file_path=tmp_path,
#         case_names=case_names,
#         setup_fn_name="__setup__",
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_expect_revert_perf(benchmark, tmp_path):
#     test_cases, case_names = make_test_file(
#         """
#         %{ expect_revert() %}
#         assert 1=2
#         """
#     )
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases, file_path=tmp_path, case_names=case_names
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_expect_events_perf(benchmark, tmp_path):
#     test_cases, case_names = make_test_file(
#         """
#         %{ expect_events({"name": "increase_balance_called", "data": {"current_balance": 123, "amount": 20} }) %}
#         increase_balance_called.emit(123, 20)
#         """
#     )
#
#     definitions = """
#         @event
#         func increase_balance_called(
#             current_balance : felt, amount : felt
#         ):
#         end
#     """
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases + definitions,
#         file_path=tmp_path,
#         case_names=case_names,
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_declare_perf(benchmark, tmp_path, basic_contract_path):
#     test_cases, case_names = make_test_file(
#         Template('%{ declare("$contractpath") %}').substitute(
#             contractpath=basic_contract_path
#         )
#     )
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases, file_path=tmp_path, case_names=case_names
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_prepare_perf(benchmark, tmp_path, basic_contract_path):
#     test_cases, case_names = make_test_file(
#         "%{ prepared = prepare(context.declared, [1,2,3]) %}"
#     )
#     definitions = Template(
#         """
#         @external
#         func __setup__{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
#             %{ context.declared = declare("$contractpath") %}
#             return ()
#         end
#     """
#     ).substitute(contractpath=basic_contract_path)
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases + definitions,
#         file_path=tmp_path,
#         case_names=case_names,
#         setup_fn_name="__setup__",
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_start_prank_perf(benchmark, tmp_path):
#     test_cases, case_names = make_test_file(
#         test_body="""
#             %{ start_prank(12) %}
#             let (address) = get_caller_address()
#             assert address = 12
#         """,
#         imports="""from starkware.starknet.common.syscalls import get_caller_address""",
#     )
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases,
#         file_path=tmp_path,
#         case_names=case_names,
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_roll_perf(benchmark, tmp_path):
#     test_cases, case_names = make_test_file(
#         test_body="""
#             %{ roll(12) %}
#             let (address) = get_block_number()
#             assert address = 12
#         """,
#         imports="""from starkware.starknet.common.syscalls import get_block_number""",
#     )
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases,
#         file_path=tmp_path,
#         case_names=case_names,
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_warp_perf(benchmark, tmp_path):
#     test_cases, case_names = make_test_file(
#         test_body="""
#             %{ warp(12) %}
#             let (time) = get_block_timestamp()
#             assert time = 12
#         """,
#         imports="""from starkware.starknet.common.syscalls import get_block_timestamp""",
#     )
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases,
#         file_path=tmp_path,
#         case_names=case_names,
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_assertions_perf(benchmark, tmp_path, protostar_cairo_path):
#     # TODO: Leverage fuzz testing here, when it's implemented
#     # TODO: Add cases for both minus values when asserts are fixed
#     test_cases, case_names = make_test_file(
#         test_body="""
#             assert_eq(1, 1)
#             assert_not_eq(1, 2)
#             assert_signed_lt(-1, 2)
#             assert_unsigned_lt(1, 2)
#             assert_signed_le(2, 2)
#             assert_signed_le(-2, 3)
#             assert_unsigned_le(2, 3)
#             assert_signed_gt(6, -3)
#             assert_unsigned_gt(3, 2)
#             assert_signed_ge(3, 3)
#             assert_signed_ge(4, -3)
#             assert_unsigned_ge(7, 3)
#             assert_unsigned_ge(7, 7)
#         """,
#         imports="""
#         from protostar.asserts import (
#                 assert_eq,
#                 assert_not_eq,
#                 assert_signed_lt,
#                 assert_unsigned_lt,
#                 assert_signed_le,
#                 assert_unsigned_le,
#                 assert_signed_gt,
#                 assert_unsigned_gt,
#                 assert_signed_ge,
#                 assert_unsigned_ge
#         )""",
#     )
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases,
#         file_path=tmp_path,
#         case_names=case_names,
#         include_paths=[protostar_cairo_path],
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_unit_testing_perf(benchmark, tmp_path):
#     test_cases, case_names = make_test_file(
#         test_body="""
#         let var1 = 1
#         assert_not_zero(var1)
#         let var2 = var1 + 3
#         assert_lt(var1, var2)
#         """,
#         imports="from starkware.cairo.common.math import assert_not_zero, assert_lt",
#     )
#
#     contract_class, test_suite = build_test_suite(
#         source_code=test_cases, file_path=tmp_path, case_names=case_names
#     )
#
#     run_tests(test_suite=test_suite, contract=contract_class, invoke_fn=timed_invoke)
#
#
# @pytest.mark.asyncio
# async def test_collecting_tests_perf(benchmark, tmp_path):
#     test_cases, case_names = make_test_file(
#         test_body="""
#         let var1 = 1
#         assert_not_zero(var1)
#         let var2 = var1 + 3
#         assert_lt(var1, var2)
#         """,
#         imports="from starkware.cairo.common.math import assert_not_zero, assert_lt",
#     )
#
#     def build_subtree(
#         current_directory: Path, current_depth=0, width=3, max_depth=3, files=5
#     ):
#         """
#         Builds subtree of `width` catalogs recursively, until reached depth of max_depth.
#         Puts `files` sample test files into the directory
#         """
#         if current_depth == max_depth:
#             return
#         for i in range(files):
#             build_test_suite(
#                 source_code=test_cases,
#                 file_path=current_directory / f"test_file_{i}.cairo",
#                 case_names=case_names,
#             )
#         for i in range(width):
#             dir_name = current_directory / f"dir_{i}"
#             dir_name.mkdir()
#             build_subtree(
#                 current_directory=dir_name,  # Continue in the descendant
#                 current_depth=current_depth + 1,
#             )
#
#     build_subtree(current_directory=tmp_path)
#
#     test_collector = TestCollector(starknet_compiler=get_test_starknet_compiler())
#     result = benchmark(test_collector.collect, [str(tmp_path)])
#     assert result.test_cases_count == 195
