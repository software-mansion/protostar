# pylint: disable=invalid-name
from collections import defaultdict
from dataclasses import dataclass
import functools
import math
from re import A, U
from typing import TYPE_CHECKING, Callable, List, Dict, Set, Tuple, cast
from xxlimited import new

from starkware.cairo.lang.vm.memory_dict import MemoryDict
from starkware.cairo.lang.compiler.identifier_definition import LabelDefinition
from starkware.cairo.lang.tracer.tracer_data import TracerData
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.compiler.identifier_definition import (
    IdentifierDefinition,
)
from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from protostar.profiler.pprof import serialize, to_protobuf
if TYPE_CHECKING:
    from protostar.starknet.cheatable_execute_entry_point import ContractProfile

Address = int
StringID = int
FunctionID = int

import random
def unique_id():
    return random.randint(0, 10000000000)

@dataclass()
class Function:
    id: str
    filename: str
    start_line: int


@dataclass()
class Instruction:
    id: int
    pc: Address
    function: Function
    line: int


@dataclass(frozen=True)
class Sample:
    value: int
    callstack: List[Instruction]


@dataclass(frozen=True)
class SampleType:
    type: str
    unit: str


@dataclass(frozen=True)
class RuntimeProfile:
    functions: List[Function]
    instructions: List[Instruction]
    sample_types: List[SampleType]
    step_samples: List[Sample]
    memhole_samples: List[Sample]
    contract_call_callstacks: List[List[Instruction]]

class ProfilerContext:
    def __init__(self, initial_fp: Address, memory: MemoryDict):
        # self._string_table: Dict[str, StringID] = {}
        # self.string_list: List[str] = []
        self.initial_fp = initial_fp
        self.memory = memory
        # self.string_id("")

    # def string_id(self, value: str) -> StringID:
    #     assert isinstance(value, str)
    #     if value in self._string_table:
    #         return self._string_table[value]
    #     self._string_table[value] = len(self._string_table)
    #     self.string_list.append(value)
    #     return self._string_table[value]

    def sample_types(self):
        return [
            SampleType("steps count", "steps"),
            SampleType("memory holes", "mem holes"),
        ]

    def get_call_stack(self, fp: Address, pc: Address) -> List[Address]:
        """
        Retrieves the call stack pc values given current fp and pc.
        """
        frame_pcs = [pc]
        while fp > self.initial_fp:
            fp_val = self.memory[fp - 2]
            pc_val = self.memory[fp - 1]
            assert isinstance(fp_val, Address)
            assert isinstance(pc_val, Address)
            fp, pc = fp_val, pc_val
            frame_pcs.append(pc)
        return frame_pcs

    def main_function(self):
        return Function(
            id="__main__",
            filename="<dummy_filename>",
            start_line=0,
        )

    def build_function_list(self, tracer_data: TracerData) -> List[Function]:
        identifiers_dict = tracer_data.program.identifiers.as_dict()
        assert tracer_data.program.debug_info is not None
        is_label: Callable[[IdentifierDefinition], bool] = lambda ident: isinstance(
            ident, LabelDefinition
        )
        labels = {
            name: cast(LabelDefinition, ident)
            for name, ident in identifiers_dict.items()
            if is_label(ident)
        }

        instruction_locations = tracer_data.program.debug_info.instruction_locations
        functions_locations = {
            str(name): instruction_locations[ident.pc] for name, ident in labels.items()
        }

        assert all(
            location.inst.input_file.filename is not None
            for location in functions_locations.values()
        )
        functions: List[Function] = []
        for name, location in functions_locations.items():
            assert location.inst.input_file.filename
            functions.append(
                Function(
                    id=name,
                    filename=location.inst.input_file.filename,
                    start_line=location.inst.start_line,
                )
            )

        return functions + [self.main_function()]

    def find_function(self, functions: List[Function], name: str) -> Function:
        for func in functions:
            if func.id == name:
                return func
        assert False

    def build_instructions_map(
        self, functions: List[Function], tracer_data: TracerData
    ) -> List[Instruction]:
        """
        Retrieves the id of a location. Adds to the table if not already present.
        """
        assert tracer_data.program.debug_info
        pc_to_locations = {
            tracer_data.get_pc_from_offset(pc_offset): inst_location
            for pc_offset, inst_location in tracer_data.program.debug_info.instruction_locations.items()
        }
        instructions = [
            Instruction(
                id=pc + 1,
                pc=pc,
                function=self.find_function(
                    functions, str(location.accessible_scopes[-1])
                ),
                line=location.inst.start_line,
            )
            for pc, location in pc_to_locations.items()
        ]
        return instructions

    @staticmethod
    def find_instruction(instructions: List[Instruction], pc: Address) -> Instruction:
        for instr in instructions:
            if instr.pc == pc:
                return instr
        assert False

    def build_call_callstacks(
        self, instructions: List[Instruction], tracer_data: TracerData
    ) -> List:
        callstacks = []
        stack_len = -1
        for trace_entry in tracer_data.trace:
            callstack = self.get_call_stack(fp=trace_entry.fp, pc=trace_entry.pc)
            instr_callstack = [
                self.find_instruction(instructions, pc) for pc in callstack
            ]

            # Wait until stack pops
            if len(instr_callstack) <= stack_len:
                continue
            stack_len = -1

            top = instr_callstack[0]
            # TODO make it based on builtin memory access
            if top.function.id == "starkware.starknet.common.syscalls.call_contract":
                stack_len = len(instr_callstack)
                callstacks.append(instr_callstack)
        return callstacks

    def build_step_samples(
        self, instructions: List[Instruction], tracer_data: TracerData
    ):
        step_samples = []
        for trace_entry in tracer_data.trace:
            callstack = self.get_call_stack(fp=trace_entry.fp, pc=trace_entry.pc)
            instr_callstack = [
                self.find_instruction(instructions, pc) for pc in callstack
            ]
            step_samples.append((Sample(value=1, callstack=instr_callstack)))
        return step_samples

    @staticmethod
    def blame_pc(max_accesses, hole_address) -> int:
        min_addr_after = math.inf
        blamed_pc = -1
        for address, pc in max_accesses.items():
            if address > hole_address:
                if address < min_addr_after:
                    min_addr_after = address
                    blamed_pc = pc
        assert min_addr_after > -1
        return blamed_pc

    @staticmethod
    def not_accessed(
        accessed_addresses, segments: MemorySegmentManager, segment_offsets
    ) -> Set[Address]:
        not_accessed_addr: Set[Address] = set()
        for idx in range(segments.n_segments):
            size = segments.get_segment_size(segment_index=idx)
            not_accessed_addr |= {segment_offsets[idx] + i for i in range(size)}

        accessed_offsets_sets = defaultdict(set)
        for addr in accessed_addresses:
            index, offset = addr.segment_index, addr.offset
            accessed_offsets_sets[index].add(offset)

        for segment_index, accessed_offsets_set in accessed_offsets_sets.items():
            for off in accessed_offsets_set:
                try:
                    idx = segment_offsets[segment_index] + off
                    not_accessed_addr.remove(idx)
                except KeyError:
                    pass
        return not_accessed_addr

    def build_memhole_samples(
        self,
        instructions: List[Instruction],
        tracer_data: TracerData,
        accessed_memory,
        segments: MemorySegmentManager,
        segment_offsets,
    ) -> List[Sample]:
        accessed_by = {}
        pc_to_callstack = {}
        for trace_entry, mem_acc in zip(tracer_data.trace, tracer_data.memory_accesses):
            frame_pcs = self.get_call_stack(fp=trace_entry.fp, pc=trace_entry.pc)
            for key in ["dst", "op0", "op1"]:
                accessed_by[mem_acc[key]] = trace_entry.pc
                pc_to_callstack[trace_entry.pc] = frame_pcs

        blame_pc = functools.partial(self.blame_pc, accessed_by)

        samples: List[Sample] = []
        not_acc = self.not_accessed(accessed_memory, segments, segment_offsets)
        for address in not_acc:
            pc = blame_pc(address)
            callstack = [
                self.find_instruction(instructions, frame_pc)
                for frame_pc in pc_to_callstack[pc]
            ]
            samples.append(Sample(value=1, callstack=callstack))
        return samples


