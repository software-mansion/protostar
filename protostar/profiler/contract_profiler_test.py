# pylint: disable=protected-access
from collections import Mapping
from typing import Dict
import pytest

from starkware.cairo.lang.vm.memory_dict import MemoryDict

from protostar.profiler.contract_profiler import ProfilerContext


@pytest.fixture(name="memory")
def memory_fixture() -> Mapping[int, int]:
    return {i: 1 for i in range(20)}


@pytest.fixture(name="profiler_context")
def profiler_context_fixture(memory) -> ProfilerContext:
    return ProfilerContext(0, MemoryDict(values=memory))


@pytest.mark.parametrize("last_accesses,hole_address,expected", [
    ({19: 0, 18: 1}, 17, 1),
    ({19: 0, 4: 1}, 17, 0),
    ({19: 0, 3: 1}, 13, 0),
    ({19: 0, 4: 1}, 3, 1),
    ({16: 0, 14: 0,}, 10, 0),
    ({16: 0, 14: 0, 12: 1}, 10, 1),
    ({16: 0, 14: 0, 12: 1}, 13, 0),
    ({16: 0, 14: 0, 12: 1}, 15, 0),
    ({16: 15}, 14, 15),
])
async def test_blame_pc(profiler_context: ProfilerContext, last_accesses: Dict[int, int], hole_address:int, expected):
    assert profiler_context.blame_pc(last_accesses, hole_address) == expected
    
