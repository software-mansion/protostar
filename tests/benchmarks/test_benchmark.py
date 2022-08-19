import multiprocessing
from contextlib import asynccontextmanager
import asyncio
import threading
from multiprocessing.managers import SyncManager
from pathlib import Path
from string import Template
from typing import List, Optional, Tuple

import pytest
from starkware.starknet.services.api.contract_class import ContractClass

from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzConfig,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_collector import TestCollector
from protostar.commands.test.test_config import TestConfig
from protostar.commands.test.test_runner import TestRunner
from protostar.commands.test.test_shared_tests_state import SharedTestsState
from protostar.commands.test.test_suite import TestSuite, TestCase
from protostar.utils.compiler.pass_managers import ProtostarPassMangerFactory
from protostar.utils.starknet_compilation import StarknetCompiler, CompilerConfig
from tests.benchmarks.constants import ROUNDS_NUMBER

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
        test_cases=[TestCase(test_fn_name=case_name) for case_name in case_names],
        setup_fn_name=setup_fn_name,
    )
    return contract, suite


async def prepare_suite(
    manager: SyncManager, test_suite: TestSuite, contract: ContractClass
) -> Tuple[TestRunner, SharedTestsState, Optional[TestExecutionState]]:
    tests_state = SharedTestsState(
        test_collector_result=TestCollector.Result(test_suites=[test_suite]),
        manager=manager,
    )
    runner = TestRunner(
        shared_tests_state=tests_state,
        include_paths=[],
        # TODO(mkaput): Remove this along with --fuzz-max-examples argument.
        fuzz_config=FuzzConfig(),
    )

    # pylint: disable=protected-access
    execution_state = await runner._build_execution_state(
        test_contract=contract,
        test_suite=test_suite,
        test_config=TestConfig(),
    )
    return runner, tests_state, execution_state


def wait_for_completion(test_suite: TestSuite, tests_state: SharedTestsState):
    tests_left = len(test_suite.test_cases)
    while tests_left:
        tests_state.get_result()
        tests_left -= 1

    assert (
        not tests_state.any_failed_or_broken()
    ), "Tests failed! See logs above for more info"


