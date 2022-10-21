# pylint: disable=invalid-name
from collections import UserDict, defaultdict
from dataclasses import dataclass
import math
from typing import cast

from starkware.cairo.lang.compiler.identifier_definition import LabelDefinition
from starkware.cairo.lang.tracer.tracer_data import TracerData
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager


Address = int
FunctionID = str


@dataclass(frozen=True)
class Function:
    """
    Represents a function in a contract
    """

    id: FunctionID
    """ Unique name of a function """

    filename: str
    """Source file of a function"""

    start_line: int
    """Number of line function starts in"""


@dataclass(frozen=True)
class Instruction:
    """
    Represents a instruction under certain pc in a contract
    """

    id: int
    """Unique id of a instruction"""

    pc: Address
    """Function from the instruction has been generated"""

    function: Function
    """Function from the instruction has been generated"""

    line: int
    """Line of code from which instruction has been generated"""


class Instructions(UserDict):
    @classmethod
    def from_list(cls, instructions: list[Instruction]):
        return cls({instr.pc: instr for instr in instructions})

    def get_by_address(self, pc: Address) -> Instruction:
        return cast(Instruction, self.data[pc])



@dataclass(frozen=True)
class Sample:
    """
    Sample of a resource
    """

    value: int
    """Value of a sample (for example 1 memory hole)"""

    callstack: list[Instruction]
    """
    Instruction callstack for the reported sample.
    Each instruction has an function assigned so it is easy to deduce the
    calltree of an functions (pprof format requires samples to be assigned to instruction not functions)
    """


@dataclass(frozen=True)
class RuntimeProfile:
    """
    Calculated profile of a single contract runtime. Can be merged into TransactionProfile.
    """

    functions: list[Function]
    instructions: list[Instruction]
    step_samples: list[Sample]
    memhole_samples: list[Sample]
    contract_call_callstacks: list[list[Instruction]]



class TracerDataManager(TracerData):
    def get_callstack(self, fp: Address, pc: Address) -> list[Address]:
        """
        func g() {
            0: ap += 1
            1: f()
            2: ret
        }

        func f() {
            10:    ap += 1
            11:    ap += 2 # <-- here calling get_callstack
            12:    ret
        }
        Returns: [11, 2]
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

    @property
    def initial_fp(self) -> Address:
        return self.trace[0].fp


def collect_contract_functions(tracer_data: TracerDataManager) -> list[Function]:
    identifiers_dict = tracer_data.program.identifiers.as_dict()
    assert tracer_data.program.debug_info is not None
    labels = {
        name: ident
        for name, ident in identifiers_dict.items()
        if isinstance(ident, LabelDefinition)
    }

    instruction_locations = tracer_data.program.debug_info.instruction_locations
    functions_locations = {
        str(name): instruction_locations[ident.pc] for name, ident in labels.items()
    }

    if not all(
        location.inst.input_file.filename is not None
        for location in functions_locations.values()
    ):
        raise ValueError("Input files should contain filenames")
    functions: list[Function] = []
    for name, location in functions_locations.items():
        assert location.inst.input_file.filename
        functions.append(
            Function(
                id=name,
                filename=location.inst.input_file.filename,
                start_line=location.inst.start_line,
            )
        )

    # TODO(maksymiliandemitraszek) check if this is necessary
    main_func = Function(
        id="__main__",
        filename="<dummy_filename>",
        start_line=0,
    )
    return functions + [main_func]


def find_function(functions: list[Function], function_id: str) -> Function:
    for func in functions:
        if func.id == function_id:
            return func
    assert False


def create_instruction_list(
    functions: list[Function], tracer_data: TracerDataManager
) -> list[Instruction]:
    """
    Builds a list of instructions in the contract and assigns them to functions they come from
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
            function=find_function(functions, str(location.accessible_scopes[-1])),
            line=location.inst.start_line,
        )
        for pc, location in pc_to_locations.items()
    ]
    return instructions


def find_instruction(instructions: dict[int, Instruction], pc: Address) -> Instruction:
    return instructions[pc]


def build_call_callstacks(
    instructions: Instructions, tracer_data: TracerDataManager
) -> list[list[Instruction]]:
    """
    Searches for the external contract calls, saves the function callstack of each call
    """
    callstacks: list[list[Instruction]] = []
    stack_len = math.inf
    for trace_entry in tracer_data.trace:
        callstack = tracer_data.get_callstack(fp=trace_entry.fp, pc=trace_entry.pc)
        instr_callstack = [instructions.get_by_address(pc) for pc in callstack]

        # Wait until call_contract pops from stack
        if len(instr_callstack) >= stack_len:
            continue
        stack_len = math.inf

        top = instr_callstack[0]
        # TODO make it based on builtin memory access
        if top.function.id == "starkware.starknet.common.syscalls.call_contract":
            stack_len = len(instr_callstack)
            callstacks.append(instr_callstack)
    return callstacks


