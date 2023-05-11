import dataclasses
from copy import deepcopy
from dataclasses import dataclass

from typing_extensions import Self

from protostar.compiler import Cairo0ProjectCompiler
from protostar.contract_path_resolver import ContractPathResolver
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.testing.stopwatch import Stopwatch
from protostar.testing.test_config import TestConfig
from protostar.testing.test_context import TestContext
from protostar.testing.test_output_recorder import OutputRecorder


@dataclass
class TestExecutionState:
    starknet: ForkableStarknet
    stopwatch: Stopwatch
    output_recorder: OutputRecorder
    context: TestContext
    config: TestConfig
    cairo0_project_compiler: Cairo0ProjectCompiler
    contract_path_resolver: ContractPathResolver

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
        cls,
        test_config: TestConfig,
        cairo0_project_compiler: Cairo0ProjectCompiler,
        contract_path_resolver: ContractPathResolver,
    ):
        return cls(
            starknet=await ForkableStarknet.empty(),
            stopwatch=Stopwatch(),
            output_recorder=OutputRecorder(),
            context=TestContext(),
            config=test_config,
            cairo0_project_compiler=cairo0_project_compiler,
            contract_path_resolver=contract_path_resolver,
        )
