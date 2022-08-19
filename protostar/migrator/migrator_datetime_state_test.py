from pathlib import Path

from freezegun import freeze_time

from .migrator_datetime_state import MigratorDateTimeState


@freeze_time("2022-04-02 21:37:42")
def test_output_directory(tmp_path: Path):
    migration_file_stem = "migration_01_init"
    state = MigratorDateTimeState(
        migration_file_path=tmp_path / f"{migration_file_stem}.cairo"
    )
    state.update_to_now()
    output_path = state.get_compilation_output_path()

    assert str(output_path) == str(tmp_path / f"20220402213742_{migration_file_stem}")
