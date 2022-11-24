from dataclasses import dataclass, replace
import itertools
from typing import TYPE_CHECKING, Tuple

from protostar.profiler.contract_profiler import (
    Instruction,
    Function,
    Sample,
)


if TYPE_CHECKING:
    from protostar.starknet.cheatable_execute_entry_point import (
        ContractProfile,
        ContractFilename,
    )

Address = int
GlobalFunctionID = str
GlobalInstructionID = str

GlobalFunction = Function
GlobalInstruction = Instruction


@dataclass(frozen=True)
class TransactionProfile:
    functions: list[GlobalFunction]
    instructions: list[GlobalInstruction]
    samples: dict[str, list[Sample]]


def translate_samples(
    contract_samples: list["ContractProfile"],
    global_instructions: dict[Tuple[GlobalFunctionID, int], Instruction],
    name: str,
) -> list[Sample]:
    samples_new: list[Sample] = []
    for smp in contract_samples[-1].profile.samples[name]:
        current_contract = contract_samples[-1].contract_callstack[-1]
        samples_new.append(
            Sample(
                value=smp.value,
                callstack=translate_callstack(
                    current_contract, global_instructions, smp.callstack
                ),
            )
        )

    # We build a tree from callstacks
    max_clst_len = max(len(s.contract_callstack) for s in contract_samples)
    callstacks_from_upper_layer = translate_callstacks(
        contract_samples[-1].contract_callstack[-1],
        global_instructions,
        contract_samples[-1].profile.contract_call_callstacks,
    )
    for i in range(2, max_clst_len + 1):
        samples_in_layer = [
            s for s in contract_samples if len(s.contract_callstack) == i
        ]
        new_callstacks_from_upper_layer: list[list[list[Instruction]]] = []
        for upper, runtime_sample in zip(callstacks_from_upper_layer, samples_in_layer):
            current_contract = runtime_sample.contract_callstack[-1]
            for smp in runtime_sample.profile.samples[name]:
                samples_new.append(
                    Sample(
                        value=smp.value,
                        callstack=translate_callstack(
                            current_contract, global_instructions, smp.callstack
                        )
                        + upper,
                    )
                )
            translated_callstacks = translate_callstacks(
                current_contract,
                global_instructions,
                runtime_sample.profile.contract_call_callstacks,
            )
            new_callstacks_from_upper_layer.append(
                [c + upper for c in translated_callstacks]
            )
        callstacks_from_upper_layer = list(
            itertools.chain(*new_callstacks_from_upper_layer)
        )
    return samples_new


# TODO(maksymiliandemitraszek): Enable it again
def merge_profiles(contract_samples: list["ContractProfile"]) -> TransactionProfile:
    global_functions = build_global_functions(contract_samples)
    global_instructions = build_global_instructions(global_functions, contract_samples)
    sample_names = {
        name for cs in contract_samples for name in cs.profile.samples.keys()
    }

    samples = {
        name: translate_samples(contract_samples, global_instructions, name)
        for name in sample_names
    }

    return TransactionProfile(
        functions=list(global_functions.values()),
        instructions=list(global_instructions.values()),
        samples=samples,
    )


def build_global_functions(
    samples: list["ContractProfile"],
) -> dict[GlobalFunctionID, GlobalFunction]:
    global_functions: dict[GlobalFunctionID, GlobalFunction] = {}
    for sample in samples:
        function_id_prefix = sample.contract_callstack[-1] + "."
        for func in sample.profile.functions:
            global_name = function_id_prefix + func.id
            global_functions[global_name] = replace(func, id=global_name)
    return global_functions


def build_global_instructions(
    global_functions: dict[GlobalFunctionID, Function], samples: list["ContractProfile"]
) -> dict[Tuple[GlobalFunctionID, int], Instruction]:
    in_instructions: dict[Tuple[GlobalFunctionID, int], Instruction] = {}
    contract_id_offsets = get_instruction_id_offsets(samples)
    for sample in samples:
        function_id_prefix = sample.contract_callstack[-1] + "."
        current_contract = sample.contract_callstack[-1]
        for instr in sample.profile.instructions:
            global_instruction_id = instr.id + contract_id_offsets[current_contract]
            global_function_id = function_id_prefix + instr.function.id
            in_instructions[(global_function_id, instr.id)] = replace(
                instr,
                id=global_instruction_id,
                function=global_functions[global_function_id],
            )
    return in_instructions


def get_instruction_id_offsets(
    samples: list["ContractProfile"],
) -> dict["ContractFilename", int]:
    contract_id_offsets: dict["ContractFilename", int] = {}
    for sample in samples:
        current_contract = sample.contract_callstack[-1]
        previous = contract_id_offsets.get(current_contract, 0)
        new = max(instr.id for instr in sample.profile.instructions) + 1
        contract_id_offsets[current_contract] = max(new, previous)
    accumulator = 0
    for contract_name, size in contract_id_offsets.items():
        contract_id_offsets[contract_name] = accumulator
        accumulator += size
    return contract_id_offsets


def translate_callstacks(
    current_contract: "ContractFilename",
    global_instructions: dict[Tuple[GlobalFunctionID, int], Instruction],
    callstacks: list[list[Instruction]],
) -> list[list[Instruction]]:
    translated: list[list[Instruction]] = []
    for call in callstacks:
        translated.append(
            translate_callstack(current_contract, global_instructions, call)
        )
    return translated


def translate_callstack(
    current_contract: "ContractFilename",
    in_instructions: dict[Tuple[GlobalFunctionID, int], Instruction],
    callstack: list[Instruction],
) -> list[Instruction]:
    new_callstack: list[Instruction] = []
    for instr in callstack:
        prefix = current_contract + "."
        new_callstack.append(in_instructions[(prefix + instr.function.id, instr.id)])
    return new_callstack
