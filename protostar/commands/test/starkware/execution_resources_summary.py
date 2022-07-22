import dataclasses
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Iterable, Optional
from typing_extensions import Self

from starkware.cairo.lang.vm.cairo_pie import ExecutionResources


class Statistic(ABC):
    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...

    def __add__(self, other: "Statistic") -> "CountSeriesStatistic":
        self_series = CountSeriesStatistic.from_statistic(self)
        other_series = CountSeriesStatistic.from_statistic(other)
        return CountSeriesStatistic(self_series.series + other_series.series)


@dataclass
class CountStatistic(Statistic):
    value: int = field(default=0)

    def __str__(self) -> str:
        return str(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)


@dataclass
class CountSeriesStatistic(Statistic):
    series: List[int] = field(default_factory=list)

    def __str__(self) -> str:
        if not self.series:
            return "0"

        if len(self.series) == 1:
            return str(self.series[0])

        mean_v = round(statistics.mean(self.series), 2)
        stdev_v = round(statistics.stdev(self.series), 2)
        min_v = min(self.series)
        max_v = max(self.series)
        return f"mean: {mean_v}, σ: {stdev_v}, min: {min_v}, max: {max_v}"

    def __bool__(self) -> bool:
        return bool(self.series)

    @classmethod
    def from_statistic(cls, statistic: Statistic) -> Self:
        if isinstance(statistic, cls):
            return statistic

        if isinstance(statistic, CountStatistic):
            if statistic.value == 0:
                return cls()

            return cls([statistic.value])

        raise TypeError("Unknown statistic type.")


@dataclass
class ExecutionResourcesSummary:
    n_steps: Statistic = field(default_factory=CountStatistic)
    n_memory_holes: Statistic = field(default_factory=CountStatistic)
    builtin_name_to_count_map: Dict[str, Statistic] = field(default_factory=dict)

    @classmethod
    def from_execution_resources(cls, execution_resources: ExecutionResources):
        return cls(
            n_steps=CountStatistic(execution_resources.n_steps),
            n_memory_holes=CountStatistic(execution_resources.n_memory_holes),
            builtin_name_to_count_map={
                k: CountStatistic(v)
                for k, v in execution_resources.builtin_instance_counter.items()
            },
        )

    def __add__(self, other: Self) -> Self:
        builtin_name_to_count_map = defaultdict(CountSeriesStatistic)
        for source in [self.builtin_name_to_count_map, other.builtin_name_to_count_map]:
            for k, v in source.items():
                builtin_name_to_count_map[k] += v

        return dataclasses.replace(
            self,
            n_steps=self.n_steps + other.n_steps,
            n_memory_holes=self.n_memory_holes + other.n_memory_holes,
            builtin_name_to_count_map=dict(builtin_name_to_count_map),
        )

    @staticmethod
    def sum(
        items: Iterable["ExecutionResourcesSummary"],
    ) -> Optional["ExecutionResourcesSummary"]:
        result = None
        for item in items:
            if result is None:
                result = item
            else:
                result += item
        return result
