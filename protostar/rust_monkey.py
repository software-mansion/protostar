"""
Inspired by https://github.com/lambdaclass/cairo-lang/pull/1/
"""
import logging
import sys
from typing import Any, Callable, Iterable, Optional, cast

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starkware_utils.error_handling import (
    stark_assert,
    wrap_with_stark_exception,
)
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.cairo.lang.vm.relocatable import MaybeRelocatable, RelocatableValue
from starkware.cairo.lang.vm.vm_exceptions import SecurityError, VmException
from starkware.python.utils import safe_zip
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.cairo.common.structs import CairoStructFactory
from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.compiler.scoped_name import ScopedName
from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.starknet.public.abi import SYSCALL_PTR_OFFSET
from starkware.cairo.common.structs import CairoStructFactory, CairoStructProxy
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.core.os import segment_utils, syscall_utils
from starkware.starknet.core.os.class_hash import load_program, get_contract_class_struct
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler, get_runtime_type
from starkware.cairo.lang.compiler.identifier_definition import StructDefinition

import cairo_rs_py


logger = logging.getLogger(__name__)

def monkeypatch_rust_vm():
    import starkware.starknet.business_logic.utils as utt 
    utt.get_return_values = get_return_values

    import starkware.starknet.business_logic.transaction.fee as fee
    fee.calculate_l1_gas_by_cairo_usage = calculate_l1_gas_by_cairo_usage

    import starkware.starknet.core.os.class_hash as ha
    ha.compute_class_hash_inner = compute_class_hash_inner

    import starkware.starknet.core.os.segment_utils as seg
    seg.get_os_segment_ptr_range = get_os_segment_ptr_range
    seg.validate_segment_pointers = validate_segment_pointers

    import starkware.starknet.core.os.os_utils as oo
    oo.prepare_os_context = prepare_os_context
    oo.validate_and_process_os_context = validate_and_process_os_context

    from protostar.starknet.cheatable_syscall_handler import CheatableSysCallHandler
    CheatableSysCallHandler._allocate_segment = _allocate_segment
    CheatableSysCallHandler._read_and_validate_syscall_request = _read_and_validate_syscall_request
    CheatableSysCallHandler.validate_read_only_segments = validate_read_only_segments
    
def calculate_l1_gas_by_cairo_usage(
    general_config, #type: ignore
    cairo_resource_usage, #type: ignore
) -> float:
    """
    Calculates the L1 gas consumed when submitting the underlying Cairo program to SHARP.
    I.e., returns the heaviest Cairo resource weight (in terms of L1 gas), as the size of
    a proof is determined similarly - by the (normalized) largest segment.
    """
    cairo_resource_fee_weights = general_config.cairo_resource_fee_weights
    cairo_resource_names = set(cairo_resource_usage.keys())
    # assert cairo_resource_names.issubset(
    #     cairo_resource_fee_weights.keys()
    # ), "Cairo resource names must be contained in fee weights dict."

    # Convert Cairo usage to L1 gas usage.
    cairo_l1_gas_usage = max(
        cairo_resource_fee_weights[key] * cairo_resource_usage.get(key, 0)
        for key in cairo_resource_fee_weights
    )

    return cairo_l1_gas_usage

def get_return_values(runner: CairoFunctionRunner) -> list[int]:
    """
    Extracts the return values of a StarkNet contract function from the Cairo runner.
    """
    with wrap_with_stark_exception(
        code=StarknetErrorCode.INVALID_RETURN_DATA,
        message="Error extracting return data.",
        logger=logger,
        exception_types=[Exception],
    ):
        ret_data_size, ret_data_ptr = runner.get_return_values(2)

        try: 
            # CAIRO-RS VERSION
            values = runner.get_range(ret_data_ptr, ret_data_size)  # type: ignore
        except:
            # ORIGINAL VERSION
            values = runner.memory.get_range(ret_data_ptr, ret_data_size)


    stark_assert(
        all(isinstance(value, int) for value in values),
        code=StarknetErrorCode.INVALID_RETURN_DATA,
        message="Return data expected to be non-relocatable.",
    )

    return cast(list[int], values)

