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
from protostar.cheatable_starknet.cheaters.expect_events_controller import (
    EventsExpectation,
    Event,
)


@dataclass
class CairoTestExecutionState:
    cheatable_starknet_facade: CheatableStarknetFacade
    stopwatch: Stopwatch
    output_recorder: OutputRecorder
    context: TestContext
    config: TestConfig
    project_compiler: ProjectCompiler
    _event_expectations: list[EventsExpectation] = []

    @classmethod
    async def from_test_config(
        cls, test_config: TestConfig, project_compiler: ProjectCompiler
    ):
        return cls(
            cheatable_starknet_facade=await CheatableStarknetFacade.create(),
            stopwatch=Stopwatch(),
            output_recorder=OutputRecorder(),
            context=TestContext(),
            config=test_config,
            project_compiler=project_compiler,
        )

    def fork(self) -> Self:
        return dataclasses.replace(
            self,
            context=deepcopy(self.context),
            config=deepcopy(self.config),
            output_recorder=self.output_recorder.fork(),
            stopwatch=self.stopwatch.fork(),
            cheatable_starknet_facade=self.cheatable_starknet_facade.fork(),
            event_expectations=self._event_expectations.copy(),
        )

    def add_events_expectation(self, events_expectation: list[Event]):
        self._event_expectations.append(events_expectation)

    def get_events_expectations(self) -> list[EventsExpectation]:
        return self._event_expectations
