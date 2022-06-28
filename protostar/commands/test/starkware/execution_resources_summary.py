from dataclasses import dataclass
from typing import Dict

from starkware.cairo.lang.vm.cairo_pie import ExecutionResources


@dataclass
class ExecutionResourcesSummary:
    @classmethod
    def from_execution_resources(cls, execution_resources: ExecutionResources):
        return cls(
            n_steps=execution_resources.n_steps,
            n_memory_holes=execution_resources.n_memory_holes,
            builtin_name_to_count_map=execution_resources.builtin_instance_counter,
        )

    n_steps: int
    n_memory_holes: int
    builtin_name_to_count_map: Dict[str, int]
