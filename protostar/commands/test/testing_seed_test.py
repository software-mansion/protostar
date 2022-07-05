import pytest

from protostar.commands.test.testing_seed import testing_seed, current_testing_seed


def test_sets_seed():
    with testing_seed(100) as i:
        assert i == 100
        assert current_testing_seed() == 100

    with testing_seed(200) as j:
        assert j == 200
        assert current_testing_seed() == 200


def test_picks_seed_automatically():
    with testing_seed() as i:
        pass

    with testing_seed(seed=None) as j:
        assert i != j


def test_current_testing_seed_raises_outside_context_manager():
    with pytest.raises(LookupError):
        current_testing_seed()
