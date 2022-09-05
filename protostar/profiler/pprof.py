# pylint: disable=invalid-name
# pylint: disable=no-member
import gzip
import time
from starkware.cairo.lang.tracer.third_party.profile_pb2 import Profile


def to_protobuf(profile_obj) -> Profile:
    profile = Profile()

    profile.time_nanos = int(time.time() * 10**9)  # type: ignore

    for sample_type in profile_obj.sample_types:
        sample_tp = profile.sample_type.add()  # type: ignore
        sample_tp.type = sample_type.type
        sample_tp.unit = sample_type.unit

    for val in profile_obj.strings:
        profile.string_table.append(val)  # type: ignore

    for function in profile_obj.functions:
        func = profile.function.add()  # type: ignore
        func.id = function.id
        func.system_name = func.name = function.id
        func.filename = function.filename
        func.start_line = function.start_line

    for inst in profile_obj.instructions:
        location = profile.location.add()  # type: ignore
        location.id = inst.id
        location.address = inst.pc
        location.is_folded = False
        line = location.line.add()
        line.function_id = inst.function.id
        line.line = inst.line

    for smp in profile_obj.step_samples:
        sample = profile.sample.add()  # type: ignore
        for instr in smp.callstack:
            sample.location_id.append(instr.id)
        sample.value.append(smp.value)
        sample.value.append(0)

    for smp in profile_obj.memhole_samples:
        sample = profile.sample.add()  # type: ignore
        for instr in smp.callstack:
            sample.location_id.append(instr.id)
        sample.value.append(0)
        sample.value.append(smp.value)

    return profile


def serialize(profile: Profile) -> bytes:
    data = profile.SerializeToString()  # type: ignore
    return gzip.compress(data)
