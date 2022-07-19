from pathlib import Path
from typing import Optional

from typing_extensions import Literal

from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)


class Migrator:
    class Builder:
        def __init__(self) -> None:
            # self._starknet_compiler: Optional[StarknetCompiler] = None
            self._migrator_execution_environment: Optional[
                MigratorExecutionEnvironment
            ] = None

        # def set_starknet_compiler(self, starknet_compiler: StarknetCompiler) -> None:
        #     self._starknet_compiler = starknet_compiler

        def set_migrator_execution_environment(
            self, migrator_execution_environment: MigratorExecutionEnvironment
        ):
            self._migrator_execution_environment = migrator_execution_environment

        def build(self):
            assert self._migrator_execution_environment is not None
            return Migrator(
                migrator_execution_environment=self._migrator_execution_environment
            )

    def __init__(
        self,
        migrator_execution_environment: MigratorExecutionEnvironment,
    ) -> None:
        self._migrator_execution_environment = migrator_execution_environment

    async def run(self, mode: Literal["up", "down"]):
        assert mode in ("up", "down")

        await self._migrator_execution_environment.invoke(function_name=mode)

        # TODO: save the results
