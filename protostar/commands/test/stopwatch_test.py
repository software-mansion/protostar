import pytest

from protostar.commands.test.stopwatch import Stopwatch


def test_measures_time():
    stopwatch = Stopwatch()

    with stopwatch.lap("a"):
        pass

    with stopwatch.lap("b"):
        pass

    assert list(stopwatch.laps.keys()) == ["a", "b"]
    for duration in stopwatch.laps.values():
        assert duration >= 0.0

    assert stopwatch.total_elapsed == stopwatch.laps["a"] + stopwatch.laps["b"]


def test_lap_raises_when_trying_to_measure_same_name():
    stopwatch = Stopwatch()

    with stopwatch.lap("foo"):
        pass

    with pytest.raises(KeyError):
        with stopwatch.lap("foo"):
            pass
