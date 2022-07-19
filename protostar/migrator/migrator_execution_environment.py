from typing import Optional

from protostar.migrator.migrator_cheatcodes_factory import MigratorCheatcodeFactory
from protostar.starknet.execution_environment import ExecutionEnvironment
from protostar.starknet.execution_state import ExecutionState


class MigratorExecutionEnvironment(ExecutionEnvironment[None]):
    class Builder:
        def __init__(
            self,
        ) -> None:
            self._state: Optional[MigratorExecutionEnvironment.State] = None
            self._migration_cheatcode_factory: Optional[MigratorCheatcodeFactory] = None

        def set_migrator_execution_environment_state(
            self, state: "MigratorExecutionEnvironment.State"
        ):
            self._state = state

        def set_migration_cheatcode_factory(
            self, migration_cheatcode_factory: MigratorCheatcodeFactory
        ):
            self._migration_cheatcode_factory = migration_cheatcode_factory

        async def build(self) -> "MigratorExecutionEnvironment":
            assert self._state is not None
            assert self._migration_cheatcode_factory is not None

            return MigratorExecutionEnvironment(
                state=self._state,
                migrator_cheatcode_factory=self._migration_cheatcode_factory,
            )

    class State(ExecutionState):
        pass

    def __init__(
        self, state: "State", migrator_cheatcode_factory: MigratorCheatcodeFactory
    ):
        super().__init__(state)
        self._migrator_cheatcode_factory = migrator_cheatcode_factory

    async def invoke(self, function_name: str) -> None:
        self.set_cheatcodes(self._migrator_cheatcode_factory)
        await self.perform_invoke(function_name)
