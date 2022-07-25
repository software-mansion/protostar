import pytest

from protostar.commands.test.testing_seed import TestingSeed


def test_sets_seed():
    with TestingSeed(100):
        assert TestingSeed.current() == 100

    with TestingSeed(200):
        assert TestingSeed.current() == 200


def test_picks_seed_automatically():
    with TestingSeed():
        i = TestingSeed.current()

    with TestingSeed(seed=None):
        j = TestingSeed.current()
        assert i != j


def test_current_testing_seed_raises_outside_context_manager():
    with pytest.raises(LookupError):
        _ = TestingSeed.current()
