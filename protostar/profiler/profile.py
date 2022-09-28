# pylint: disable=invalid-name
import itertools
import random
from typing import TYPE_CHECKING, List, Dict, Tuple

from starkware.cairo.lang.tracer.tracer_data import TracerData
from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from protostar.profiler.pprof import serialize, to_protobuf
from protostar.profiler.contract_profiler import (
    Instruction,
    build_profile,
    Function,
    Sample,
    RuntimeProfile,
)


if TYPE_CHECKING:
    from protostar.starknet.cheatable_execute_entry_point import ContractProfile

Address = int
StringID = int
FunctionID = int


def unique_id():
    return random.randint(0, 10000000000)


def profile_from_tracer_data(tracer_data: TracerData, runner: CairoFunctionRunner):
    assert runner.accessed_addresses
    assert runner.segment_offsets
    profile = build_profile(
        tracer_data, runner.segments, runner.segment_offsets, runner.accessed_addresses
    )

    protobuf = to_protobuf(profile)
    return serialize(protobuf)


def translate_callstack(in_instructions, callstack: List[Instruction]):
    new_callstack = []
    for instr in callstack:
        new_callstack.append(in_instructions[(instr.function.id, instr.id)])
    return new_callstack


# TODO(maksymiliandemitraszek): Enable it again
# pylint: disable=too-many-branches
def merge_profiles(samples: List["ContractProfile"]):
    step_samples = []
    memhole_samples = []

    for sample in samples:
        for func in sample.profile.functions:
            # TODO(maksymiliandemitraszek) test it against contracts with duplicate filenames
            func.id = sample.callstack[-1] + "." + func.id

    in_functions: Dict[str, Function] = {}
    for sample in samples:
        for func in sample.profile.functions:
            if func.id not in in_functions:
                in_functions[func.id] = func

    contract_id_offsets = {}
    in_instructions: Dict[Tuple[str, int], Instruction] = {}
    for sample in samples:
        current_contract = sample.callstack[-1]
        if current_contract not in contract_id_offsets:
            contract_id_offsets[current_contract] = unique_id()

        for instr in sample.profile.instructions:
            instr.id = instr.id + contract_id_offsets[current_contract]
            in_instructions[(instr.function.id, instr.id)] = instr

    for smp in samples[-1].profile.step_samples:
        step_samples.append(
            Sample(
                value=smp.value,
                callstack=translate_callstack(in_instructions, smp.callstack),
            )
        )

    # We build a tree from callstacks
    max_clst_len = max(len(s.callstack) for s in samples)
    callstacks_from_upper_layer = samples[-1].profile.contract_call_callstacks
    for i in range(2, max_clst_len + 1):
        samples_in_layer = [s for s in samples if len(s.callstack) == i]
        new_callstacks_from_upper_layer: List[List[List[Instruction]]] = []
        for upper, runtime_sample in zip(callstacks_from_upper_layer, samples_in_layer):
            for smp in runtime_sample.profile.step_samples:
                step_samples.append(
                    Sample(
                        value=smp.value,
                        callstack=translate_callstack(
                            in_instructions, smp.callstack + upper
                        ),
                    )
                )
            new_callstacks_from_upper_layer.append(
                [c + upper for c in runtime_sample.profile.contract_call_callstacks]
            )
        callstacks_from_upper_layer = list(
            itertools.chain(*new_callstacks_from_upper_layer)
        )

    for smp in samples[-1].profile.memhole_samples:
        memhole_samples.append(
            Sample(
                value=smp.value,
                callstack=translate_callstack(in_instructions, smp.callstack),
            )
        )

    # We build a tree from callstacks
    callstacks_from_upper_layer = samples[-1].profile.contract_call_callstacks
    for i in range(2, max_clst_len + 1):
        samples_in_layer = [s for s in samples if len(s.callstack) == i]
        new_callstacks_from_upper_layer: List[List[List[Instruction]]] = []
        for upper, runtime_sample in zip(callstacks_from_upper_layer, samples_in_layer):
            for smp in runtime_sample.profile.memhole_samples:
                memhole_samples.append(
                    Sample(
                        value=smp.value,
                        callstack=translate_callstack(
                            in_instructions, smp.callstack + upper
                        ),
                    )
                )
            new_callstacks_from_upper_layer.append(
                [c + upper for c in runtime_sample.profile.contract_call_callstacks]
            )
        callstacks_from_upper_layer = list(
            itertools.chain(*new_callstacks_from_upper_layer)
        )

    return RuntimeProfile(
        functions=list(in_functions.values()),
        instructions=list(in_instructions.values()),
        step_samples=step_samples,
        memhole_samples=memhole_samples,
        contract_call_callstacks=[],
    )
