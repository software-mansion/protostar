from os import listdir
from pathlib import Path

from freezegun import freeze_time

from protostar.migrator.migrator import Migrator
from protostar.starknet_gateway.starknet_interaction import StarknetInteraction


@freeze_time("2022-04-02 21:37:42")
def test_migrator_saves_result_successfully_with_proper_name(tmp_path: Path):
    Migrator.save_history(
        history=Migrator.History(
            starknet_interactions=[
                StarknetInteraction(
                    direction="FROM_STARKNET", action="DEPLOY", payload={"foo": "bar"}
                )
            ]
        ),
        migration_file_basename="01_init",
        output_dir_path=tmp_path,
    )

    assert "20220402213742_01_init.json" in listdir(tmp_path)
