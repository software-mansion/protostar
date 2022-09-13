# pylint: disable=invalid-name
from collections import defaultdict
from dataclasses import dataclass
import functools
import math
from typing import Callable, List, Dict, Set, cast

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

Address = int
StringID = int
FunctionID = int


@dataclass(frozen=True)
class Function:
    id: StringID
    filename: StringID
    start_line: int


@dataclass(frozen=True)
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
    type: StringID
    unit: StringID


@dataclass(frozen=True)
class RuntimeProfile:
    strings: List[str]
    functions: List[Function]
    instructions: List[Instruction]
    sample_types: List[SampleType]
    step_samples: List[Sample]
    memhole_samples: List[Sample]


class ProfilerContext:
    def __init__(self, initial_fp: Address, memory: MemoryDict):
        self._string_table: Dict[str, StringID] = {}
        self.string_list: List[str] = []
        self.initial_fp = initial_fp
        self.memory = memory
        self.string_id("")

    def string_id(self, value: str) -> StringID:
        assert isinstance(value, str)
        if value in self._string_table:
            return self._string_table[value]
        self._string_table[value] = len(self._string_table)
        self.string_list.append(value)
        return self._string_table[value]

    def sample_types(self):
        return [
            SampleType(self.string_id("steps count"), self.string_id("steps")),
            SampleType(self.string_id("memory holes"), self.string_id("mem holes")),
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
            id=self.string_id("__main__"),
            filename=self.string_id("<dummy_filename>"),
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
                    id=self.string_id(name),
                    filename=self.string_id(location.inst.input_file.filename),
                    start_line=location.inst.start_line,
                )
            )

        return functions + [self.main_function()]

    def find_function(self, functions: List[Function], name: str) -> Function:
        for func in functions:
            if func.id == self.string_id(name):
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
    profile = RuntimeProfile(
        strings=builder.string_list,
        sample_types=sample_types,
        functions=function_list,
        instructions=instructions_list,
        step_samples=step_samples,
        memhole_samples=memhole_samples,
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
