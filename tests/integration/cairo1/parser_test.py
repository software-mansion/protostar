
from pathlib import Path
from protostar.starknet.cairo1_parser import parse
from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner, CairoRunner
from starkware.cairo.lang.vm.utils import RunResources

def roll_c(address, caller_address):
    print(address, caller_address, "Cheatcode sie wykonuje")

def test_parse():
    program, tests = parse(Path("tests/integration/cairo1/out.json"))
    runner = CairoFunctionRunner(program=program, layout="all")
    runner.run_from_entrypoint(
        6,
        *[],
        hint_locals={
            "roll": roll_c 
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

    assert False