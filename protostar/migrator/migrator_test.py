from os import listdir
from pathlib import Path

from freezegun import freeze_time
from pytest_mock import MockerFixture

from protostar.migrator.migrator import Migrator
from protostar.starknet_gateway.starknet_request import StarknetRequest


@freeze_time("2022-04-02 21:37:42")
def test_migrator_saves_result_successfully_with_proper_name(
    mocker: MockerFixture, tmp_path: Path
):
    migrator = Migrator(
        migrator_execution_environment=mocker.MagicMock(),
        compilation_output_path=mocker.MagicMock(),
    )

    migrator.save_history(
        history=Migrator.History(
            starknet_requests=[
                StarknetRequest(
                    action="DEPLOY", payload={"foo": "bar"}, response={"bar": "foo"}
                )
            ]
        ),
        migration_file_basename="01_init",
        output_dir_relative_path=tmp_path,
    )

    assert "20220402213742_01_init.json" in listdir(tmp_path)
