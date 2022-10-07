import dataclasses
import json
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import List, Optional

from starknet_py.net.signer import BaseSigner

from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.starknet_gateway import GatewayFacade
from protostar.starknet_gateway.starknet_request import StarknetRequest
from protostar.io.log_color_provider import LogColorProvider

from .output_directory import create_output_directory
from .migrator_datetime_state import MigratorDateTimeState


class Migrator:
    @dataclass(frozen=True)
    class History:
        starknet_requests: List[StarknetRequest]

        def save_as_json(self, output_file_path: Path):
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                json.dump(dataclasses.asdict(self), output_file, indent=4)

    class Builder:
        def __init__(
            self,
            migrator_execution_environment_builder: MigratorExecutionEnvironment.Builder,
            project_root_path: Optional[Path] = None,
        ) -> None:
            self._migrator_execution_environment_builder = (
                migrator_execution_environment_builder
            )
            self._logger: Optional[Logger] = None
            self._log_color_provider: Optional[LogColorProvider] = None
            self._migrator_execution_environment_config = None
            self._gateway_facade = None
            self._project_root_path = project_root_path

        def set_logger(
            self, logger: Logger, log_color_provider: LogColorProvider
        ) -> None:
            self._logger = logger
            self._log_color_provider = log_color_provider

        def set_migration_execution_environment_config(
            self, config: MigratorExecutionEnvironment.Config
        ):
            self._migrator_execution_environment_config = config

        def set_gateway_facade(self, gateway_facade: GatewayFacade):
            self._gateway_facade = gateway_facade

        def set_signer(self, signer: BaseSigner):
            self._migrator_execution_environment_builder.set_signer(signer)

        async def build(self, migration_file_path: Path):
            assert self._migrator_execution_environment_config is not None
            assert self._gateway_facade is not None
            self._migrator_execution_environment_builder.set_gateway_facade(
                self._gateway_facade
            )

            migrator_datetime_state = MigratorDateTimeState(migration_file_path)
            self._migrator_execution_environment_builder.set_migration_datetime_state(
                migrator_datetime_state
            )

            migrator_execution_env = (
                await self._migrator_execution_environment_builder.build(
                    migration_file_path,
                    config=self._migrator_execution_environment_config,
                )
            )

            return Migrator(
                migrator_execution_environment=migrator_execution_env,
                project_root_path=self._project_root_path,
                migrator_datetime_state=migrator_datetime_state,
            )

    def __init__(
        self,
        migrator_execution_environment: MigratorExecutionEnvironment,
        migrator_datetime_state: MigratorDateTimeState,
        project_root_path: Optional[Path] = None,
    ) -> None:
        self._project_root_path = project_root_path or Path()
        self._migrator_execution_environment = migrator_execution_environment
        self._migrator_datetime_state = migrator_datetime_state

    async def run(self, rollback=False) -> History:
        self._migrator_datetime_state.update_to_now()
        with create_output_directory(
            self._migrator_datetime_state.get_compilation_output_path()
        ):
            await self._migrator_execution_environment.execute(
                function_name="down" if rollback else "up"
            )

        return Migrator.History(starknet_requests=self._get_sent_requests())

    def _get_sent_requests(self):
        return (
            self._migrator_execution_environment.cheatcode_factory.gateway_facade.get_starknet_requests()
        )

    def save_history(
        self,
        history: History,
        output_dir_relative_path: Path,
    ):
        output_dir_path = self._project_root_path / output_dir_relative_path

        output_file_path = (
            output_dir_path / f"{self._migrator_datetime_state.get_output_stem()}.json"
        )

        if not output_dir_path.exists():
            output_dir_path.mkdir(
                parents=True,
            )

        history.save_as_json(output_file_path)
