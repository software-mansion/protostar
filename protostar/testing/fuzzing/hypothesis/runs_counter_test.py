from .runs_counter import RunsCounter


def test_available_runs_is_always_non_negative():
    counter = RunsCounter(budget=10)

    for _ in range(20):
        next(counter)

    assert counter.balance == -10
    assert counter.available_runs == 0
