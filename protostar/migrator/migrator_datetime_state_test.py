from freezegun import freeze_time

from .migrator_datetime_state import MigratorDateTimeState


@freeze_time("2022-04-02 21:37:42")
def test_migrator_datetime_state():
    state = MigratorDateTimeState()

    state.update_to_now()
    prefix = state.get_prefix()

    assert prefix == "20220402213742"


def test_prefix_when_state_is_empty():
    state = MigratorDateTimeState()

    prefix = state.get_prefix()

    assert prefix is None