def compute_class_hash_inner(
    contract_class: ContractClass, hash_func: Callable[[int, int], int]
) -> int:
    print("Use OK")
    program = load_program()
    contract_class_struct = get_contract_class_struct(
        identifiers=program.identifiers, contract_class=contract_class
    )

    runner = cairo_rs_py.CairoRunner(program=program.dumps(), entrypoint=None, layout="all", proof_mode=False) # type: ignore
    runner.initialize_function_runner()
    hash_ptr = runner.add_additional_hash_builtin()


    run_function_runner(
        runner,
        program,
        "starkware.starknet.core.os.contracts.class_hash",
        hash_ptr=hash_ptr,
        contract_class=contract_class_struct,
        use_full_name=True,
        verify_secure=False,
    )
    _, class_hash = runner.get_return_values(2)
    return class_hash

def run_function_runner(
        runner, # type: ignore
        program, # type: ignore
        func_name: str,
        *args, # type: ignore
        hint_locals: Optional[dict[str, Any]] = None, 
        static_locals: Optional[dict[str, Any]] = None,
        verify_secure: Optional[bool] = None,
        trace_on_failure: bool = False,
        apply_modulo_to_args: Optional[bool] = None,
        use_full_name: bool = False,
        verify_implicit_args_segment: bool = False,
        **kwargs, # type: ignore
    ) -> tuple[tuple[MaybeRelocatable, ...], tuple[MaybeRelocatable, ...]]: 
        """
        Runs func_name(*args).
        args are converted to Cairo-friendly ones using gen_arg.
        Returns the return values of the function, splitted into 2 tuples of implicit values and
        explicit values. Structs will be flattened to a sequence of felts as part of the returned
        tuple.
        Additional params:
        verify_secure - Run verify_secure_runner to do extra verifications.
        trace_on_failure - Run the tracer in case of failure to help debugging.
        apply_modulo_to_args - Apply modulo operation on integer arguments.
        use_full_name - Treat 'func_name' as a fully qualified identifier name, rather than a
          relative one.
        verify_implicit_args_segment - For each implicit argument, verify that the argument and the
          return value are in the same segment.
        """
        assert isinstance(program, Program)
        entrypoint = program.get_label(func_name, full_name_lookup=use_full_name)

        #Construct Fu
        structs_factory = CairoStructFactory.from_program(program=program)
        func = ScopedName.from_string(scope=func_name)

        full_args_struct = structs_factory.build_func_args(func=func)
        all_args = full_args_struct(*args, **kwargs)

        try:
            runner.run_from_entrypoint(
                entrypoint,
                all_args,
                typed_args=True,
                hint_locals=hint_locals,
                static_locals=static_locals,
                verify_secure=verify_secure,
                apply_modulo_to_args=apply_modulo_to_args,
            )
        except (VmException, SecurityError, AssertionError) as ex:
            if trace_on_failure:
                print(
                    f"""\
Got {type(ex).__name__} exception during the execution of {func_name}:
{str(ex)}
"""
                )
                #trace_runner(runner=runner)
            raise

        # The number of implicit arguments is identical to the number of implicit return values.
        n_implicit_ret_vals = structs_factory.get_implicit_args_length(func=func)
        n_explicit_ret_vals = structs_factory.get_explicit_return_values_length(func=func)
        n_ret_vals = n_explicit_ret_vals + n_implicit_ret_vals
        implicit_retvals = tuple(
            runner.get_range(
                runner.get_ap() - n_ret_vals, n_implicit_ret_vals
            )
        )

        explicit_retvals = tuple(
            runner.get_range(
                runner.get_ap() - n_explicit_ret_vals, n_explicit_ret_vals
            )
        )

        # Verify the memory segments of the implicit arguments.
        if verify_implicit_args_segment:
            implicit_args = all_args[:n_implicit_ret_vals]
            for implicit_arg, implicit_retval in safe_zip(implicit_args, implicit_retvals):
                assert isinstance(
                    implicit_arg, RelocatableValue
                ), f"Implicit arguments must be RelocatableValues, {implicit_arg} is not."
                assert isinstance(implicit_retval, RelocatableValue), (
                    f"Argument {implicit_arg} is a RelocatableValue, but the returned value "
                    f"{implicit_retval} is not."
                )
                assert implicit_arg.segment_index == implicit_retval.segment_index, (
                    f"Implicit argument {implicit_arg} is not on the same segment as the returned "
                    f"{implicit_retval}."
                )
                assert implicit_retval.offset >= implicit_arg.offset, (
                    f"The offset of the returned implicit argument {implicit_retval} is less than "
                    f"the offset of the input {implicit_arg}."
                )

        return implicit_retvals, explicit_retvals

