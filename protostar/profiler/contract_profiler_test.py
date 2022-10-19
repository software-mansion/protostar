# pylint: disable=invalid-name
from typing import Dict, List, Set
import pytest
from pytest_mock import MockerFixture

from starkware.cairo.lang.vm.memory_dict import (
    MemoryDict,
    MemoryDictInitializer,
    RelocatableValue,
)
from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME

from protostar.profiler.contract_profiler import (
    TracerDataManager,
    blame_pc,
    get_not_accessed_addresses,
)


@pytest.fixture(name="memory")
def memory_fixture() -> MemoryDictInitializer:
    return {i: 1 for i in range(20)}


@pytest.fixture(name="n_seg")
def n_seg_fixture() -> int:
    return 1


@pytest.fixture(name="memory_segments")
def memory_segments_fixture(memory: MemoryDictInitializer, n_seg: int) -> MemorySegmentManager:
    manager = MemorySegmentManager(MemoryDict(memory), DEFAULT_PRIME)
    for _ in range(n_seg):
        manager.add()
    return manager


@pytest.fixture(name="segments_offsets")
def segments_offsets_fixture(memory_segments: MemorySegmentManager) -> Dict[int, int]:
    memory_segments.memory.freeze()
    memory_segments.compute_effective_sizes()
    return memory_segments.relocate_segments()


@pytest.fixture(name="tracer_data")
def tracer_data_fixture(mocker: MockerFixture, memory: MemoryDict) -> TracerDataManager:
    data_mock = mocker.MagicMock()
    data_mock.memory = memory
    data_mock.initial_fp = 0
    return data_mock


@pytest.mark.parametrize(
    "last_accesses,hole_address,expected",
    [
        ({19: 0, 18: 1}, 17, 1),
        ({19: 0, 4: 1}, 17, 0),
        ({19: 0, 3: 1}, 13, 0),
        ({19: 0, 4: 1}, 3, 1),
        (
            {
                16: 0,
                14: 0,
            },
            10,
            0,
        ),
        ({16: 0, 14: 0, 12: 1}, 10, 1),
        ({16: 0, 14: 0, 12: 1}, 13, 0),
        ({16: 0, 14: 0, 12: 1}, 15, 0),
        ({16: 15}, 14, 15),
    ],
)
def test_blame_pc(
    last_accesses: Dict[int, int],
    hole_address: int,
    expected: int,
):
    assert blame_pc(last_accesses, hole_address) == expected


@pytest.mark.parametrize(
    "memory,fp,pc,expected",
    [
        ({100: 42, 99: 43, 98: 39, 38: 11, 37: 0, 0: 0}, 100, 101, [101, 43, 11]),
    ],
)
def test_get_callstack(tracer_data: TracerDataManager, fp: int, pc: int, expected: List[int]):
    assert TracerDataManager.get_callstack(tracer_data, fp, pc) == expected


@pytest.mark.parametrize(
    "n_seg,memory,not_accessed,expected",
    [
        (
            2,
            {
                RelocatableValue(0, 2): 1,
                RelocatableValue(0, 4): 1,
                RelocatableValue(1, 3): 1,
                RelocatableValue(1, 5): 1,
            },
            {RelocatableValue(1, 4), RelocatableValue(0, 3)},
            set(range(12)) - {0, 4, 10},
        ),
        (
            2,
            {
                RelocatableValue(0, 2): 1,
                RelocatableValue(0, 4): 1,
                RelocatableValue(1, 20): 1,
            },
            {RelocatableValue(0, 3), RelocatableValue(1, 19)},
            set(range(27)) - {0, 4, 25},
        ),
    ],
)
def test_not_accessed(
    not_accessed: Set[RelocatableValue],
    memory_segments: MemorySegmentManager,
    segments_offsets: Dict[int, int],
    expected: List[int],
):
    assert (
        get_not_accessed_addresses(not_accessed, memory_segments, segments_offsets)
        == expected
    )