# https://github.com/ionelmc/pytest-benchmark/issues/66#issuecomment-575853801
@pytest.fixture(scope="function", name="aio_benchmark")
def aio_benchmark_fixture(benchmark):
    class Sync2Async:
        def __init__(self, coro, *args, **kwargs):
            self.coro = coro
            self.args = args
            self.kwargs = kwargs
            self.custom_loop = None
            self.thread = None

        def start_background_loop(self) -> None:
            asyncio.set_event_loop(self.custom_loop)
            if self.custom_loop:
                self.custom_loop.run_forever()
            raise RuntimeError("No custom_loop set!")

        def __call__(self):
            evloop = None
            awaitable = self.coro(*self.args, **self.kwargs)
            try:
                evloop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if evloop is None:
                return asyncio.run(awaitable)

            if not self.custom_loop or not self.thread or not self.thread.is_alive():
                self.custom_loop = asyncio.new_event_loop()
                self.thread = threading.Thread(
                    target=self.start_background_loop, daemon=True
                )
                self.thread.start()

            return asyncio.run_coroutine_threadsafe(
                awaitable, self.custom_loop
            ).result()

    def _wrapper(func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            prepared_function = Sync2Async(func, *args, **kwargs)
            return benchmark.pedantic(prepared_function, rounds=ROUNDS_NUMBER)
        return benchmark.pedantic(func, rounds=ROUNDS_NUMBER, args=args, kwargs=kwargs)

    return _wrapper


@asynccontextmanager
async def prepare_tests(contract_class: ContractClass, test_suite: TestSuite):
    with multiprocessing.Manager() as manager:
        runner, shared_state, execution_state = await prepare_suite(
            manager, test_suite, contract_class
        )
        if not execution_state:
            return

        async def run():
            # pylint: disable=protected-access
            await runner._invoke_test_cases(test_suite, execution_state)

        yield run

        wait_for_completion(test_suite, shared_state)


async def test_deploy_perf(aio_benchmark, tmp_path, basic_contract_path):
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

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_setup_perf(aio_benchmark, tmp_path, basic_contract_path):
    test_cases, case_names = make_test_file(
        """
        alloc_locals
        local deployed_contract_address: felt
        %{ ids.deployed_contract_address = context.deployed_contract_addr %}
        """
    )
    definitions = Template(
        """
        @external
        func __setup__{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
            %{ context.deployed_contract_addr = deploy_contract("$basic_contract_path").contract_address %}
            return ()
        end
        """
    ).substitute(basic_contract_path=basic_contract_path)

    contract_class, test_suite = build_test_suite(
        source_code=test_cases + definitions,
        file_path=tmp_path,
        case_names=case_names,
        setup_fn_name="__setup__",
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_expect_revert_perf(aio_benchmark, tmp_path):
    test_cases, case_names = make_test_file(
        """
        %{ expect_revert() %}
        assert 1=2
        """
    )
    contract_class, test_suite = build_test_suite(
        source_code=test_cases, file_path=tmp_path, case_names=case_names
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_expect_events_perf(aio_benchmark, tmp_path):
    test_cases, case_names = make_test_file(
        """
        %{ expect_events({"name": "increase_balance_called", "data": {"current_balance": 123, "amount": 20} }) %}
        increase_balance_called.emit(123, 20)
        """
    )

    definitions = """
        @event
        func increase_balance_called(
            current_balance : felt, amount : felt
        ):
        end
    """

    contract_class, test_suite = build_test_suite(
        source_code=test_cases + definitions,
        file_path=tmp_path,
        case_names=case_names,
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_declare_perf(aio_benchmark, tmp_path, basic_contract_path):
    test_cases, case_names = make_test_file(
        Template('%{ declare("$contractpath") %}').substitute(
            contractpath=basic_contract_path
        )
    )

    contract_class, test_suite = build_test_suite(
        source_code=test_cases, file_path=tmp_path, case_names=case_names
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_prepare_perf(aio_benchmark, tmp_path, basic_contract_path):
    test_cases, case_names = make_test_file(
        "%{ prepared = prepare(context.declared, [1,2,3]) %}"
    )
    definitions = Template(
        """
        @external
        func __setup__{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
            %{ context.declared = declare("$contractpath") %}
            return ()
        end
    """
    ).substitute(contractpath=basic_contract_path)

    contract_class, test_suite = build_test_suite(
        source_code=test_cases + definitions,
        file_path=tmp_path,
        case_names=case_names,
        setup_fn_name="__setup__",
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_start_prank_perf(aio_benchmark, tmp_path):
    test_cases, case_names = make_test_file(
        test_body="""
            %{ start_prank(12) %}
            let (address) = get_caller_address()
            assert address = 12
        """,
        imports="""from starkware.starknet.common.syscalls import get_caller_address""",
    )

    contract_class, test_suite = build_test_suite(
        source_code=test_cases,
        file_path=tmp_path,
        case_names=case_names,
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_roll_perf(aio_benchmark, tmp_path):
    test_cases, case_names = make_test_file(
        test_body="""
            %{ roll(12) %}
            let (address) = get_block_number()
            assert address = 12
        """,
        imports="""from starkware.starknet.common.syscalls import get_block_number""",
    )

    contract_class, test_suite = build_test_suite(
        source_code=test_cases,
        file_path=tmp_path,
        case_names=case_names,
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_warp_perf(aio_benchmark, tmp_path):
    test_cases, case_names = make_test_file(
        test_body="""
            %{ warp(12) %}
            let (time) = get_block_timestamp()
            assert time = 12
        """,
        imports="""from starkware.starknet.common.syscalls import get_block_timestamp""",
    )

    contract_class, test_suite = build_test_suite(
        source_code=test_cases,
        file_path=tmp_path,
        case_names=case_names,
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_assertions_perf(aio_benchmark, tmp_path, protostar_cairo_path):
    # TODO: Leverage fuzz testing here, when it's implemented
    # TODO: Add cases for both minus values when asserts are fixed
    test_cases, case_names = make_test_file(
        test_body="""
            assert_eq(1, 1)
            assert_not_eq(1, 2)
            assert_signed_lt(-1, 2)
            assert_unsigned_lt(1, 2)
            assert_signed_le(2, 2)
            assert_signed_le(-2, 3)
            assert_unsigned_le(2, 3)
            assert_signed_gt(6, -3)
            assert_unsigned_gt(3, 2)
            assert_signed_ge(3, 3)
            assert_signed_ge(4, -3)
            assert_unsigned_ge(7, 3)
            assert_unsigned_ge(7, 7)
        """,
        imports="""
        from protostar.asserts import (
                assert_eq,
                assert_not_eq,
                assert_signed_lt,
                assert_unsigned_lt,
                assert_signed_le,
                assert_unsigned_le,
                assert_signed_gt,
                assert_unsigned_gt,
                assert_signed_ge,
                assert_unsigned_ge
        )""",
    )

    contract_class, test_suite = build_test_suite(
        source_code=test_cases,
        file_path=tmp_path,
        case_names=case_names,
        include_paths=[str(protostar_cairo_path)],
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_unit_testing_perf(aio_benchmark, tmp_path):
    test_cases, case_names = make_test_file(
        test_body="""
        let var1 = 1
        assert_not_zero(var1)
        let var2 = var1 + 3
        assert_lt(var1, var2)
        """,
        imports="from starkware.cairo.common.math import assert_not_zero, assert_lt",
    )

    contract_class, test_suite = build_test_suite(
        source_code=test_cases, file_path=tmp_path, case_names=case_names
    )

    async with prepare_tests(contract_class, test_suite) as run_tests:
        aio_benchmark(run_tests)


async def test_collecting_tests_perf(aio_benchmark, tmp_path):
    test_cases, case_names = make_test_file(
        test_body="""
        let var1 = 1
        assert_not_zero(var1)
        let var2 = var1 + 3
        assert_lt(var1, var2)
        """,
        imports="from starkware.cairo.common.math import assert_not_zero, assert_lt",
    )

    def build_subtree(
        current_directory: Path, current_depth=0, width=3, max_depth=3, files=5
    ):
        """
        Builds subtree of `width` catalogs recursively, until reached depth of max_depth.
        Puts `files` sample test files into the directory
        """
        if current_depth == max_depth:
            return
        for i in range(files):
            build_test_suite(
                source_code=test_cases,
                file_path=current_directory / f"test_file_{i}.cairo",
                case_names=case_names,
            )
        for i in range(width):
            dir_name = current_directory / f"dir_{i}"
            dir_name.mkdir()
            build_subtree(
                current_directory=dir_name,  # Continue in the descendant
                current_depth=current_depth + 1,
            )

    build_subtree(current_directory=tmp_path)

    test_collector = TestCollector(starknet_compiler=get_test_starknet_compiler())
    result = aio_benchmark(test_collector.collect, [str(tmp_path)])
    assert result.test_cases_count == 195
