from collections import defaultdict
from dataclasses import dataclass
import gzip
import time
from typing import Callable, List, Dict, Optional, Tuple

from starkware.cairo.lang.compiler.debug_info import InstructionLocation
from starkware.cairo.lang.compiler.identifier_definition import LabelDefinition
from starkware.cairo.lang.tracer.third_party.profile_pb2 import Profile
from starkware.cairo.lang.tracer.tracer_data import TracerData
from starkware.cairo.lang.vm.trace_entry import TraceEntry
from starkware.cairo.lang.compiler.identifier_definition import (
    IdentifierDefinition,
)

from starkware.cairo.lang.compiler.encode import decode_instruction

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
    memhole_samples: List[Tuple[Instruction, Sample]]


class ProfilerContext:
    def __init__(self, initial_fp: Address, memory):
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
            SampleType(
                self.string_id("steps count"),
                self.string_id("steps")
            ),
            SampleType(
                self.string_id("memory holes"),
                self.string_id("mem holes")
            ),
        ]

    def get_call_stack(self, fp, pc) -> List[Address]:
        """
        Retrieves the call stack pc values given current fp and pc.       
        """
        frame_pcs = [pc]
        while fp > self.initial_fp:
            fp, pc = self.memory[fp - 2], self.memory[fp - 1]
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

        is_function: Callable[[IdentifierDefinition], bool] = lambda ident: isinstance(ident, LabelDefinition)

        functions_locations = {str(name): tracer_data.program.debug_info.instruction_locations[ident.pc] 
            for name, ident in identifiers_dict.items() if is_function(ident)
        }

        assert all(location.inst.input_file.filename is not None for location in functions_locations.values())

        functions = [
            Function(
                id=self.string_id(name),
                filename=self.string_id(location.inst.input_file.filename),
                start_line=location.inst.start_line 
            )
            for name, location in functions_locations.items()
        ]
        return functions + [self.main_function()]

    def find_function(self, functions: List[Function], name: str) -> Function:
        for func in functions:
            if func.id == self.string_id(name):
                return func
        assert False

    def build_instructions_map(self, functions: List[Function], tracer_data: TracerData) -> List[Instruction]:
        """
        Retrieves the id of a location. Adds to the table if not already present.
        """
        pc_to_locations = {
            tracer_data.get_pc_from_offset(pc_offset): inst_location for pc_offset, inst_location in tracer_data.program.debug_info.instruction_locations.items()
        }
        instructions = [
            Instruction(
                id=pc+1,
                pc=pc,
                function=self.find_function(functions, str(location.accessible_scopes[-1])),
                line=location.inst.start_line
            )
            for pc, location in pc_to_locations.items()
        ]
        return instructions
    
    def find_instruction(self, instructions: List[Instruction], pc: Address) -> Instruction:
        for instr in instructions:
            if instr.pc == pc:
                return instr
        assert False
        
    def build_step_samples(self, instructions: Dict[Instruction, Function], tracer_data: TracerData):
        step_samples = []
        for trace_entry in tracer_data.trace:
            callstack = self.get_call_stack(fp=trace_entry.fp, pc=trace_entry.pc)
            instr_callstack = [self.find_instruction(instructions, pc) for pc in callstack]
            step_samples.append((Sample(value=1, callstack=instr_callstack)))
        return step_samples

    

def build_profile(tracer_data: TracerData) -> RuntimeProfile:
    builder = ProfilerContext(initial_fp=tracer_data.trace[0].fp, memory=tracer_data.memory)
    function_list = builder.build_function_list(tracer_data)
    instructions_map = builder.build_instructions_map(function_list, tracer_data)
    step_samples = builder.build_step_samples(instructions_map, tracer_data)
    sample_types = builder.sample_types()
    profile = RuntimeProfile(
        strings=builder.string_list,
        sample_types=sample_types,
        functions=function_list,
        instructions=instructions_map,
        step_samples=step_samples,
        memhole_samples=[]
    )
    return profile




def to_protobuf(profile_obj: RuntimeProfile) -> Profile:
    profile = Profile()

    profile.time_nanos = int(time.time() * 10**9)

    for sample_type in profile_obj.sample_types:
        sample_tp = profile.sample_type.add()
        sample_tp.type = sample_type.type
        sample_tp.unit = sample_type.unit

    for val in profile_obj.strings:
        profile.string_table.append(val)
    
    for function in profile_obj.functions:
        func = profile.function.add()
        func.id = function.id
        func.system_name = func.name = function.id
        func.filename = function.filename
        func.start_line = function.start_line

    for inst in profile_obj.instructions:
        location = profile.location.add()
        location.id = inst.id
        location.address = inst.pc
        location.is_folded = False
        line = location.line.add()
        line.function_id = inst.function.id
        line.line = inst.line
    
    for smp in profile_obj.step_samples:
        sample = profile.sample.add()
        for instr in smp.callstack:
            sample.location_id.append(instr.id)
        sample.value.append(smp.value)
        sample.value.append(0)
    return profile
    
