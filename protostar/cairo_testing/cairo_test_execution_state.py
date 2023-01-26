import dataclasses
from copy import deepcopy
from dataclasses import dataclass

from typing_extensions import Self

from protostar.cheatable_starknet.cheatables.cheatable_starknet_facade import (
    CheatableStarknetFacade,
)
from protostar.compiler import ProjectCompiler
from protostar.testing.stopwatch import Stopwatch
from protostar.testing.test_config import TestConfig
from protostar.testing.test_context import TestContext
from protostar.testing.test_output_recorder import OutputRecorder


@dataclass
class CairoTestExecutionState:
    starknet: CheatableStarknetFacade
    stopwatch: Stopwatch
    output_recorder: OutputRecorder
    context: TestContext
    config: TestConfig
    project_compiler: ProjectCompiler

    def fork(self) -> Self:
        return dataclasses.replace(
            self,
            context=deepcopy(self.context),
            config=deepcopy(self.config),
            output_recorder=self.output_recorder.fork(),
            stopwatch=self.stopwatch.fork(),
            starknet=self.starknet.fork(),
        )

    @classmethod
    async def from_test_config(
        cls, test_config: TestConfig, project_compiler: ProjectCompiler
    ):
        return cls(
            starknet=await CheatableStarknetFacade.create(),
            stopwatch=Stopwatch(),
            output_recorder=OutputRecorder(),
            context=TestContext(),
            config=test_config,
            project_compiler=project_compiler,
        )