def build_step_samples(
    instructions: Instructions, tracer_data: TracerDataManager
) -> list[Sample]:
    step_samples: list[Sample] = []
    for trace_entry in tracer_data.trace:
        callstack = tracer_data.get_callstack(fp=trace_entry.fp, pc=trace_entry.pc)
        instr_callstack = [instructions.get_by_address(pc) for pc in callstack]
        step_samples.append((Sample(value=1, callstack=instr_callstack)))
    return step_samples


def blame_pc(last_accesses: dict[Address, Address], hole_address: Address) -> int:
    """
    Decides under which pc is placed an intruction which is responsible for the memory hole

    Keyword arguments:
    last_accesses -- Address -> Pc of instruction which accessed the address last
    hole_address -- Address of the memory hole
    """
    assert hole_address not in last_accesses
    min_addr_after = math.inf
    blamed_pc = -1
    for address, pc in last_accesses.items():
        if address > hole_address:
            if address < min_addr_after:
                min_addr_after = address
                blamed_pc = pc
    assert blamed_pc > -1
    return blamed_pc


def get_not_accessed_addresses(
    accessed_memory: set[RelocatableValue],
    segments: MemorySegmentManager,
    segment_offsets: dict[int, int],
) -> set[Address]:
    not_accessed_addr: set[Address] = set()
    for idx in range(segments.n_segments):
        size = segments.get_segment_size(segment_index=idx)
        not_accessed_addr |= {segment_offsets[idx] + i for i in range(size)}

    accessed_offsets_sets: defaultdict[int, set[int]] = defaultdict(set)
    for addr in accessed_memory:
        index, offset = addr.segment_index, addr.offset
        accessed_offsets_sets[index].add(offset)

    for segment_index, accessed_offsets_set in accessed_offsets_sets.items():
        for off in accessed_offsets_set:
            try:
                idx: Address = segment_offsets[segment_index] + off
                not_accessed_addr.remove(idx)
            except KeyError:
                pass
    return not_accessed_addr


def build_memhole_samples(
    instructions: Instructions,
    tracer_data: TracerDataManager,
    accessed_memory: set[RelocatableValue],
    segments: MemorySegmentManager,
    segment_offsets,
) -> list[Sample]:
    # Address -> Pc of instruction which accessed the address last
    accessed_by: dict[Address, Address] = {}
    pc_to_callstack: dict[Address, list[Address]] = {}
    for trace_entry, mem_acc in zip(tracer_data.trace, tracer_data.memory_accesses):
        frame_pcs = tracer_data.get_callstack(fp=trace_entry.fp, pc=trace_entry.pc)
        addresses: list[Address] = [mem_acc[d] for d in ["dst", "op0", "op1"]]
        for addr in addresses:
            # Casting to Addres because adresses have been already relocated
            # TODO(maksymiliandemitraszek) check if that's correct
            accessed_by[addr] = cast(Address, trace_entry.pc)
            pc_to_callstack[trace_entry.pc] = frame_pcs

    samples: list[Sample] = []
    not_acc = get_not_accessed_addresses(accessed_memory, segments, segment_offsets)
    for address in not_acc:
        pc = blame_pc(accessed_by, address)
        callstack = [
            instructions.get_by_address(frame_pc) for frame_pc in pc_to_callstack[pc]
        ]
        samples.append(Sample(value=1, callstack=callstack))
    return samples


def build_profile(
    tracer_data: TracerDataManager,
    segments: MemorySegmentManager,
    segment_offsets: dict[int, int],
    accessed_memory: set[RelocatableValue],
) -> RuntimeProfile:
    function_list = collect_contract_functions(tracer_data)
    instructions_list = create_instruction_list(function_list, tracer_data)
    instructions = Instructions.from_list(instructions_list)
    step_samples = build_step_samples(instructions, tracer_data)
    memhole_samples = build_memhole_samples(
        instructions,
        tracer_data,
        accessed_memory,
        segments,
        segment_offsets,
    )
    callstacks_syscall = build_call_callstacks(instructions, tracer_data)
    profile = RuntimeProfile(
        functions=function_list,
        instructions=instructions_list,
        step_samples=step_samples,
        memhole_samples=memhole_samples,
        contract_call_callstacks=callstacks_syscall,
    )
    return profile