def serialize(profile: Profile) -> bytes:
    data = profile.SerializeToString()
    return gzip.compress(data)


def profile_from_tracer_data(tracer_data: TracerData, runner):
    profile = build_profile(tracer_data)
    protobuf = to_protobuf(profile)
    return serialize(protobuf)

class ProfileBuilder:
    """
    Builds a profile protobuf from trace samples of a specific run.
    The Profile protobuf uses ids to reference objects, so we maintain id dictionaries internally.
    For example: instead of writing string in objects, we always pass an id to the string table.
    See profile.proto for more information.

    initial_fp - First fp in the program.
    memory - memory object of the run.
    """

    def __init__(self, initial_fp, memory):
        self.max_accesses = {}
        self.pc_to_callstack = {}
        self._profile = Profile()
        # A map from a string to its id in the string table.
        self._string_to_id = {}
        # First string in the table must be ''.
        self.string_id("")
        # A map from a function name to its id in the function table.
        # Current implementation uses the string id of the function name as a function id.
        self._func_name_to_id = {}
        # A map from a pc value to the location id at that pc.
        self._pc_to_location_id = {}

        self.ap_to_fp = {}

        # frame pointer of the top function
        self.initial_fp = initial_fp
        self.memory = memory

        # Global fields.
        sample_type = self._profile.sample_type.add()
        sample_type.type = self.string_id("steps count")
        sample_type.unit = self.string_id("steps")
        self._profile.time_nanos = int(time.time() * 10**9)

        sample_type_memory = self._profile.sample_type.add()
        sample_type_memory.type = self.string_id("builtin runs")
        sample_type_memory.unit = self.string_id("builtins")

        sample_type_memory = self._profile.sample_type.add()
        sample_type_memory.type = self.string_id("memory holes")
        sample_type_memory.unit = self.string_id("mem holes")


        # Main function.
        self._func_name_to_id["__main__"] = self.string_id("__main__")
        main_func = self._profile.function.add()
        main_func.id = self.string_id("__main__")
        main_func.system_name = main_func.name = self.string_id("<dummy>")
        main_func.filename = self.string_id("<dummy_filename>")
        main_func.start_line = 0

    def string_id(self, s: str) -> int:
        """
        Retrieves the id of a string in the string table. Adds to the table if not already present.
        """
        if s not in self._string_to_id:
            self._string_to_id[s] = len(self._string_to_id)
            self._profile.string_table.append(s)
        return self._string_to_id[s]

    def function_id(self, name: str, inst_location: InstructionLocation) -> int:
        """
        Retrieves the id of a function. Adds to the table if not already present.
        """
        func_id = self.string_id(name)
        if name not in self._func_name_to_id:
            self._func_name_to_id[name] = func_id
            func = self._profile.function.add()
            func.id = func_id
            func.system_name = func.name = self.string_id(name)
            assert inst_location.inst.input_file.filename is not None
            func.filename = self.string_id(inst_location.inst.input_file.filename)
            func.start_line = inst_location.inst.start_line
        return func_id

    def location_id(self, pc, inst_location: InstructionLocation) -> int:
        """
        Retrieves the id of a location. Adds to the table if not already present.
        """
        if pc not in self._pc_to_location_id:
            self._pc_to_location_id[pc] = pc + 1
            location = self._profile.location.add()
            location.id = pc + 1
            location.address = pc
            location.is_folded = False

            line = location.line.add()
            line.function_id = self._func_name_to_id[str(inst_location.accessible_scopes[-1])]
            line.line = inst_location.inst.start_line
        return self._pc_to_location_id[pc]

    def get_call_stack(self, fp, pc):
        """
        Retrieves the call stack pc values given current fp and pc.       
        """
        frame_pcs = [pc]
        while fp > self.initial_fp:
            fp, pc = self.memory[fp - 2], self.memory[fp - 1]
            frame_pcs.append(pc)
        return frame_pcs

    def add_sample(self, trace_entry: TraceEntry):
        """
        Adds a sample to the profile.
        """
        frame_pcs = self.get_call_stack(fp=trace_entry.fp, pc=trace_entry.pc)
        # print(trace_entry.fp, trace_entry.pc, frame_pcs)
        sample = self._profile.sample.add()
        for pc in frame_pcs:
            sample.location_id.append(self._pc_to_location_id[pc])
        sample.value.append(1)  # 1 step.
        sample.value.append(0)  # 1 step.
        # sample.value.append(0)  # 1 step.

        # sample.value.append(int(is_builtin(trace_entry)))
        # sample.value.append(1)  # 1 step.
    
    def memholes(self, tracer_data: TracerData):
        accessed_by = {}
        for trace_entry, mem_acc in zip(tracer_data.trace, tracer_data.memory_accesses):
            frame_pcs = self.get_call_stack(fp=trace_entry.fp, pc=trace_entry.pc)
            for key in ["dst", "op0", "op1"]:
                accessed_by[mem_acc[key]] = trace_entry.pc
                self.pc_to_callstack[trace_entry.pc] = frame_pcs
        self.max_accesses = accessed_by
             
    def add_memholes_samples(self, accessed_memory, segments, runner):
        """
        Adds a sample to the profile.
        """
        not_acc = self.not_accessed(accessed_memory, segments, runner)
        # l = 0
        for address in not_acc:
            sample = self._profile.sample.add()
            pc = self.blame_pc(address)
            for st_el in self.pc_to_callstack[pc]:
                sample.location_id.append(self._pc_to_location_id[st_el])
        
            sample.value.append(0)  # 1 step.
            sample.value.append(0)  # 1 step.
            sample.value.append(1)  # 1 step.

                

    def blame_pc(self, hole_address) -> int:
        min_addr_after = 100000000000000000000
        blamed_pc = -1
        for address, pc in self.max_accesses.items():
            if address > hole_address:
                if address < min_addr_after:
                    min_addr_after = address
                    blamed_pc = pc
        assert min_addr_after > -1
        return blamed_pc 

    def not_accessed(self, accessed_addresses, segments, runner) -> List[int]:
        size = segments.get_segment_size(segment_index=1)
        not_accessed_addr = set([runner.segment_offsets[1] + i for i in range(size)])

        accessed_offsets_sets = defaultdict(set)
        for addr in accessed_addresses:
            index, offset = addr.segment_index, addr.offset
            accessed_offsets_sets[index].add(offset)

        for off in list(accessed_offsets_sets[1]):
            try:
                idx = runner.segment_offsets[1] + off
                not_accessed_addr.remove(idx)
            except KeyError:
                pass
        return not_accessed_addr

    def dump(self) -> bytes:
        """
        Dumps the current profile. Returns the serialized bytes.
        """
        data = self._profile.SerializeToString()
        return gzip.compress(data)



