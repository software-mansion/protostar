import pytest

from protostar.commands.test.starkware.execution_resources_summary import (
    CountStatistic,
    CountSeriesStatistic,
    Statistic,
    ExecutionResourcesSummary,
)


def test_count_statistic_str():
    assert str(CountStatistic(10)) == "10"


def test_count_statistic_bool():
    assert not bool(CountStatistic(0))
    assert bool(CountStatistic(1))


def test_count_series_statistic_str():
    assert str(CountSeriesStatistic([])) == "0"
    assert str(CountSeriesStatistic([1])) == "1"
    assert (
        str(CountSeriesStatistic([1, 2, 3, 4, 5, 6]))
        == "mean: 3.5, σ: 1.87, min: 1, max: 6"
    )
    assert (
        str(CountSeriesStatistic([1, 1, 1, 1, 1, 1]))
        == "mean: 1, σ: 0.0, min: 1, max: 1"
    )


def test_count_series_statistic_bool():
    assert not bool(CountSeriesStatistic([]))
    assert bool(CountSeriesStatistic([0]))
    assert bool(CountSeriesStatistic([1]))


def test_count_series_statistic_from_count_series_statistic():
    css = CountSeriesStatistic([1, 2])
    assert CountSeriesStatistic.from_statistic(css) is css


def test_count_series_statistic_from_count_statistic():
    assert CountSeriesStatistic.from_statistic(
        CountStatistic(1)
    ) == CountSeriesStatistic([1])


def test_count_series_statistic_from_zero_count_statistic():
    assert (
        CountSeriesStatistic.from_statistic(CountStatistic()) == CountSeriesStatistic()
    )


def test_count_series_statistic_from_unknown_type():
    class SentinelStatistic(Statistic):
        def __str__(self) -> str:
            raise NotImplementedError

        def __bool__(self) -> bool:
            raise NotImplementedError

    with pytest.raises(TypeError):
        CountSeriesStatistic.from_statistic(SentinelStatistic())


def test_statistic_add():
    assert CountStatistic(1) + CountStatistic(2) == CountSeriesStatistic([1, 2])
    assert CountStatistic(1) + CountSeriesStatistic([2, 3]) == CountSeriesStatistic(
        [1, 2, 3]
    )
    assert CountSeriesStatistic([1, 2]) + CountStatistic(3) == CountSeriesStatistic(
        [1, 2, 3]
    )
    assert CountSeriesStatistic([1, 2]) + CountSeriesStatistic(
        [3, 4]
    ) == CountSeriesStatistic([1, 2, 3, 4])


def test_statistic_add_zeros():
    assert CountStatistic() + CountStatistic() == CountSeriesStatistic()
    assert CountStatistic() + CountSeriesStatistic() == CountSeriesStatistic()
    assert CountSeriesStatistic() + CountStatistic() == CountSeriesStatistic()
    assert CountSeriesStatistic() + CountSeriesStatistic() == CountSeriesStatistic()


def test_execution_resources_summary_add():
    lhs = ExecutionResourcesSummary(
        n_steps=CountStatistic(1),
        n_memory_holes=CountSeriesStatistic([1, 2]),
        builtin_name_to_count_map={"foo": CountStatistic(1), "bar": CountStatistic(1)},
    )

    rhs = ExecutionResourcesSummary(
        n_steps=CountStatistic(2),
        n_memory_holes=CountSeriesStatistic([3, 4]),
        builtin_name_to_count_map={"foo": CountStatistic(2), "moo": CountStatistic(1)},
    )

    assert lhs + rhs == ExecutionResourcesSummary(
        n_steps=CountSeriesStatistic([1, 2]),
        n_memory_holes=CountSeriesStatistic([1, 2, 3, 4]),
        builtin_name_to_count_map={
            "foo": CountSeriesStatistic([1, 2]),
            "bar": CountSeriesStatistic([1]),
            "moo": CountSeriesStatistic([1]),
        },
    )


def test_execution_resources_summary_add_zeros():
    assert (
        ExecutionResourcesSummary() + ExecutionResourcesSummary()
        == ExecutionResourcesSummary(
            n_steps=CountSeriesStatistic(),
            n_memory_holes=CountSeriesStatistic(),
        )
    )