def build_profile(
    tracer_data: TracerData,
    segments: MemorySegmentManager,
    segment_offsets: Dict[int, int],
    accessed_memory: Set[RelocatableValue],
) -> RuntimeProfile:
    builder = ProfilerContext(
        initial_fp=tracer_data.trace[0].fp, memory=tracer_data.memory
    )
    function_list = builder.build_function_list(tracer_data)
    instructions_list = builder.build_instructions_map(function_list, tracer_data)
    step_samples = builder.build_step_samples(instructions_list, tracer_data)
    memhole_samples = builder.build_memhole_samples(
        instructions_list, tracer_data, accessed_memory, segments, segment_offsets
    )
    sample_types = builder.sample_types()
    callstacks_syscall = builder.build_call_callstacks(instructions_list, tracer_data)
    profile = RuntimeProfile(
        sample_types=sample_types,
        functions=function_list,
        instructions=instructions_list,
        step_samples=step_samples,
        memhole_samples=memhole_samples,
        contract_call_callstacks=callstacks_syscall,
    )
    return profile


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
        new_callstack.append(
            in_instructions[(instr.function.id, instr.id)]
        )
    return new_callstack

def merge_profiles(samples: List["ContractProfile"]):
    sample_types = samples[0].profile.sample_types
    step_samples = []
    memhole_samples = []

    for sample in samples:
        for func in sample.profile.functions:
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

    
    for sample in samples:
        current_contract = sample.callstack[-1]
        for smp in sample.profile.step_samples:
            step_samples.append(Sample(
                value=smp.value,
                callstack=translate_callstack(in_instructions, smp.callstack)
            ))

    for sample in samples:
        current_contract = sample.callstack[-1]
        for smp in sample.profile.memhole_samples:
            memhole_samples.append(Sample(
                value=smp.value,
                callstack=translate_callstack(in_instructions, smp.callstack)
            ))

    return RuntimeProfile(
        functions=list(in_functions.values()),
        instructions=list(in_instructions.values()),
        sample_types=sample_types,
        step_samples=step_samples,
        memhole_samples=memhole_samples,
        contract_call_callstacks=[]
    )