# def profile_from_tracer_data(tracer_data: TracerData, runner):
#     """
#     Computes the profile file data given a TracerData instance.
#     Can be read by pprof.
#     """
#     breakpoint()
#     builder = ProfileBuilder(initial_fp=tracer_data.trace[0].fp, memory=tracer_data.memory)

#     # for i in range(max(tracer_data.memory.data.keys()) + 1):
#     #     if i in tracer_data.memory:
#     #         print(f"{i} : {tracer_data.memory[i]}") 
#     #     else:
#     #         print(f"{i} : ----------") 

#     # Functions.
#     identifiers_dict = tracer_data.program.identifiers.as_dict()
#     assert tracer_data.program.debug_info is not None
#     for name, ident in identifiers_dict.items():
#         if not isinstance(ident, LabelDefinition):
#             continue
#         builder.function_id(
#             name=str(name),
#             inst_location=tracer_data.program.debug_info.instruction_locations[ident.pc],
#         )

#     # Locations.
#     for pc_offset, inst_location in tracer_data.program.debug_info.instruction_locations.items():
#         # print(tracer_data.get_pc_from_offset(pc_offset), inst_location)
#         builder.location_id(
#             pc=tracer_data.get_pc_from_offset(pc_offset), inst_location=inst_location
#         )
#     # Samples.
#     for trace_entry in tracer_data.trace:
#         builder.add_sample(trace_entry)

#     # for trace_entry in tracer_data.trace:
#     builder.memholes(tracer_data)
#     # builder.add_accesses_aps(tracer_data.trace)
#     # breakpoint()
#     builder.add_memholes_samples(runner.accessed_addresses, runner.segments, runner)


#     return builder.dump()