def prepare_os_context(runner: CairoFunctionRunner) -> list[MaybeRelocatable]:
    # CAIRO-RS VERSION
    try: 
        syscall_segment = runner.add_segment() #type: ignore
        os_context: list[MaybeRelocatable] = [syscall_segment]
        os_context.extend(runner.get_program_builtins_initial_stack()) #type: ignore
        print("kappa")
    # ORIGINAL VERSION
    except:
        syscall_segment = runner.segments.add()
        os_context: list[MaybeRelocatable] = [syscall_segment]

        for builtin in runner.program.builtins:
            builtin_runner = runner.builtin_runners[f"{builtin}_builtin"]
            os_context.extend(builtin_runner.initial_stack())
    return os_context

def validate_and_process_os_context(
    runner: CairoFunctionRunner,
    syscall_handler: syscall_utils.BusinessLogicSysCallHandler,
    initial_os_context: list[MaybeRelocatable],
):
    """
    Validates and processes an OS context that was returned by a transaction.
    Returns the syscall processor object containing the accumulated syscall information.
    """
    # CAIRO-RS VERSION
    try:
        os_context_end = runner.get_ap() - 2 #type: ignore
        stack_ptr = os_context_end
        # The returned values are os_context, retdata_size, retdata_ptr.
        stack_ptr = runner.get_builtins_final_stack(stack_ptr) #type: ignore
    # ORIGINAL VERSION
    except:
        os_context_end = runner.vm.run_context.ap - 2

        stack_ptr = os_context_end

        for builtin in runner.program.builtins[::-1]:
            builtin_runner = runner.builtin_runners[f"{builtin}_builtin"]

            with wrap_with_stark_exception(code=StarknetErrorCode.SECURITY_ERROR):
                stack_ptr = builtin_runner.final_stack(runner=runner, pointer=stack_ptr)

    final_os_context_ptr = stack_ptr - 1
    assert final_os_context_ptr + len(initial_os_context) == os_context_end

    # Validate system calls.
    syscall_base_ptr, syscall_stop_ptr = segment_utils.get_os_segment_ptr_range(
        runner=runner, ptr_offset=SYSCALL_PTR_OFFSET, os_context=initial_os_context
    )

    # ORIGINAL VERSION
    try: 
        segment_utils.validate_segment_pointers(
            segments=runner, #type: ignore
            segment_base_ptr=syscall_base_ptr,
            segment_stop_ptr=syscall_stop_ptr,
        )
    # CAIRO-RS VERSION
    except:
        segment_utils.validate_segment_pointers(
            segments=runner.segments,
            segment_base_ptr=syscall_base_ptr,
            segment_stop_ptr=syscall_stop_ptr,
        )

    syscall_handler.post_run(runner=runner, syscall_stop_ptr=syscall_stop_ptr)

def get_os_segment_ptr_range(
    runner: CairoFunctionRunner, ptr_offset: int, os_context: list[MaybeRelocatable]
) -> tuple[MaybeRelocatable, MaybeRelocatable]:
    """
    Returns the base and stop ptr of the OS-designated segment that starts at ptr_offset.
    """
    allowed_offsets = (SYSCALL_PTR_OFFSET,)
    assert (
        ptr_offset in allowed_offsets
    ), f"Illegal OS ptr offset; must be one of: {allowed_offsets}."

    # The returned values are os_context, retdata_size, retdata_ptr.
    # CAIRO-RS VERSION
    try:
        os_context_end = runner.get_ap() - 2 #type: ignore
    except:
    # ORIGINAL VERSION
        os_context_end = runner.vm.run_context.ap - 2

    final_os_context_ptr = os_context_end - len(os_context)

    # CAIRO-RS VERSION
    try:
        return os_context[ptr_offset], runner.get(final_os_context_ptr + ptr_offset) #type: ignore
    # ORIGINAL VERSION
    except:
        return os_context[ptr_offset], runner.vm_memory[final_os_context_ptr + ptr_offset]

