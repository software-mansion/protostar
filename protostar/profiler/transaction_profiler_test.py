import pytest
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ContractEntryPoint,
)
from protostar.profiler.contract_profiler import Function, RuntimeProfile, Instruction
from dataclasses import replace
from protostar.profiler.transaction_profiler import build_global_functions, build_global_instructions, get_instruction_id_offsets, translate_callstack

from protostar.starknet.cheatable_execute_entry_point import ContractProfile

profile = RuntimeProfile(
    [Function("f1", "d", 1), Function("f2", "d", 2)], [], [], [], []
)




@pytest.mark.parametrize(
    "samples,result",
    [
        (
            [
                ContractProfile(["a", "b"], ContractEntryPoint(0, 0), replace(profile)),
                ContractProfile(["c", "b"], ContractEntryPoint(0, 0), replace(profile)),
            ],
            {
                "b.f1": profile.functions[0],
                "b.f2": profile.functions[1],
            },
        ),
        ([], {}),
        (
            [
                ContractProfile(["a", "b"], ContractEntryPoint(0, 0), replace(profile)),
                ContractProfile(["a", "c"], ContractEntryPoint(0, 0), replace(profile)),
            ],
            {
                "b.f1": profile.functions[0],
                "b.f2": profile.functions[1],
                "c.f1": profile.functions[0],
                "c.f2": profile.functions[1],
            },
        ),
    ],
)
def test_build_global_functions(samples, result):
    assert build_global_functions(samples) == result



funct = Function("z", "z", 0)
ep = ContractEntryPoint(0,0)
@pytest.mark.parametrize(
    "samples,result",
    [
        (
            [
                ContractProfile(["a"], ep, RuntimeProfile([], [Instruction(1000, 0, replace(funct), 0), Instruction(100, 0, replace(funct), 0)] , [], [], [])),
                ContractProfile(["b"], ep, RuntimeProfile([], [Instruction(150, 0, replace(funct), 0), Instruction(100, 0, replace(funct), 0)] , [], [], [])),
                ContractProfile(["c"], ep, RuntimeProfile([], [Instruction(10, 0, replace(funct), 0), Instruction(100, 0, replace(funct), 0)] , [], [], [])),
            ],
            {
                "a": 0,
                "b": 1001,
                "c": 1152,
            },
        ),
        ([], {}),
    ],
)
def test_get_instructions_id_offsets(samples, result):
    assert get_instruction_id_offsets(samples) == result



glob_func = {
        "a.A" :Function("A", "z", 0),
        "a.B" :Function("B", "z", 0),
        "b.C" :Function("C", "z", 0),

}

ep = ContractEntryPoint(0,0)
@pytest.mark.parametrize(
    "samples,result",
    [
        (
            [
                ContractProfile(["a"], ep, RuntimeProfile([], [Instruction(1000, 0, glob_func["a.A"], 0)] , [], [], [])),
                ContractProfile(["b"], ep, RuntimeProfile([], [Instruction(150, 0, glob_func["b.C"], 0), Instruction(100, 0, glob_func["b.C"], 0)] , [], [], [])),
                ContractProfile(["a"], ep, RuntimeProfile([], [Instruction(1000, 0, glob_func["a.A"], 0), Instruction(100, 0, glob_func["a.B"], 0)] , [], [], [])),
            ],
            {
                ("a.A", 1000): Instruction(1000, 0, glob_func["a.A"], 0), 
                ("b.C", 150): Instruction(1151, 0, glob_func["b.C"], 0), 
                ("b.C", 100): Instruction(1101, 0, glob_func["b.C"], 0), 
                ("a.B", 100): Instruction(100, 0, glob_func["a.B"], 0), 
            },
        ),
        ([], {}),
    ],
)
def test_build_global_instructions(samples, result):
    assert build_global_instructions(glob_func, samples) == result


@pytest.mark.parametrize("current_contract,in_instructions,callstack,result", [
    (
        "b", 
        {
            ("a.A", 1000): Instruction(1000, 0, glob_func["a.A"], 0), 
            ("b.C", 150): Instruction(1151, 0, glob_func["b.C"], 0), 
            ("b.C", 100): Instruction(1101, 0, glob_func["b.C"], 0), 
            ("a.B", 100): Instruction(100, 0, glob_func["a.B"], 0), 
        },
        [Instruction(150, 0, glob_func["b.C"], 0), Instruction(100, 0, glob_func["b.C"], 0)],
        [Instruction(1151, 0, glob_func["b.C"], 0), Instruction(1101, 0, glob_func["b.C"], 0)],
    ),
    (
        "a", 
        {
            ("a.A", 1000): Instruction(1000, 0, glob_func["a.A"], 0), 
            ("b.C", 150): Instruction(1151, 0, glob_func["b.C"], 0), 
            ("b.C", 100): Instruction(1101, 0, glob_func["b.C"], 0), 
            ("a.B", 100): Instruction(100, 0, glob_func["a.B"], 0), 
        },
        [Instruction(1000, 0, glob_func["a.A"], 0), Instruction(100, 0, glob_func["a.B"], 0)],
        [Instruction(1000, 0, glob_func["a.A"], 0), Instruction(100, 0, glob_func["a.B"], 0)],
    ),
    ("z", {}, [], [])
])
def test_translate_callstack(current_contract, in_instructions, callstack, result):
    assert translate_callstack(current_contract, in_instructions, callstack) == result


