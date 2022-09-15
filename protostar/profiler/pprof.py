# pylint: disable=invalid-name
# pylint: disable=no-member
import gzip
import time
from starkware.cairo.lang.tracer.third_party.profile_pb2 import Profile


def string_id(string_table, string_ids, val):
    if val not in string_ids:
        string_ids[val] = len(string_table)
        string_table.append(val)
    return string_ids[val]


def to_protobuf(profile_obj) -> Profile:
    profile = Profile()
    string_table = [""]
    string_ids = {"": 0}

    profile.time_nanos = int(time.time() * 10**9)  # type: ignore

    for sample_type in profile_obj.sample_types:
        sample_tp = profile.sample_type.add()  # type: ignore
        sample_tp.type = string_id(string_table, string_ids, sample_type.type)
        sample_tp.unit = string_id(string_table, string_ids, sample_type.unit)

    for function in profile_obj.functions:
        func = profile.function.add()  # type: ignore
        func.id = string_id(string_table, string_ids, function.id)
        func.system_name = func.name = string_id(string_table, string_ids, function.id)
        func.filename = string_id(string_table, string_ids, function.filename)
        func.start_line = function.start_line

    for inst in profile_obj.instructions:
        location = profile.location.add()  # type: ignore
        location.id = inst.id
        location.address = inst.pc
        location.is_folded = False
        line = location.line.add()
        line.function_id = string_id(string_table, string_ids, inst.function.id)
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

    for val in string_table:
        profile.string_table.append(val)  # type: ignore

    return profile


def serialize(profile: Profile) -> bytes:
    data = profile.SerializeToString()  # type: ignore
    return gzip.compress(data)
