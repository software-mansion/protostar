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
        str(CountSeriesStatistic([1, 6, 3, 2, 6, 2]))
        == "μ: 3.33, Md: 2.5, min: 1, max: 6"
    )
    assert (
        str(CountSeriesStatistic([1, 1, 1, 1, 1, 1])) == "μ: 1, Md: 1, min: 1, max: 1"
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


def test_statistic_add_observation():
    assert CountStatistic(1).add_observation(CountStatistic(2)) == CountSeriesStatistic(
        [1, 2]
    )
    assert CountStatistic(1).add_observation(
        CountSeriesStatistic([2, 3])
    ) == CountSeriesStatistic([1, 2, 3])
    assert CountSeriesStatistic([1, 2]).add_observation(
        CountStatistic(3)
    ) == CountSeriesStatistic([1, 2, 3])
    assert CountSeriesStatistic([1, 2]).add_observation(
        CountSeriesStatistic([3, 4])
    ) == CountSeriesStatistic([1, 2, 3, 4])


def test_statistic_add_observation_zeros():
    assert CountStatistic().add_observation(CountStatistic()) == CountSeriesStatistic()
    assert (
        CountStatistic().add_observation(CountSeriesStatistic())
        == CountSeriesStatistic()
    )
    assert (
        CountSeriesStatistic().add_observation(CountStatistic())
        == CountSeriesStatistic()
    )
    assert (
        CountSeriesStatistic().add_observation(CountSeriesStatistic())
        == CountSeriesStatistic()
    )

    assert CountStatistic(1).add_observation(CountStatistic()) == CountSeriesStatistic(
        [1]
    )


def test_statistic_add_observation_is_associative():
    assert CountStatistic(1).add_observation(CountStatistic(2)).add_observation(
        CountStatistic(3)
    ) == CountStatistic(1).add_observation(
        CountStatistic(2).add_observation(CountStatistic(3))
    )


def test_execution_resources_summary_add_observation():
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

    assert lhs.add_observation(rhs) == ExecutionResourcesSummary(
        n_steps=CountSeriesStatistic([1, 2]),
        n_memory_holes=CountSeriesStatistic([1, 2, 3, 4]),
        builtin_name_to_count_map={
            "foo": CountSeriesStatistic([1, 2]),
            "bar": CountSeriesStatistic([1]),
            "moo": CountSeriesStatistic([1]),
        },
    )


def test_execution_resources_summary_add_observation_zeros():
    assert ExecutionResourcesSummary().add_observation(
        ExecutionResourcesSummary()
    ) == ExecutionResourcesSummary(
        n_steps=CountSeriesStatistic(),
        n_memory_holes=CountSeriesStatistic(),
    )

    assert ExecutionResourcesSummary(
        n_steps=CountStatistic(1),
        n_memory_holes=CountSeriesStatistic([1, 2]),
        builtin_name_to_count_map={"foo": CountStatistic(1), "bar": CountStatistic(1)},
    ).add_observation(ExecutionResourcesSummary()) == ExecutionResourcesSummary(
        n_steps=CountSeriesStatistic([1]),
        n_memory_holes=CountSeriesStatistic([1, 2]),
        builtin_name_to_count_map={
            "foo": CountSeriesStatistic([1]),
            "bar": CountSeriesStatistic([1]),
        },
    )


def test_execution_resources_summary_add_observation_is_associative():
    ers_a = ExecutionResourcesSummary(
        n_steps=CountStatistic(1),
        n_memory_holes=CountSeriesStatistic([1, 2]),
        builtin_name_to_count_map={"foo": CountStatistic(1), "bar": CountStatistic(1)},
    )

    ers_b = ExecutionResourcesSummary(
        n_steps=CountStatistic(3),
        n_memory_holes=CountSeriesStatistic([3, 4]),
        builtin_name_to_count_map={"foo": CountStatistic(2), "bar": CountStatistic(2)},
    )

    ers_c = ExecutionResourcesSummary(
        n_steps=CountStatistic(4),
        n_memory_holes=CountSeriesStatistic([5, 6]),
        builtin_name_to_count_map={"foo": CountStatistic(3), "bar": CountStatistic(3)},
    )

    assert ers_a.add_observation(ers_b).add_observation(ers_c) == ers_a.add_observation(
        ers_b.add_observation(ers_c)
    )