def validate_segment_pointers(
    segments: MemorySegmentManager,
    segment_base_ptr: MaybeRelocatable,
    segment_stop_ptr: MaybeRelocatable,
):
    # assert isinstance(segment_base_ptr, RelocatableValue)
    assert (
        segment_base_ptr.offset == 0 # type: ignore
    ), f"Segment base pointer must be zero; got {segment_base_ptr.offset}."  # type: ignore

    # CAIRO-RS VERSION
    try: 
        expected_stop_ptr = segment_base_ptr + segments.get_segment_used_size(
            index=segment_base_ptr.segment_index)  # type: ignore
   # ORIGINAL VERSION 
    except:
        expected_stop_ptr = segment_base_ptr + segments.get_segment_used_size(
            segment_index=segment_base_ptr.segment_index)  # type: ignore

    stark_assert(
        expected_stop_ptr == segment_stop_ptr,
        code=StarknetErrorCode.SECURITY_ERROR,
        message=(
            f"Invalid stop pointer for segment. "
            f"Expected: {expected_stop_ptr}, found: {segment_stop_ptr}."
        ),
    )

def _allocate_segment(
    self, segments: MemorySegmentManager, data: Iterable[MaybeRelocatable] #type: ignore
) -> RelocatableValue:
    # FIXME: Here "segments" in really a Runner under the hood.
    # May want to change the variable names.

    # CAIRO-RS VERSION
    try: 
        segment_start = segments.add_segment() #type: ignore
    # ORIGINAL VERSION
    except:
        segment_start = segments.add()

    segment_end = segments.write_arg(ptr=segment_start, arg=data)
    self.read_only_segments.append((segment_start, segment_end - segment_start)) #type: ignore
    return segment_start

def _read_and_validate_syscall_request(
    self, syscall_name: str, segments: MemorySegmentManager, syscall_ptr: RelocatableValue #type: ignore
) -> CairoStructProxy:
    """
    Returns the system call request written in the syscall segment, starting at syscall_ptr.
    Performs validations on the request.
    """
    # Update syscall count.
    self._count_syscall(syscall_name=syscall_name)

    request = self._read_syscall_request(
        syscall_name=syscall_name, segments=segments, syscall_ptr=syscall_ptr
    )

    assert (
        syscall_ptr == self.expected_syscall_ptr
    ), f"Bad syscall_ptr, Expected {self.expected_syscall_ptr}, got {syscall_ptr}."

    syscall_info = self.syscall_info[syscall_name]
    self.expected_syscall_ptr += syscall_info.syscall_size

    selector = request.selector
    assert isinstance(selector, int), (
        f"The selector argument to syscall {syscall_name} is of unexpected type. "
        f"Expected: int; got: {type(selector).__name__}."
    )
    assert (
        selector == syscall_info.selector
    ), f"Bad syscall selector, expected {syscall_info.selector}. Got: {selector}"

    args_struct_def: StructDefinition = syscall_info.syscall_request_struct.struct_definition_
    for arg, (arg_name, arg_def) in safe_zip(request, args_struct_def.members.items()):
        expected_type = get_runtime_type(arg_def.cairo_type)
        # assert isinstance(arg, expected_type), (
        #     f"Argument {arg_name} to syscall {syscall_name} is of unexpected type. "
        #     f"Expected: value of type {expected_type}; got: {arg}."
        # )

    return request

def validate_read_only_segments(self, runner: CairoFunctionRunner): #type: ignore
        """
        Validates that there were no out of bounds writes to read-only segments and marks
        them as accessed.
        """
        # ORIGINAL VERSION
        try: 
            segments = runner.segments
        # CAIRO-RS VERSION
        except:
            segments = runner

        for segment_ptr, segment_size in self.read_only_segments:
            # CAIRO-RS VERSION
            try:
                used_size = segments.get_segment_used_size(index=segment_ptr.segment_index) #type: ignore
            # ORIGINAL VERSION
            except: 
                used_size = segments.get_segment_used_size(segment_index=segment_ptr.segment_index) #type: ignore
            stark_assert(
                used_size == segment_size,
                code=StarknetErrorCode.SECURITY_ERROR,
                message="Out of bounds write to a read-only segment.",
            )

            runner.mark_as_accessed(address=segment_ptr, size=segment_size)
